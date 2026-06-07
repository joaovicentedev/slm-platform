FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

ARG UV_SYNC_ARGS="--group serving"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project ${UV_SYNC_ARGS}

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked ${UV_SYNC_ARGS}

CMD ["python", "-m", "main"]
