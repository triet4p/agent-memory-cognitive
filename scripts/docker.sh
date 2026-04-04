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
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COGMEM_DOCKER_COMPOSE_FILE:-${REPO_ROOT}/docker/docker-compose/external-pg/docker-compose.yaml}"
COMPOSE_ENV_FILE="${COGMEM_DOCKER_ENV_FILE:-${REPO_ROOT}/.env}"
DOCKER_INCLUDE_LOCAL_MODELS="${COGMEM_DOCKER_INCLUDE_LOCAL_MODELS:-true}"
DOCKER_PRELOAD_ML_MODELS="${COGMEM_DOCKER_PRELOAD_ML_MODELS:-false}"

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
        docker build \
            -f "${REPO_ROOT}/docker/standalone/Dockerfile" \
            --build-arg "INCLUDE_LOCAL_MODELS=${DOCKER_INCLUDE_LOCAL_MODELS}" \
            --build-arg "PRELOAD_ML_MODELS=${DOCKER_PRELOAD_ML_MODELS}" \
            -t "${IMAGE}" \
            "${REPO_ROOT}"

        mkdir -p "${PG0_VOLUME_DIR}"
        DOCKER_ARGS+=(
            -e "COGMEM_API_DATABASE_URL=pg0"
            -v "${PG0_VOLUME_DIR}:/home/cogmem/.pg0"
        )

        echo "Starting CogMem container"
        echo "  Mode: ${MODE}"
        echo "  Image: ${IMAGE}"
        echo "  Port: ${PORT}"
        echo "  LLM provider/model: ${LLM_PROVIDER}/${LLM_MODEL}"
        if [ -n "${LLM_BASE_URL}" ]; then
            echo "  LLM base URL: ${LLM_BASE_URL}"
        fi

        exec docker run "${DOCKER_ARGS[@]}" "${IMAGE}"
        ;;
    external)
        if [ -n "${EXTERNAL_DATABASE_URL}" ]; then
            docker build \
                -f "${REPO_ROOT}/docker/standalone/Dockerfile" \
                --build-arg "INCLUDE_LOCAL_MODELS=${DOCKER_INCLUDE_LOCAL_MODELS}" \
                --build-arg "PRELOAD_ML_MODELS=${DOCKER_PRELOAD_ML_MODELS}" \
                -t "${IMAGE}" \
                "${REPO_ROOT}"

            DOCKER_ARGS+=( -e "COGMEM_API_DATABASE_URL=${EXTERNAL_DATABASE_URL}" )

            echo "Starting CogMem container"
            echo "  Mode: ${MODE} (legacy external URL)"
            echo "  Image: ${IMAGE}"
            echo "  Port: ${PORT}"
            echo "  LLM provider/model: ${LLM_PROVIDER}/${LLM_MODEL}"
            if [ -n "${LLM_BASE_URL}" ]; then
                echo "  LLM base URL: ${LLM_BASE_URL}"
            fi

            exec docker run "${DOCKER_ARGS[@]}" "${IMAGE}"
        fi

        if [ ! -f "${COMPOSE_ENV_FILE}" ]; then
            echo "Error: ${COMPOSE_ENV_FILE} not found. Copy .env.example to .env first."
            exit 2
        fi

        echo "Starting CogMem stack with docker compose"
        echo "  Mode: ${MODE} (compose unified app+db)"
        echo "  Compose file: ${COMPOSE_FILE}"
        echo "  Env file: ${COMPOSE_ENV_FILE}"

        exec docker compose \
            --env-file "${COMPOSE_ENV_FILE}" \
            -f "${COMPOSE_FILE}" \
            up --build
        ;;
    *)
        echo "Error: unknown mode '${MODE}'. Use embedded or external."
        exit 2
        ;;
esac
