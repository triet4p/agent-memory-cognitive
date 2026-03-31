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

    # Keep memory available even when lifespan does not fire (mounted app scenarios).
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

    return app
