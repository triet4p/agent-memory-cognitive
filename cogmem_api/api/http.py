"""FastAPI application factory and runtime routes for CogMem."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from cogmem_api import MemoryEngine, __version__
from cogmem_api.engine import eval_helpers


class HealthResponse(BaseModel):
    """Health response payload for readiness and liveness probes."""

    status: str
    initialized: bool
    database: dict[str, Any]
    reason: str | None = None


class VersionResponse(BaseModel):
    """Version metadata for diagnostics."""

    version: str
    service: str


class EntityInput(BaseModel):
    """Entity attached to a retained memory item."""

    text: str
    type: str | None = None


class RetainItem(BaseModel):
    """Single retain item accepted by retain endpoint."""

    content: str
    timestamp: datetime | str | None = None
    context: str | None = None
    metadata: dict[str, str] | None = None
    document_id: str | None = None
    entities: list[EntityInput] | None = None
    tags: list[str] | None = None


class RetainRequest(BaseModel):
    """Retain request payload."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[RetainItem]
    async_: bool = Field(default=False, alias="async")


class RetainResponse(BaseModel):
    """Retain response payload."""

    success: bool
    bank_id: str
    items_count: int
    unit_ids: list[list[str]]


class RecallRequest(BaseModel):
    """Recall request payload."""

    query: str
    types: list[str] | None = None
    budget: Literal["low", "mid", "high"] = "mid"
    max_tokens: int = 4096
    top_k: int | None = None
    snippet_budget: int | None = None
    trace: bool = False
    query_timestamp: str | None = None
    adaptive_router: bool = True
    graph_retriever: str | None = None


class RecallResult(BaseModel):
    """Recall result payload entry."""

    id: str
    text: str
    type: str
    score: float = 0.0
    raw_snippet: str | None = None
    document_id: str | None = None


class RecallResponse(BaseModel):
    """Recall response payload."""

    results: list[RecallResult]
    trace: dict[str, Any] | None = None


class GenerateRequest(BaseModel):
    """Request payload for generation endpoint."""

    query: str
    evidence: list[dict]
    max_tokens: int = 2048


class GenerateResponse(BaseModel):
    """Response payload for generation endpoint."""

    answer: str


class JudgeRequest(BaseModel):
    """Request payload for judge endpoint."""

    question: str
    gold_answer: str
    predicted_answer: str
    category: str | None = None


class JudgeResponse(BaseModel):
    """Response payload for judge endpoint."""

    correct: bool
    score: float
    reason: str
    raw: str


class BankInfo(BaseModel):
    """Summary info for a single bank."""

    bank_id: str
    unit_count: int


class DeleteBankResponse(BaseModel):
    """Response for bank deletion."""

    bank_id: str
    deleted: bool
    units_deleted: int


def _parse_query_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid query_timestamp: {exc}") from exc


def _build_retain_payload(item: RetainItem) -> dict[str, Any] | None:
    content = item.content.strip()
    if not content:
        return None

    payload: dict[str, Any] = {"content": content}
    if item.context:
        payload["context"] = item.context
    if item.timestamp is not None:
        payload["event_date"] = item.timestamp
    if item.metadata:
        payload["metadata"] = item.metadata
    if item.document_id:
        payload["document_id"] = item.document_id
    if item.entities:
        payload["entities"] = [
            {"text": entity.text, "type": entity.type or "CONCEPT"}
            for entity in item.entities
            if entity.text.strip()
        ]
    if item.tags:
        payload["tags"] = [tag for tag in item.tags if tag.strip()]
    return payload


def create_app(
    memory: MemoryEngine,
    initialize_memory: bool = True,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.memory = memory
        if initialize_memory:
            await memory.initialize()
        try:
            yield
        finally:
            await memory.close()

    app = FastAPI(
        title="CogMem HTTP API",
        version=__version__,
        description="HTTP API for CogMem",
        lifespan=lifespan,
    )

    app.state.memory = memory

    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Health check endpoint",
        description="Checks the health of the API and database connectivity.",
        tags=["Monitoring"],
    )
    async def health_endpoint() -> JSONResponse:
        health = await app.state.memory.health_check()
        status_code = 200 if health.get("status") == "healthy" else 503
        return JSONResponse(content=health, status_code=status_code)

    @app.get(
        "/version",
        response_model=VersionResponse,
        summary="Version endpoint",
        description="Returns service and package version.",
        tags=["Monitoring"],
    )
    async def version_endpoint() -> VersionResponse:
        return VersionResponse(version=__version__, service="cogmem-api")

    @app.get(
        "/v1/banks",
        response_model=list[BankInfo],
        summary="List all banks",
        description="Returns all memory banks with their unit counts.",
        operation_id="list_banks",
        tags=["Memory"],
    )
    async def list_banks() -> list[BankInfo]:
        try:
            banks = await app.state.memory.list_banks()
            return [BankInfo(**b) for b in banks]
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.delete(
        "/v1/default/banks/{bank_id}",
        response_model=DeleteBankResponse,
        summary="Delete a bank",
        description="Deletes a bank and all its memory units, documents, and edges.",
        operation_id="delete_bank",
        tags=["Memory"],
    )
    async def delete_bank(bank_id: str) -> DeleteBankResponse:
        try:
            result = await app.state.memory.delete_bank(bank_id)
            return DeleteBankResponse(**result)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post(
        "/v1/default/banks/{bank_id}/memories",
        response_model=RetainResponse,
        summary="Retain memories",
        description="Stores memory items using CogMem retain_batch runtime path.",
        operation_id="retain_memories",
        tags=["Memory"],
    )
    async def retain_memories(bank_id: str, payload: RetainRequest) -> RetainResponse:
        contents = [candidate for candidate in (_build_retain_payload(item) for item in payload.items) if candidate]
        if not contents:
            return RetainResponse(success=True, bank_id=bank_id, items_count=0, unit_ids=[])

        if payload.async_:
            raise HTTPException(status_code=400, detail="Async retain is not available in CogMem runtime yet.")

        try:
            unit_ids = await app.state.memory.retain_batch_async(bank_id=bank_id, contents=contents)
            return RetainResponse(success=True, bank_id=bank_id, items_count=len(contents), unit_ids=unit_ids)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post(
        "/v1/default/banks/{bank_id}/memories/recall",
        response_model=RecallResponse,
        summary="Recall memories",
        description="Recalls memories through CogMem recall stack.",
        operation_id="recall_memories",
        tags=["Memory"],
    )
    async def recall_memories(bank_id: str, payload: RecallRequest) -> RecallResponse:
        question_date = _parse_query_timestamp(payload.query_timestamp)

        try:
            recall_result = await app.state.memory.recall_async(
                bank_id=bank_id,
                query=payload.query,
                budget=payload.budget,
                max_tokens=payload.max_tokens,
                top_k=payload.top_k,
                snippet_budget=payload.snippet_budget,
                enable_trace=payload.trace,
                fact_types=payload.types,
                question_date=question_date,
                adaptive_router=payload.adaptive_router,
                graph_retriever_override=payload.graph_retriever,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        results = [
            RecallResult(
                id=str(item.get("id") or ""),
                text=str(item.get("text") or ""),
                type=str(item.get("fact_type") or "world"),
                score=float(item.get("score") or 0.0),
                raw_snippet=item.get("raw_snippet"),
                document_id=item.get("document_id"),
            )
            for item in recall_result.get("results", [])
            if item.get("id") and item.get("text")
        ]
        return RecallResponse(results=results, trace=recall_result.get("trace"))

    @app.post(
        "/v1/default/banks/{bank_id}/memories/generate",
        response_model=GenerateResponse,
        summary="Generate answer from recall evidence",
        description="Uses the retain LLM to generate an answer grounded in recall evidence.",
        operation_id="generate_answer",
        tags=["Memory"],
    )
    async def generate_answer(bank_id: str, payload: GenerateRequest) -> GenerateResponse:
        if not app.state.memory._runtime_config.llm_base_url:
            raise HTTPException(status_code=503, detail="Retain LLM not configured")

        llm_config = app.state.memory._build_retain_llm_config()
        if llm_config is None:
            raise HTTPException(status_code=503, detail="Retain LLM not available")

        prompt = eval_helpers.build_generation_prompt(payload.query, payload.evidence)
        messages = [{"role": "user", "content": prompt}]

        try:
            answer = await llm_config.call(
                messages=messages,
                temperature=0.1,
                max_completion_tokens=payload.max_tokens,
            )
            return GenerateResponse(answer=str(answer or ""))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post(
        "/v1/default/judge",
        response_model=JudgeResponse,
        summary="Judge predicted answer against gold answer",
        description="Uses a dedicated judge LLM to evaluate prediction quality.",
        operation_id="judge_answer",
        tags=["Evaluation"],
    )
    async def judge_answer(payload: JudgeRequest) -> JudgeResponse:
        if not app.state.memory._runtime_config.judge_llm_base_url:
            raise HTTPException(status_code=503, detail="Judge LLM not configured")

        llm_config = app.state.memory._build_judge_llm_config()
        if llm_config is None:
            raise HTTPException(status_code=503, detail="Judge LLM not available")

        system_prompt = eval_helpers.build_judge_system_prompt(payload.category)
        user_prompt = (
            f"Question: {payload.question}\n"
            f"Gold Answer: {payload.gold_answer}\n"
            f"Predicted Answer: {payload.predicted_answer}\n"
            "Return JSON only."
        )

        try:
            raw = await llm_config.call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_completion_tokens=40000,
            )
            parsed = eval_helpers.parse_judge_response(str(raw or "{}"))
            return JudgeResponse(
                correct=parsed.get("correct", False),
                score=float(parsed.get("score", 0.0)),
                reason=parsed.get("reason", ""),
                raw=parsed.get("raw", ""),
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app
