# syntax=docker/dockerfile:1

# ---- 前端构建 ----
FROM node:22-alpine AS webui
WORKDIR /webui
COPY webui/package.json webui/package-lock.json ./
RUN npm ci
COPY webui/ ./
RUN npm run build

# ---- Python 运行时 ----
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY skills/ ./skills/
COPY GTM/ ./GTM/
COPY tests/ ./tests/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# 前端产物放进包内静态目录（app.py 的 find_static_dir 第一候选）
COPY --from=webui /webui/dist ./src/openarch/web/static/dist

ENV OPENARCH_DB=/data/openarch.db
ENV OPENARCH_WORKSPACE=/data/deliverables
VOLUME ["/data"]

CMD ["uv", "run", "--no-sync", "openarch", "web"]