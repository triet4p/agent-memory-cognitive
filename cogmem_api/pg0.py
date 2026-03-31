from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pg0 import Pg0

logger = logging.getLogger(__name__)

DEFAULT_USERNAME = "cogmem"
DEFAULT_PASSWORD = "cogmem"
DEFAULT_DATABASE = "cogmem"
DEFAULT_INSTANCE_NAME = "cogmem"


class EmbeddedPostgres:
    """Manage an embedded PostgreSQL instance backed by pg0-embedded."""

    def __init__(
        self,
        port: int | None = None,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        database: str = DEFAULT_DATABASE,
        name: str = DEFAULT_INSTANCE_NAME,
        **kwargs,
    ):
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.name = name
        self._pg0: Pg0 | None = None

    def _get_pg0(self) -> Pg0:
        if self._pg0 is None:
            try:
                from pg0 import Pg0
            except ImportError as exc:
                raise ImportError(
                    "pg0-embedded is required for embedded PostgreSQL. "
                    "Install it with: uv sync --extra embedded-db"
                ) from exc
            kwargs = {
                "name": self.name,
                "username": self.username,
                "password": self.password,
                "database": self.database,
            }
            if self.port is not None:
                kwargs["port"] = self.port
            self._pg0 = Pg0(**kwargs)
        return self._pg0

    async def start(self, max_retries: int = 5, retry_delay: float = 4.0) -> str:
        """Start embedded Postgres with retry and backoff."""
        port_info = f"port={self.port}" if self.port else "port=auto"
        logger.info(f"Starting embedded PostgreSQL (name={self.name}, {port_info})")

        pg0 = self._get_pg0()
        last_error: str | None = None

        for attempt in range(1, max_retries + 1):
            try:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(None, pg0.start)
                return info.uri
            except Exception as exc:  # pragma: no cover - runtime retry guard
                last_error = str(exc)
                if attempt < max_retries:
                    delay = retry_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        raise RuntimeError(
            f"Failed to start embedded PostgreSQL after {max_retries} attempts. Last error: {last_error}"
        )

    async def stop(self) -> None:
        """Stop embedded PostgreSQL if running."""
        pg0 = self._get_pg0()
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, pg0.stop)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            if "not running" in str(exc).lower():
                return
            raise RuntimeError(f"Failed to stop PostgreSQL: {exc}") from exc

    async def get_uri(self) -> str:
        """Return active PostgreSQL URI."""
        pg0 = self._get_pg0()
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, pg0.info)
        return info.uri

    async def is_running(self) -> bool:
        """Check whether the embedded PostgreSQL instance is running."""
        try:
            pg0 = self._get_pg0()
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, pg0.info)
            return info is not None and info.running
        except Exception:
            return False

    async def ensure_running(self) -> str:
        """Return DB URI and start service if needed."""
        if await self.is_running():
            return await self.get_uri()
        return await self.start()


def parse_pg0_url(db_url: str) -> tuple[bool, str | None, int | None]:
    """Parse pg0 URLs and return mode tuple (is_pg0, instance_name, port)."""
    if db_url == "pg0":
        return True, DEFAULT_INSTANCE_NAME, None

    if db_url.startswith("pg0://"):
        url_part = db_url[6:]
        if ":" in url_part:
            instance_name, port_str = url_part.rsplit(":", 1)
            return True, instance_name or DEFAULT_INSTANCE_NAME, int(port_str)
        return True, url_part or DEFAULT_INSTANCE_NAME, None

    return False, None, None
