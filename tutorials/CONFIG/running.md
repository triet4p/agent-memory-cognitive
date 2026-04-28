# Running CogMem — Three Deployment Modes

## Overview

CogMem can be run in three ways:

| Mode | When to Use | Database | LLM |
|------|------------|---------|-----|
| **Host** (direct) | Development, debugging | `pg0` (embedded) or external pg | Local via ngrok |
| **Docker standalone** | Single-node deployment | `pg0` volume or external pg | Via ngrok |
| **Docker compose** | Multi-service setup | External pg service | Separate container or external |

## Mode 1 — Run on Host (Direct)

### Prerequisites

```bash
# Install dependencies
uv sync

# Edit .env with your LLM endpoint
# Minimal .env for local dev:
COGMEM_API_LLM_BASE_URL=http://localhost:11434/v1
COGMEM_API_LLM_MODEL=ministral3-3b
COGMEM_API_LLM_API_KEY=ollama
COGMEM_API_DATABASE_URL=pg0
COGMEM_API_GRAPH_RETRIEVER=bfs
```

### Start the API

```bash
# Simple start
uv run cogmem-api

# With custom host/port
COGMEM_API_HOST=127.0.0.1 COGMEM_API_PORT=8889 uv run cogmem-api

# With debug logging
COGMEM_API_LOG_LEVEL=debug uv run cogmem-api
```

### Verify Health

```bash
curl http://localhost:8888/health
# Expected: {"status":"ok","version":"..."}
```

### Stop

`Ctrl+C` — the process terminates cleanly.

### Using External PostgreSQL (Host)

```bash
# Instead of pg0, point to your pg instance
COGMEM_API_DATABASE_URL=postgresql://user:pass@localhost:5432/cogmem \
COGMEM_API_GRAPH_RETRIEVER=bfs \
uv run cogmem-api
```

### First-Time DB Setup

The first time you run with external pg, the schema is created automatically via SQLAlchemy. No manual migration needed for new databases.

---

## Mode 2 — Docker Standalone

### Build the Image

```bash
docker build -f docker/standalone/Dockerfile -t cogmem:local .
```

### Run with Embedded Postgres (pg0)

```bash
docker run -d \
  --name cogmem-dev \
  -p 8888:8888 \
  -v ~/.cogmem-docker-smoke:/home/cogmem/.pg0 \
  -e COGMEM_API_DATABASE_URL=pg0 \
  -e COGMEM_API_LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  -e COGMEM_API_LLM_MODEL=ministral3-3b \
  -e COGMEM_API_LLM_API_KEY=ollama \
  -e COGMEM_API_GRAPH_RETRIEVER=bfs \
  cogmem:local
```

**Note**: `host.docker.internal` routes from Docker container to the host machine's localhost. On Linux you may need `--network=host` instead.

### Run with External PostgreSQL

```bash
docker run -d \
  --name cogmem-dev \
  -p 8888:8888 \
  -e COGMEM_API_DATABASE_URL=postgresql://user:pass@pg-host:5432/cogmem \
  -e COGMEM_API_LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  -e COGMEM_API_LLM_MODEL=ministral3-3b \
  -e COGMEM_API_LLM_API_KEY=ollama \
  -e COGMEM_API_GRAPH_RETRIEVER=bfs \
  cogmem:local
```

### Verify Health

```bash
curl http://localhost:8888/health

# Watch startup logs
docker logs -f cogmem-dev --tail 50

# Follow real-time logs
docker logs -f cogmem-dev
```

### Stop and Remove

```bash
docker stop cogmem-dev && docker rm cogmem-dev
```

### Run the Smoke Test

```powershell
# PowerShell
.\docker\test-image.ps1 -Image cogmem:local

# Linux/macOS
./docker/test-image.sh cogmem:local
```

### Environment Variables in Docker

| Variable | Purpose | Example |
|----------|---------|---------|
| `COGMEM_API_DATABASE_URL` | DB connection | `pg0` or `postgresql://...` |
| `COGMEM_API_LLM_BASE_URL` | LLM endpoint | `http://host.docker.internal:11434/v1` |
| `COGMEM_API_LLM_MODEL` | Model name | `ministral3-3b` |
| `COGMEM_API_GRAPH_RETRIEVER` | Graph strategy | `bfs` (use `link_expansion` for HINDSIGHT baseline) |
| `COGMEM_API_RETAIN_CHUNK_SIZE` | Chunk size | `3000` |
| `COGMEM_API_LOG_LEVEL` | Logging | `info` or `debug` |

### Preload ML Models at Startup

Models are downloaded on first use. To pre-fetch at container start:

```bash
docker run -d \
  ... \
  -e COGMEM_DOCKER_INCLUDE_LOCAL_MODELS=true \
  -e HF_TOKEN=hf_your_token \
  cogmem:local
```

This downloads the sentence-transformer and cross-encoder models before the API starts serving.

---

## Mode 3 — Docker Compose

If you have a `docker-compose.yml` at project root, use it to orchestrate CogMem + PostgreSQL + any other services.

### Typical docker-compose.yml Structure

```yaml
version: "3.9"
services:
  cogmem:
    build:
      context: .
      dockerfile: docker/standalone/Dockerfile
    ports:
      - "8888:8888"
    environment:
      COGMEM_API_DATABASE_URL: postgresql://cogmem:password@postgres:5432/cogmem
      COGMEM_API_LLM_BASE_URL: http://host.docker.internal:11434/v1
      COGMEM_API_LLM_MODEL: ministral3-3b
      COGMEM_API_LLM_API_KEY: ollama
      COGMEM_API_GRAPH_RETRIEVER: bfs
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: cogmem
      POSTGRES_USER: cogmem
      POSTGRES_PASSWORD: password
    volumes:
      - cogmem-pg-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cogmem -d cogmem"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

volumes:
  cogmem-pg-data:
```

### Run with Compose

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f cogmem

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Verify with Compose

```bash
# Check services are healthy
curl http://localhost:8888/health
# Expected: {"status":"ok","version":"..."}

# Check postgres is ready
docker-compose exec postgres pg_isready -U cogmem -d cogmem
```

---

## Switching Between Deployment Modes

### Retain Data is Shared (if same DATABASE_URL)

Whether you run on host or in Docker, if they point to the **same PostgreSQL instance**, they share the same data. This is useful for eval:

```
Host (dev)  ──┐
             ├──►  postgresql://user:pass@pg-host:5432/cogmem  (shared DB)
Docker (eval)─┘
```

**Caution**: Never run two `cogmem-api` processes against the **same `pg0`** embedded instance simultaneously. pg0 is single-process.

### Resetting pg0 Data

pg0 stores its data in `~/.pg0/` by default. To reset:

```bash
# Stop the running container/process
docker stop cogmem-dev  # or Ctrl+C on host

# Remove pg0 data directory
rm -rf ~/.cogmem-docker-smoke/

# Restart — new empty database will be created
```

---

## Common Startup Issues

### API doesn't bind to port

```
Error: Address already in use: 0.0.0.0:8888
```

Something else is using port 8888. Either stop that process or run on a different port:

```bash
COGMEM_API_PORT=8889 uv run cogmem-api
```

### pg0 fails to start in Docker

```
pg0: could not start embedded postgres
```

The pg0 volume directory (`~/.cogmem-docker-smoke/`) may be corrupted. Delete it and restart:

```bash
docker stop cogmem-dev && docker rm cogmem-dev
rm -rf ~/.cogmem-docker-smoke/
docker run -v ~/.cogmem-docker-smoke:/home/cogmem/.pg0:rw ...
```

### Health check passes but retain fails

```
asyncpg.ForeignKeyViolationError
```

This was a known bug (task 756) — the `documents` table was not being upserted before `memory_units`. This is fixed in the current build. If you see this, verify your `fact_storage.py` has the upsert code.

### LLM calls all fail

```
ModuleNotFoundError: No module named 'dateparser'
```

The `dateparser` library is required for temporal query parsing. In Docker, make sure the image was built with `uv sync`. If you're using a custom image, add it:

```dockerfile
RUN uv add dateparser
```

---

## Quick Reference Commands

```bash
# Host — start
uv run cogmem-api

# Host — with external pg
COGMEM_API_DATABASE_URL=postgresql://user:pass@host:5432/db uv run cogmem-api

# Docker standalone — build + run
docker build -f docker/standalone/Dockerfile -t cogmem:local .
docker run -d --name cogmem -p 8888:8888 -e COGMEM_API_DATABASE_URL=pg0 cogmem:local

# Docker smoke test
.\docker\test-image.ps1 -Image cogmem:local

# Docker compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```
