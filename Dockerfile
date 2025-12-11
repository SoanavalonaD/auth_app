FROM python:3.12-slim

RUN find /etc/apt/ -name '*.sources' -exec sed -i 's|^\(URIs: \)http://|\1https://|' {} +

RUN apt-get update \
    && apt-get install -y apt-transport-https \
    && apt-get update \
    && apt-get install -y netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/


COPY pyproject.toml /app/
COPY ./uv.lock /app/
COPY ./alembic.ini /app/

COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_HTTP_TIMEOUT=3000

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY ./scripts/entrypoint.sh /app/scripts/entrypoint.sh
COPY ./scripts /app/scripts
COPY ./src /app/src
COPY ./fixture_data /app/fixture_data
COPY ./alembic.ini .

RUN chmod +x /app/scripts/entrypoint.sh

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--host", "127.0.0.1", "--workers", "4", "src/main.py", "--port", "${API_PORT:-8000}"]