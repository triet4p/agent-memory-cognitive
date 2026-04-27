# CogMem standalone Docker image (API only).
# Supports embedded pg0 by default and external PostgreSQL via COGMEM_API_DATABASE_URL.
#
# Build args:
#   INCLUDE_LOCAL_MODELS=true/false  Install local embeddings/reranker dependencies.
#   TORCH_CPU_VERSION=...            Pin CPU-only torch version used in Docker image.
#   ST_VERSION=...                   Pin sentence-transformers version in Docker image.
#
# Runtime env (set via docker-compose or .env — NOT baked into image):
#   PRELOAD_ML_MODELS=true/false     Download ST models on first container startup.
#   HF_TOKEN=...                     HuggingFace token for authenticated downloads.

ARG INCLUDE_LOCAL_MODELS=true
ARG TORCH_CPU_VERSION=2.11.0
ARG ST_VERSION=5.3.0

FROM python:3.13-slim AS standalone

ARG INCLUDE_LOCAL_MODELS
ARG TORCH_CPU_VERSION
ARG ST_VERSION

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    libicu-dev \
    libldap2 \
    liblz4-1 \
    libreadline8 \
    libssl3 \
    libxml2 \
    libxslt1.1 \
    libzstd1 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash cogmem

COPY pyproject.toml uv.lock README.md ./

RUN pip install --no-cache-dir uv \
    && if [ "${INCLUDE_LOCAL_MODELS}" = "true" ]; then \
        uv sync --frozen --extra embedded-db; \
        uv pip install --python /app/.venv/bin/python --index-url https://download.pytorch.org/whl/cpu "torch==${TORCH_CPU_VERSION}+cpu"; \
        uv pip install --python /app/.venv/bin/python "sentence-transformers==${ST_VERSION}"; \
    else \
        uv sync --frozen --extra embedded-db; \
    fi

COPY cogmem_api ./cogmem_api
COPY docker/standalone/start-all.sh /app/start-all.sh
RUN chmod +x /app/start-all.sh \
    && mkdir -p /home/cogmem/.pg0 \
    && chown -R cogmem:cogmem /app /home/cogmem

USER cogmem

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

EXPOSE 8888

CMD ["/app/start-all.sh"]
