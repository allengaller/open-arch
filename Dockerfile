FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md uv.lock ./
COPY src/ ./src/
COPY skills/ ./skills/
COPY tests/ ./tests/

RUN uv sync --frozen --no-dev

ENV OPENARCH_WORKSPACE=/data/deliverables
VOLUME ["/data/deliverables"]

CMD ["uv", "run", "openarch"]
