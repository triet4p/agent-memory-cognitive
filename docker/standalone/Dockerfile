# CogMem standalone Docker image (API only)
# Supports embedded pg0 by default and external PostgreSQL via COGMEM_API_DATABASE_URL.

FROM python:3.13-slim AS standalone

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
COPY cogmem_api ./cogmem_api

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --extra embedded-db

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

EXPOSE 8888

CMD ["/app/start-all.sh"]
