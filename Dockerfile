# syntax=docker/dockerfile:1
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY skills/ ./skills/
COPY tests/ ./tests/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

ENV OPENARCH_WORKSPACE=/data/deliverables
VOLUME ["/data/deliverables"]

CMD ["uv", "run", "--no-sync", "openarch"]
