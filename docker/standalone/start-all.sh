#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Startup config dump — print every important variable so there is no
# ambiguity about what value is actually in effect at runtime.
# Sensitive values (tokens, passwords) are masked: shown as SET/UNSET only.
# ---------------------------------------------------------------------------
_mask() {
    # Print SET or UNSET for a variable name
    local val="${!1:-}"
    [ -n "$val" ] && echo "SET" || echo "UNSET"
}
_db_url_safe() {
    # Strip password from DATABASE_URL for logging
    echo "${COGMEM_API_DATABASE_URL:-}" | sed 's|://[^:]*:[^@]*@|://***:***@|'
}

echo "=========================================="
echo " CogMem startup config"
echo "=========================================="
echo " API"
echo "   COGMEM_API_COMMAND     = ${COGMEM_API_COMMAND:-cogmem-api}"
echo "   COGMEM_API_HOST        = ${COGMEM_API_HOST:-0.0.0.0}"
echo "   COGMEM_API_PORT        = ${COGMEM_API_PORT:-8888}"
echo "   COGMEM_API_LOG_LEVEL   = ${COGMEM_API_LOG_LEVEL:-info}"
echo " Database"
echo "   COGMEM_API_DATABASE_URL= $(_db_url_safe)"
echo "   COGMEM_WAIT_FOR_DEPS   = ${COGMEM_WAIT_FOR_DEPS:-false}"
echo " LLM (retain)"
echo "   LLM_BASE_URL           = ${COGMEM_API_LLM_BASE_URL:-UNSET}"
echo "   LLM_MODEL              = ${COGMEM_API_LLM_MODEL:-ministral3-3b}"
echo "   EXTRACTION_MODE        = ${COGMEM_API_RETAIN_EXTRACTION_MODE:-concise}"
echo " LLM (generate)"
echo "   GENERATE_LLM_BASE_URL  = ${COGMEM_API_GENERATE_LLM_BASE_URL:-UNSET}"
echo "   GENERATE_LLM_MODEL     = ${COGMEM_API_GENERATE_LLM_MODEL:-UNSET}"
echo " ML models"
echo "   PRELOAD_ML_MODELS      = ${PRELOAD_ML_MODELS:-false}"
echo "   HF_TOKEN               = $(_mask HF_TOKEN)"
echo "=========================================="

# Pre-download ML models at startup so HF_TOKEN from runtime environment is available.
# Set PRELOAD_ML_MODELS=true to enable; safe to skip if models are already cached.
if [ "${PRELOAD_ML_MODELS:-false}" = "true" ]; then
    echo "Preloading ML models from HuggingFace..."
    python -c "
from sentence_transformers import SentenceTransformer, CrossEncoder
SentenceTransformer('BAAI/bge-small-en-v1.5')
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
" || echo "Warning: ML model preload failed — models will be downloaded on first use."
fi

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
