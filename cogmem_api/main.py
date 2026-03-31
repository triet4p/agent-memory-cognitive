"""Command-line interface for CogMem API."""

from __future__ import annotations

import argparse
import os

import uvicorn

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8888
DEFAULT_LOG_LEVEL = "info"
DEFAULT_WORKERS = 1


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for cogmem-api runtime."""
    parser = argparse.ArgumentParser(
        prog="cogmem-api",
        description="CogMem API Server",
    )

    parser.add_argument(
        "--host",
        default=os.getenv("COGMEM_API_HOST", DEFAULT_HOST),
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("COGMEM_API_PORT", str(DEFAULT_PORT))),
        help="Port to bind to",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("COGMEM_API_LOG_LEVEL", DEFAULT_LOG_LEVEL),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level",
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("COGMEM_API_WORKERS", str(DEFAULT_WORKERS))),
        help="Number of worker processes",
    )
    parser.add_argument("--access-log", action="store_true", help="Enable access log")
    parser.add_argument("--no-access-log", dest="access_log", action="store_false", help="Disable access log")
    parser.set_defaults(access_log=False)
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
    )


if __name__ == "__main__":
    main()
