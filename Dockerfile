
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# FROM base AS docbuilder

# WORKDIR /appdocs

# COPY mkdocs.yml .
# COPY docs ./docs
# COPY src ./src

# WORKDIR /app

# RUN uv run zensical build --config-file /appdocs/mkdocs.yml

FROM ghcr.io/astral-sh/uv:python3.14-alpine

COPY --from=base /app/.venv /app/.venv
COPY src /app
# COPY --from=docbuilder /appdocs/site /app/docs

WORKDIR /app

RUN addgroup -g 2000 usergroup && \ 
    adduser -S -u 1001 -G usergroup appuser

USER appuser

CMD ["python", "main.py"]
