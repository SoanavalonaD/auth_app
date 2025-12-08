# Étape 1: Utilisation de l'image de base Python
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN find /etc/apt/ -name '*.sources' -exec sed -i 's|^\(URIs: \)http://|\1https://|' {} +

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    python3-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# peux être utile pour les scripts
RUN pip install psycopg2-binary

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

ENV PATH="/app/.venv/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV UV_HTTP_TIMEOUT=3000

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync

ENV PYTHONPATH=/app

COPY ./scripts /app/scripts
COPY ./src /app/src
COPY ./fixture_data /app/fixture_data

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--host", "127.0.0.1", "--workers", "4", "src/main.py", "--port", "${API_PORT:-8000}"]