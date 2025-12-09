FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY --from=builder /app/.venv /app/.venv

COPY ./scripts/entrypoint.sh /app/scripts/entrypoint.sh
COPY ./scripts /app/scripts
COPY ./src /app/src
COPY ./fixture_data /app/fixture_data
COPY ./alembic.ini .

RUN chmod +x /app/scripts/entrypoint.sh

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--host", "127.0.0.1", "--workers", "4", "src/main.py", "--port", "${API_PORT:-8000}"]