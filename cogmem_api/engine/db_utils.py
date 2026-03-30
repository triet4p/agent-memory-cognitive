"""Database utility functions for connection management with retry logic."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

import asyncpg

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 0.5
DEFAULT_MAX_DELAY = 5.0

RETRYABLE_EXCEPTIONS = (
    asyncpg.exceptions.InterfaceError,
    asyncpg.exceptions.ConnectionDoesNotExistError,
    asyncpg.exceptions.TooManyConnectionsError,
    asyncpg.exceptions.DeadlockDetectedError,
    OSError,
    ConnectionError,
    asyncio.TimeoutError,
)


async def retry_with_backoff(
    func,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    retryable_exceptions: tuple[type[BaseException], ...] = RETRYABLE_EXCEPTIONS,
):
    """Execute an async function with exponential backoff retry."""
    last_exception: BaseException | None = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as exc:
            last_exception = exc
            if attempt < max_retries:
                delay = min(base_delay * (2**attempt), max_delay)
                logger.warning(
                    "Database operation failed (attempt %s/%s): %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries + 1,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error("Database operation failed after %s attempts: %s", max_retries + 1, exc)

    if last_exception is not None:
        raise last_exception
    raise RuntimeError("Retry logic finished without result or exception")


@asynccontextmanager
async def acquire_with_retry(pool: asyncpg.Pool, max_retries: int = DEFAULT_MAX_RETRIES):
    """Acquire a pooled connection with retry and release it safely."""

    async def acquire():
        return await pool.acquire()

    conn = await retry_with_backoff(acquire, max_retries=max_retries)
    try:
        yield conn
    finally:
        await pool.release(conn)
