#!/bin/bash
#
# CogMem Docker smoke test script.
#
# Usage:
#   ./docker/test-image.sh <image>
#
# Example:
#   ./docker/test-image.sh cogmem:local

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

IMAGE="${1:-}"
TIMEOUT="${SMOKE_TEST_TIMEOUT:-120}"
CONTAINER_NAME="${SMOKE_TEST_CONTAINER_NAME:-cogmem-smoke-test}"
HEALTH_URL="${COGMEM_API_HEALTH_URL:-http://localhost:8888/health}"
SMOKE_BASE_URL="${COGMEM_SMOKE_BASE_URL:-http://localhost:8888}"
SMOKE_DATABASE_URL="${COGMEM_SMOKE_DATABASE_URL:-pg0}"
SMOKE_PG0_VOLUME_DIR="${COGMEM_SMOKE_PG0_VOLUME_DIR:-${HOME}/.cogmem-docker-smoke}"
SMOKE_REQUIRE_NON_DETERMINISTIC="${COGMEM_SMOKE_REQUIRE_NON_DETERMINISTIC:-true}"

# Backfill B5: pass through LLM + retain knobs for real retain runtime.
LLM_PROVIDER="${COGMEM_API_LLM_PROVIDER:-openai}"
LLM_BASE_URL="${COGMEM_API_LLM_BASE_URL:-}"
LLM_API_KEY="${COGMEM_API_LLM_API_KEY:-dummy}"
LLM_MODEL="${COGMEM_API_LLM_MODEL:-gpt-4o-mini}"
LLM_TIMEOUT="${COGMEM_API_LLM_TIMEOUT:-120}"
RETAIN_LLM_TIMEOUT="${COGMEM_API_RETAIN_LLM_TIMEOUT:-120}"
REFLECT_LLM_TIMEOUT="${COGMEM_API_REFLECT_LLM_TIMEOUT:-120}"
RETAIN_MAX_COMPLETION_TOKENS="${COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS:-64000}"
RETAIN_EXTRACTION_MODE="${COGMEM_API_RETAIN_EXTRACTION_MODE:-concise}"
EMBEDDINGS_PROVIDER="${COGMEM_API_EMBEDDINGS_PROVIDER:-local}"
EMBEDDINGS_LOCAL_MODEL="${COGMEM_API_EMBEDDINGS_LOCAL_MODEL:-BAAI/bge-small-en-v1.5}"
EMBEDDINGS_OPENAI_MODEL="${COGMEM_API_EMBEDDINGS_OPENAI_MODEL:-text-embedding-3-small}"
EMBEDDINGS_OPENAI_BASE_URL="${COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL:-}"
EMBEDDINGS_OPENAI_API_KEY="${COGMEM_API_EMBEDDINGS_OPENAI_API_KEY:-}"
RERANKER_PROVIDER="${COGMEM_API_RERANKER_PROVIDER:-rrf}"
RERANKER_LOCAL_MODEL="${COGMEM_API_RERANKER_LOCAL_MODEL:-cross-encoder/ms-marco-MiniLM-L-6-v2}"
RERANKER_TEI_URL="${COGMEM_API_RERANKER_TEI_URL:-}"
RERANKER_TEI_BATCH_SIZE="${COGMEM_API_RERANKER_TEI_BATCH_SIZE:-128}"
RERANKER_MAX_CANDIDATES="${COGMEM_API_RERANKER_MAX_CANDIDATES:-300}"

if [ -z "$IMAGE" ]; then
    echo -e "${RED}Error: image argument is required${NC}"
    echo "Usage: $0 <image>"
    exit 2
fi

cleanup() {
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
}

trap cleanup EXIT

echo -e "${YELLOW}Starting CogMem Docker smoke test${NC}"
echo "  Image: $IMAGE"
echo "  Health URL: $HEALTH_URL"
echo "  Timeout: ${TIMEOUT}s"
echo "  Database mode: ${SMOKE_DATABASE_URL}"
echo "  LLM provider/model: ${LLM_PROVIDER}/${LLM_MODEL}"
echo "  Embeddings provider: ${EMBEDDINGS_PROVIDER}"
if [ -n "$LLM_BASE_URL" ]; then
    echo "  LLM base URL: $LLM_BASE_URL"
fi

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

DOCKER_RUN_ARGS=(
    -d
    --name "$CONTAINER_NAME"
    -p 8888:8888
    -e "COGMEM_API_DATABASE_URL=${SMOKE_DATABASE_URL}"
    -e "COGMEM_API_LLM_PROVIDER=${LLM_PROVIDER}"
    -e "COGMEM_API_LLM_API_KEY=${LLM_API_KEY}"
    -e "COGMEM_API_LLM_MODEL=${LLM_MODEL}"
    -e "COGMEM_API_LLM_TIMEOUT=${LLM_TIMEOUT}"
    -e "COGMEM_API_RETAIN_LLM_TIMEOUT=${RETAIN_LLM_TIMEOUT}"
    -e "COGMEM_API_REFLECT_LLM_TIMEOUT=${REFLECT_LLM_TIMEOUT}"
    -e "COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS=${RETAIN_MAX_COMPLETION_TOKENS}"
    -e "COGMEM_API_RETAIN_EXTRACTION_MODE=${RETAIN_EXTRACTION_MODE}"
    -e "COGMEM_API_EMBEDDINGS_PROVIDER=${EMBEDDINGS_PROVIDER}"
    -e "COGMEM_API_EMBEDDINGS_LOCAL_MODEL=${EMBEDDINGS_LOCAL_MODEL}"
    -e "COGMEM_API_EMBEDDINGS_OPENAI_MODEL=${EMBEDDINGS_OPENAI_MODEL}"
    -e "COGMEM_API_RERANKER_PROVIDER=${RERANKER_PROVIDER}"
    -e "COGMEM_API_RERANKER_LOCAL_MODEL=${RERANKER_LOCAL_MODEL}"
    -e "COGMEM_API_RERANKER_TEI_BATCH_SIZE=${RERANKER_TEI_BATCH_SIZE}"
    -e "COGMEM_API_RERANKER_MAX_CANDIDATES=${RERANKER_MAX_CANDIDATES}"
)

if [ -n "$LLM_BASE_URL" ]; then
    DOCKER_RUN_ARGS+=( -e "COGMEM_API_LLM_BASE_URL=${LLM_BASE_URL}" )
fi

if [ -n "$EMBEDDINGS_OPENAI_BASE_URL" ]; then
    DOCKER_RUN_ARGS+=( -e "COGMEM_API_EMBEDDINGS_OPENAI_BASE_URL=${EMBEDDINGS_OPENAI_BASE_URL}" )
fi

if [ -n "$EMBEDDINGS_OPENAI_API_KEY" ]; then
    DOCKER_RUN_ARGS+=( -e "COGMEM_API_EMBEDDINGS_OPENAI_API_KEY=${EMBEDDINGS_OPENAI_API_KEY}" )
fi

if [ -n "$RERANKER_TEI_URL" ]; then
    DOCKER_RUN_ARGS+=( -e "COGMEM_API_RERANKER_TEI_URL=${RERANKER_TEI_URL}" )
fi

if [[ "$SMOKE_DATABASE_URL" == pg0* ]]; then
    mkdir -p "$SMOKE_PG0_VOLUME_DIR"
    DOCKER_RUN_ARGS+=( -v "${SMOKE_PG0_VOLUME_DIR}:/home/cogmem/.pg0" )
fi

docker run "${DOCKER_RUN_ARGS[@]}" "$IMAGE" >/dev/null

start_time=$(date +%s)
for i in $(seq 1 "$TIMEOUT"); do
    if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${GREEN}Health check passed after ${duration}s${NC}"

        echo "Running retain/recall smoke checks..."
        "$REPO_ROOT/scripts/smoke-test-cogmem.sh" "$SMOKE_BASE_URL"

        if [ "$SMOKE_REQUIRE_NON_DETERMINISTIC" = "true" ] && [ "$EMBEDDINGS_PROVIDER" = "local" ]; then
            if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "Falling back to deterministic embeddings"; then
                echo -e "${RED}FAIL: local embeddings requested but runtime fell back to deterministic embeddings${NC}"
                docker logs "$CONTAINER_NAME" 2>&1 | tail -80 || true
                exit 1
            fi
        fi

        echo ""
        echo "=== Container Logs (last 50 lines) ==="
        docker logs "$CONTAINER_NAME" 2>&1 | tail -50 || true
        echo ""
        echo -e "${GREEN}PASS: Docker smoke test${NC}"
        exit 0
    fi

    if ! docker ps -q -f "name=$CONTAINER_NAME" | grep -q .; then
        echo -e "${RED}Container exited unexpectedly${NC}"
        docker logs "$CONTAINER_NAME" 2>&1 || true
        exit 1
    fi

    if [ $((i % 10)) -eq 0 ]; then
        echo "  Still waiting for health... (${i}s)"
    fi

    sleep 1
done

echo -e "${RED}Timed out waiting for health endpoint${NC}"
docker logs "$CONTAINER_NAME" 2>&1 || true
exit 1
