"""Command-line interface for CogMem API."""

from __future__ import annotations

import argparse

import uvicorn

from cogmem_api.config import _get_raw_config

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8888
DEFAULT_LOG_LEVEL = "info"
DEFAULT_WORKERS = 1


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for cogmem-api runtime."""
    config = _get_raw_config()

    parser = argparse.ArgumentParser(
        prog="cogmem-api",
        description="CogMem API Server",
    )

    parser.add_argument(
        "--host",
        default=config.host,
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.port,
        help="Port to bind to",
    )
    parser.add_argument(
        "--log-level",
        default=config.log_level,
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level",
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument(
        "--workers",
        type=int,
        default=config.workers,
        help="Number of worker processes",
    )
    parser.add_argument("--access-log", action="store_true", help="Enable access log")
    parser.add_argument("--no-access-log", dest="access_log", action="store_false", help="Disable access log")
    parser.set_defaults(access_log=False)
    parser.add_argument(
        "--timeout-keep-alive",
        type=int,
        default=7200,
        help="Seconds to keep idle HTTP connections alive (default: 7200)",
    )
    parser.add_argument("--proxy-headers", action="store_true", help="Enable proxy headers")
    parser.add_argument("--forwarded-allow-ips", default=None, help="Trusted proxy IPs")

    return parser


def main() -> None:
    """Run the CogMem API server."""
    args = build_parser().parse_args()

    workers = 1 if args.reload else max(1, args.workers)

    uvicorn.run(
        "cogmem_api.server:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
        workers=workers,
        access_log=args.access_log,
        proxy_headers=args.proxy_headers,
        forwarded_allow_ips=args.forwarded_allow_ips,
        timeout_keep_alive=args.timeout_keep_alive,
    )


if __name__ == "__main__":
    main()
