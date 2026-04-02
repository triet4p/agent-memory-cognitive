#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/docker.sh [embedded|external]
#
# Modes:
#   embedded (default): run with pg0 inside container
#   external          : run with external PostgreSQL URL

MODE="${1:-embedded}"
IMAGE="${COGMEM_DOCKER_IMAGE:-cogmem:local}"
PORT="${COGMEM_API_PORT:-8888}"
LOG_LEVEL="${COGMEM_API_LOG_LEVEL:-info}"
SCHEMA="${COGMEM_API_DATABASE_SCHEMA:-public}"
PG0_VOLUME_DIR="${COGMEM_PG0_VOLUME_DIR:-${HOME}/.cogmem-docker}"
EXTERNAL_DATABASE_URL="${COGMEM_EXTERNAL_DATABASE_URL:-}"

# Backfill B5: minimal LLM + retain runtime contract.
LLM_PROVIDER="${COGMEM_API_LLM_PROVIDER:-openai}"
LLM_BASE_URL="${COGMEM_API_LLM_BASE_URL:-}"
LLM_API_KEY="${COGMEM_API_LLM_API_KEY:-dummy}"
LLM_MODEL="${COGMEM_API_LLM_MODEL:-gpt-4o-mini}"
LLM_TIMEOUT="${COGMEM_API_LLM_TIMEOUT:-120}"
RETAIN_LLM_TIMEOUT="${COGMEM_API_RETAIN_LLM_TIMEOUT:-120}"
REFLECT_LLM_TIMEOUT="${COGMEM_API_REFLECT_LLM_TIMEOUT:-120}"
RETAIN_MAX_COMPLETION_TOKENS="${COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS:-64000}"
RETAIN_EXTRACTION_MODE="${COGMEM_API_RETAIN_EXTRACTION_MODE:-concise}"

DOCKER_ARGS=(
    --rm -it --pull always
    -p "${PORT}:8888"
    -e "COGMEM_API_HOST=0.0.0.0"
    -e "COGMEM_API_PORT=8888"
    -e "COGMEM_API_LOG_LEVEL=${LOG_LEVEL}"
    -e "COGMEM_API_DATABASE_SCHEMA=${SCHEMA}"
    -e "COGMEM_API_LLM_PROVIDER=${LLM_PROVIDER}"
    -e "COGMEM_API_LLM_API_KEY=${LLM_API_KEY}"
    -e "COGMEM_API_LLM_MODEL=${LLM_MODEL}"
    -e "COGMEM_API_LLM_TIMEOUT=${LLM_TIMEOUT}"
    -e "COGMEM_API_RETAIN_LLM_TIMEOUT=${RETAIN_LLM_TIMEOUT}"
    -e "COGMEM_API_REFLECT_LLM_TIMEOUT=${REFLECT_LLM_TIMEOUT}"
    -e "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS=${RETAIN_MAX_COMPLETION_TOKENS}"
    -e "COGMEM_API_RETAIN_EXTRACTION_MODE=${RETAIN_EXTRACTION_MODE}"
)

if [ -n "${LLM_BASE_URL}" ]; then
    DOCKER_ARGS+=( -e "COGMEM_API_LLM_BASE_URL=${LLM_BASE_URL}" )
fi

case "${MODE}" in
    embedded)
        mkdir -p "${PG0_VOLUME_DIR}"
        DOCKER_ARGS+=(
            -e "COGMEM_API_DATABASE_URL=pg0"
            -v "${PG0_VOLUME_DIR}:/home/cogmem/.pg0"
        )
        ;;
    external)
        if [ -z "${EXTERNAL_DATABASE_URL}" ]; then
            echo "Error: COGMEM_EXTERNAL_DATABASE_URL is required for external mode."
            exit 2
        fi
        DOCKER_ARGS+=( -e "COGMEM_API_DATABASE_URL=${EXTERNAL_DATABASE_URL}" )
        ;;
    *)
        echo "Error: unknown mode '${MODE}'. Use embedded or external."
        exit 2
        ;;
esac

echo "Starting CogMem container"
echo "  Mode: ${MODE}"
echo "  Image: ${IMAGE}"
echo "  Port: ${PORT}"
echo "  LLM provider/model: ${LLM_PROVIDER}/${LLM_MODEL}"
if [ -n "${LLM_BASE_URL}" ]; then
    echo "  LLM base URL: ${LLM_BASE_URL}"
fi

exec docker run "${DOCKER_ARGS[@]}" "${IMAGE}"
