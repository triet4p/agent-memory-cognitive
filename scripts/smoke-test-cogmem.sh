#!/bin/bash
#
# CogMem retain/recall smoke script.
#
# Usage:
#   ./scripts/smoke-test-cogmem.sh [base_url]
#
# Example:
#   ./scripts/smoke-test-cogmem.sh http://localhost:8888

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

BASE_URL="${1:-http://localhost:8888}"
BANK_ID="cogmem-smoke-$$"

echo "Running retain/recall smoke test against: $BASE_URL"
echo "Bank: $BANK_ID"

echo ""
echo "--- Retain ---"
RETAIN_RESPONSE=$(curl -sf -X POST "$BASE_URL/v1/default/banks/$BANK_ID/memories" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"content": "Alice is a software engineer who likes distributed systems and Python."}]}')

echo "$RETAIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RETAIN_RESPONSE"

SUCCESS=$(echo "$RETAIN_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "False")
if [ "$SUCCESS" != "True" ]; then
  echo -e "${RED}FAIL: retain did not return success=true${NC}"
  exit 1
fi

echo ""
echo "--- Recall ---"
RECALL_RESPONSE=$(curl -sf -X POST "$BASE_URL/v1/default/banks/$BANK_ID/memories/recall" \
  -H "Content-Type: application/json" \
  -d '{"query": "What does Alice do?"}')

echo "$RECALL_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RECALL_RESPONSE"

RESULTS_COUNT=$(echo "$RECALL_RESPONSE" | python3 -c "import sys, json; d = json.load(sys.stdin); print(len(d.get('results', [])))" 2>/dev/null || echo "0")
if [ -z "$RESULTS_COUNT" ] || [ "$RESULTS_COUNT" -eq 0 ]; then
  echo -e "${RED}FAIL: recall returned no results${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}PASS: retain/recall smoke test${NC}"
