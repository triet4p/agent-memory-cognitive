"""ASGI server module for CogMem API."""

from __future__ import annotations

import logging
import os

from cogmem_api import MemoryEngine
from cogmem_api.api import create_app

logging.getLogger(__name__)

_memory = MemoryEngine(
    db_url=os.getenv("COGMEM_API_DATABASE_URL"),
    database_schema=os.getenv("COGMEM_API_DATABASE_SCHEMA"),
)

app = create_app(
    memory=_memory,
    http_api_enabled=True,
    initialize_memory=True,
)


if __name__ == "__main__":
    from cogmem_api.main import main

    main()
