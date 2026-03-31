"""FastAPI application factory and minimal runtime routes for CogMem."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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


class RetainItem(BaseModel):
    """Single memory item accepted by retain endpoint."""

    content: str


class RetainRequest(BaseModel):
    """Retain request payload for smoke-level API contract."""

    items: list[RetainItem]


class RetainResponse(BaseModel):
    """Retain response payload."""

    success: bool
    count: int


class RecallRequest(BaseModel):
    """Recall request payload for smoke-level API contract."""

    query: str


class RecallResult(BaseModel):
    """Recall result payload entry."""

    text: str


class RecallResponse(BaseModel):
    """Recall response payload."""

    results: list[RecallResult]


def _tokenize(text: str) -> set[str]:
    """Tokenize text with a lightweight alnum-only split for smoke recall."""
    lowered = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    return {token for token in lowered.split() if token}


def _rank_smoke_results(query: str, memories: list[str], limit: int = 10) -> list[str]:
    """Rank in-memory retained memories using simple lexical overlap scoring."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return memories[:limit]

    scored: list[tuple[int, str]] = []
    for memory in memories:
        overlap = len(query_tokens.intersection(_tokenize(memory)))
        if overlap > 0:
            scored.append((overlap, memory))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [memory for _, memory in scored[:limit]]


def create_app(
    memory: MemoryEngine,
    initialize_memory: bool = True,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.memory = memory
        app.state.smoke_banks = {}
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

    # Keep memory available even when lifespan does not fire (mounted app scenarios).
    app.state.memory = memory
    app.state.smoke_banks = {}

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
        summary="Retain memories (smoke baseline)",
        description="Stores memories in an in-process buffer for Docker smoke testing.",
        tags=["Memory"],
    )
    async def retain_memories(bank_id: str, payload: RetainRequest) -> RetainResponse:
        if bank_id not in app.state.smoke_banks:
            app.state.smoke_banks[bank_id] = []

        contents = [item.content.strip() for item in payload.items if item.content.strip()]
        app.state.smoke_banks[bank_id].extend(contents)
        return RetainResponse(success=True, count=len(contents))

    @app.post(
        "/v1/default/banks/{bank_id}/memories/recall",
        response_model=RecallResponse,
        summary="Recall memories (smoke baseline)",
        description="Retrieves memories from in-process buffer for Docker smoke testing.",
        tags=["Memory"],
    )
    async def recall_memories(bank_id: str, payload: RecallRequest) -> RecallResponse:
        memories: list[str] = app.state.smoke_banks.get(bank_id, [])
        ranked = _rank_smoke_results(payload.query, memories)
        return RecallResponse(results=[RecallResult(text=item) for item in ranked])

    return app
