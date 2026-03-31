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

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run -d --name "$CONTAINER_NAME" \
    -p 8888:8888 \
    -e COGMEM_API_DATABASE_URL="${COGMEM_API_DATABASE_URL:-pg0}" \
    "$IMAGE" >/dev/null

start_time=$(date +%s)
for i in $(seq 1 "$TIMEOUT"); do
    if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${GREEN}Health check passed after ${duration}s${NC}"

        echo "Running retain/recall smoke checks..."
        "$REPO_ROOT/scripts/smoke-test-cogmem.sh" "$SMOKE_BASE_URL"

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
