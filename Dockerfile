# Étape 1: Utilisation de l'image de base Python
FROM python:3.12-slim

# Met en cache la sortie du buffer Python
ENV PYTHONUNBUFFERED=1

# Mise à jour des sources pour utiliser HTTPS
RUN find /etc/apt/ -name '*.sources' -exec sed -i 's|^\(URIs: \)http://|\1https://|' {} +

# Installation des dépendances du système nécessaires pour 'asyncpg' et 'psycopg2'
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    python3-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installation de psycopg2-binary
# Note : C'est une dépendance système, mais elle est souvent installée via pip
# ici pour garantir la présence de l'exécutable client pour Alembic/scripts.
RUN pip install psycopg2-binary

# Définition du répertoire de travail
WORKDIR /app/

# Installation de uv (copie depuis l'image fournie)
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Ajout du chemin d'environnement virtuel au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Compilation du bytecode (bonne pratique uv)
ENV UV_COMPILE_BYTECODE=1

# Mode de lien du cache uv (bonne pratique uv)
ENV UV_LINK_MODE=copy

# Timeout pour les requêtes HTTP (bonne pratique uv)
ENV UV_HTTP_TIMEOUT=3000

# Copie des fichiers de configuration
COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

# Installation des dépendances du projet
# CORRECTION du système de fichiers en lecture seule (Read-only file system):
# Nous retirons le 'mount' de uv.lock pour permettre à uv de l'écrire 
# après l'avoir copié dans le conteneur.
# Nous montons uniquement pyproject.toml car c'est en lecture seule.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync

# Chemin Python pour les importations de modules
ENV PYTHONPATH=/app

# Copie du code source et des scripts
COPY ./scripts /app/scripts
COPY ./src /app/src
COPY ./fixture_data /app/fixture_data

# Synchronisation finale après copie du code 
# Nous utilisons un simple 'uv sync' ici pour capturer les dépendances
# du projet principal + dev (même si elles sont déjà là).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Commande par défaut pour démarrer l'API
CMD ["fastapi", "run", "--host", "127.0.0.1", "--workers", "4", "src/main.py", "--port", "${API_PORT:-8000}"]