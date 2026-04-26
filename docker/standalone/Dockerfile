# CogMem standalone Docker image (API only).
# Supports embedded pg0 by default and external PostgreSQL via COGMEM_API_DATABASE_URL.
#
# Build args:
#   INCLUDE_LOCAL_MODELS=true/false  Install local embeddings/reranker dependencies.
#   PRELOAD_ML_MODELS=true/false     Pre-download local ST models during image build.
#   TORCH_CPU_VERSION=...            Pin CPU-only torch version used in Docker image.
#   ST_VERSION=...                   Pin sentence-transformers version in Docker image.

ARG INCLUDE_LOCAL_MODELS=true
ARG PRELOAD_ML_MODELS=false
ARG TORCH_CPU_VERSION=2.11.0
ARG ST_VERSION=5.3.0

FROM python:3.13-slim AS standalone

ARG INCLUDE_LOCAL_MODELS
ARG PRELOAD_ML_MODELS
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
ENV COGMEM_API_COMMAND="python -m cogmem_api.main"
ENV COGMEM_API_HOST=0.0.0.0
ENV COGMEM_API_PORT=8888
ENV COGMEM_API_LOG_LEVEL=info
ENV PYTHONUNBUFFERED=1

RUN if [ "${PRELOAD_ML_MODELS}" = "true" ] && [ "${INCLUDE_LOCAL_MODELS}" = "true" ]; then \
        /app/.venv/bin/python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; SentenceTransformer('BAAI/bge-small-en-v1.5'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"; \
    else \
        echo "Skipping local ML model preload"; \
    fi

EXPOSE 8888

CMD ["/app/start-all.sh"]
