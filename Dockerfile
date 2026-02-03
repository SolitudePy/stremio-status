FROM ghcr.io/astral-sh/uv:python3.12-alpine

ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

COPY stremio_status ./stremio_status

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

EXPOSE 7000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:7000/health || exit 1

ENV HOST=0.0.0.0
ENV PORT=7000

CMD ["uv", "run", "stremio-status"]
