"""FastAPI application factory and runtime routes for CogMem."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from cogmem_api import MemoryEngine, __version__


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

    return app
