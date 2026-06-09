FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS base
WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    make \
    swig \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://abyz.me.uk/lg/lg.zip && \
    unzip lg.zip && \
    cd lg && \
    make && \
    make install && \
    ldconfig && \
    cd .. && rm -rf lg lg.zip

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

FROM ghcr.io/astral-sh/uv:python3.14-bookworm

COPY --from=base /usr/local/lib/liblgpio.so* /usr/local/lib/
RUN ldconfig

COPY --from=base /src/.venv /src/.venv
COPY src /src

WORKDIR /src
CMD ["uv", "run", "python", "main.py"]
