"""Minimal memory engine bootstrap for CogMem schema operations."""

from __future__ import annotations

import contextvars
import re
from contextlib import contextmanager
from typing import Any

import asyncpg

from cogmem_api import config
from .db_utils import acquire_with_retry

_current_schema: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_schema", default=None)

_PROTECTED_TABLES = frozenset(
    [
        "memory_units",
        "memory_links",
        "unit_entities",
        "entities",
        "entity_cooccurrences",
        "banks",
        "documents",
        "chunks",
        "async_operations",
        "file_storage",
    ]
)

_VALIDATE_SQL_SCHEMAS = True


class UnqualifiedTableError(Exception):
    """Raised when SQL contains unqualified references to protected tables."""



def get_current_schema() -> str:
    """Get current schema from task context, falling back to default config."""
    schema = _current_schema.get()
    return schema if schema is not None else config.DATABASE_SCHEMA


@contextmanager
def set_schema_context(schema: str):
    """Temporarily override the active schema in the current context."""
    token = _current_schema.set(schema)
    try:
        yield
    finally:
        _current_schema.reset(token)



def fq_table(table_name: str) -> str:
    """Return fully-qualified table name using active schema context."""
    return f"{get_current_schema()}.{table_name}"



def validate_sql_schema(sql: str) -> None:
    """Ensure protected tables are always referenced with explicit schema prefix."""
    if not _VALIDATE_SQL_SCHEMAS:
        return

    sql_upper = sql.upper()
    for table in _PROTECTED_TABLES:
        table_upper = table.upper()
        patterns = [
            rf"FROM\s+{table_upper}(?:\s|$|,|\)|;)",
            rf"JOIN\s+{table_upper}(?:\s|$|,|\)|;)",
            rf"INTO\s+{table_upper}(?:\s|$|\()",
            rf"UPDATE\s+{table_upper}(?:\s|$)",
            rf"DELETE\s+FROM\s+{table_upper}(?:\s|$|;)",
        ]

        for pattern in patterns:
            match = re.search(pattern, sql_upper)
            if not match:
                continue

            start = match.start()
            table_pos = sql_upper.find(table_upper, start)
            if table_pos > 0:
                prefix = sql[:table_pos].rstrip()
                if not prefix.endswith("."):
                    raise UnqualifiedTableError(
                        f"Unqualified table reference '{table}'. Use fq_table('{table}') for schema safety."
                    )


class MemoryEngine:
    """Minimal CogMem engine scaffold for schema-safe DB bootstrap."""

    def __init__(
        self,
        db_url: str | None = None,
        database_schema: str | None = None,
        pool_min_size: int | None = None,
        pool_max_size: int | None = None,
    ):
        self.db_url = db_url
        self.database_schema = database_schema or config.DATABASE_SCHEMA
        self._pool_min_size = pool_min_size if pool_min_size is not None else config.DB_POOL_MIN_SIZE
        self._pool_max_size = pool_max_size if pool_max_size is not None else config.DB_POOL_MAX_SIZE
        self._pool: asyncpg.Pool | None = None
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def pool(self) -> asyncpg.Pool | None:
        return self._pool

    async def initialize(self) -> None:
        """Initialize DB connection pool if db_url is provided."""
        if self._initialized:
            return

        _current_schema.set(self.database_schema)

        if not self.db_url:
            self._initialized = True
            return

        self._pool = await asyncpg.create_pool(
            self.db_url,
            min_size=self._pool_min_size,
            max_size=self._pool_max_size,
        )
        self._initialized = True

    async def close(self) -> None:
        """Close connection pool if initialized."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
        self._initialized = False

    async def execute(self, sql: str, *args: Any) -> str:
        """Execute SQL after schema safety validation."""
        validate_sql_schema(sql)
        if self._pool is None:
            raise RuntimeError("MemoryEngine is not connected. Call initialize() with db_url first.")

        async with acquire_with_retry(self._pool) as conn:
            return await conn.execute(sql, *args)
