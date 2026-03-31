#!/bin/bash
set -euo pipefail

API_COMMAND="${COGMEM_API_COMMAND:-cogmem-api}"
API_HEALTH_URL="${COGMEM_API_HEALTH_URL:-http://localhost:${COGMEM_API_PORT:-8888}/health}"
API_STARTUP_WAIT_SECONDS="${COGMEM_API_STARTUP_WAIT_SECONDS:-120}"

if [ "${COGMEM_WAIT_FOR_DEPS:-false}" = "true" ]; then
    if [ -n "${COGMEM_API_DATABASE_URL:-}" ] && [[ "${COGMEM_API_DATABASE_URL}" != pg0* ]]; then
        echo "Waiting for PostgreSQL endpoint from COGMEM_API_DATABASE_URL..."
        python - <<'PY'
import os
import socket
import time
from urllib.parse import urlparse

url = os.environ.get("COGMEM_API_DATABASE_URL", "")
parsed = urlparse(url)
host = parsed.hostname
port = parsed.port or 5432
max_wait = int(os.environ.get("COGMEM_DEP_WAIT_SECONDS", "120"))
start = time.time()

if not host:
    raise SystemExit("COGMEM_API_DATABASE_URL is set but host is missing")

while True:
    sock = socket.socket()
    sock.settimeout(2)
    try:
        sock.connect((host, port))
        sock.close()
        break
    except OSError:
        sock.close()
        if time.time() - start > max_wait:
            raise SystemExit(f"Timed out waiting for {host}:{port}")
        time.sleep(2)
PY
    fi
fi

${API_COMMAND} &
API_PID=$!

cleanup() {
    if kill -0 "$API_PID" 2>/dev/null; then
        kill "$API_PID"
        wait "$API_PID" || true
    fi
}

trap cleanup INT TERM

api_ready=false
for ((i=1; i<=API_STARTUP_WAIT_SECONDS; i++)); do
    if ! kill -0 "$API_PID" 2>/dev/null; then
        wait "$API_PID"
        exit $?
    fi

    if curl -sf "$API_HEALTH_URL" >/dev/null 2>&1; then
        api_ready=true
        break
    fi

    sleep 1
done

if [ "$api_ready" != "true" ]; then
    echo "API did not become healthy within ${API_STARTUP_WAIT_SECONDS}s"
    exit 1
fi

echo "CogMem API is running at http://0.0.0.0:${COGMEM_API_PORT:-8888}"

wait "$API_PID"
