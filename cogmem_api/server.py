"""ASGI server module for CogMem API."""

from __future__ import annotations

import logging

from cogmem_api import MemoryEngine
from cogmem_api.api import create_app
from cogmem_api.config import _get_raw_config

logging.getLogger(__name__)

_config = _get_raw_config()

_memory = MemoryEngine(
    db_url=_config.database_url,
    database_schema=_config.database_schema,
    pool_min_size=_config.db_pool_min_size,
    pool_max_size=_config.db_pool_max_size,
)

app = create_app(
    memory=_memory,
    http_api_enabled=True,
    initialize_memory=True,
)


if __name__ == "__main__":
    from cogmem_api.main import main

    main()
