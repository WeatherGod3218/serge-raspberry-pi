
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

WORKDIR /app

# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     linux-headers \
#     i2c-tools \
#     libgpiod \
#     libgpiod-dev

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

# RUN apk add --no-cache libgpiod i2c-tools

COPY --from=base /app/.venv /app/.venv
COPY src /app
# COPY --from=docbuilder /appdocs/site /app/docs

WORKDIR /app

RUN addgroup -g 2000 usergroup && \ 
    adduser -S -u 1001 -G usergroup appuser

USER appuser

CMD ["uv", "run", "python", "main.py"]
