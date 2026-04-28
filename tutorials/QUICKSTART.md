# CogMem Quickstart

## Start the API

```bash
# Clone and install
cd agent-memory-cognitive
uv sync

# Copy and edit env vars
cp .env.example .env 2>nul || cp .env.development .env 2>nul
# Edit .env: set COGMEM_API_LLM_BASE_URL to your LLM endpoint

# Run the API server
uv run cogmem-api
# Server starts at http://localhost:8888
```

## Your First Retain + Recall

```bash
# Create a memory bank
curl -X PUT http://localhost:8888/v1/test_user/banks/test_bank

# Store a conversation
curl -X POST http://localhost:8888/v1/test_user/banks/test_bank/memories \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "content": "I joined DI as an ML Engineer in April 2024 and I love working with Python. I always check email before standup meetings.",
      "event_date": "2024-04-15T09:00:00Z"
    }]
  }'

# Query the memory
curl -X POST http://localhost:8888/v1/test_user/banks/test_bank/memories/recall \
  -H "Content-Type: application/json" \
  -d '{"query": "What does the user do for work and what are their habits?"}'

# Get memory stats
curl http://localhost:8888/v1/test_user/banks/test_bank/stats
```

## What Just Happened?

Behind the scenes, the retain pipeline:

1. **Extracted 3 facts** from the input text:
   - `experience`: "I joined DI as ML Engineer in April 2024" (occurred_start=2024-04-15)
   - `opinion`: "User loves Python for ML" (confidence high)
   - `habit`: "User always checks email before standup" (S-R link created)

2. **Stored them** in `memory_units` with:
   - Sentence-transformer embedding (BAAI/bge-small-en-v1.5)
   - Raw snippet preserved for lossless recall
   - 7 edge types created linking them

3. **Recall** retrieved relevant facts by:
   - Semantic similarity (vector search)
   - BM25 full-text
   - Temporal filtering (April 2024)
   - Graph traversal (entity links)

## Run a Test

```bash
# Retain baseline test
uv run python tests/artifacts/test_task201_retain_baseline.py

# Search pipeline smoke test
uv run python tests/artifacts/test_task301_search_fork.py

# Adaptive router test
uv run python tests/artifacts/test_task303_adaptive_router.py
```

## Docker Deployment

```bash
# Build
docker build -f docker/standalone/Dockerfile -t cogmem:local .

# Run
docker run --env-file .env -p 8888:8888 cogmem:local
```

## Next Steps

- Read `ARCHITECTURE/overview.md` to understand the system
- Read `CONFIG/env-vars.md` to understand all configuration options
- Read `LEARNING-PATH.md` for the full learning track
