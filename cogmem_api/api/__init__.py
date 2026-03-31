"""Unified API module for CogMem."""

from fastapi import FastAPI

from cogmem_api import MemoryEngine
from cogmem_api.api.http import create_app as create_http_app


def create_app(
    memory: MemoryEngine,
    http_api_enabled: bool = True,
    initialize_memory: bool = True,
) -> FastAPI:
    """Create and configure the CogMem API application."""
    if http_api_enabled:
        return create_http_app(memory=memory, initialize_memory=initialize_memory)

    return FastAPI(title="CogMem API")


__all__ = ["create_app"]
