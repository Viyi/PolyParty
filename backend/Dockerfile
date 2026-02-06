# --- Stage 1: Base & uv setup ---
FROM python:3.12-slim AS base

# Install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    WORKDIR=/app

WORKDIR $WORKDIR

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Development ---
FROM base AS development

# Install dependencies using the cache mount for speed
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project

COPY . .

# Hot reloading via uvicorn
CMD ["uv", "run", "uvicorn", "poly_party.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Stage 3: Production ---
FROM base AS production

# Create a non-root user
RUN groupadd -g 999 python && useradd -r -u 999 -g python python

# Install dependencies for production (exclude dev group if you have one)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN chown -R python:python $WORKDIR
USER python

CMD ["uv", "run", "uvicorn", "poly_party.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]