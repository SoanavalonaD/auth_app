#!/bin/sh
# entrypoint.sh - Script pour garantir que l'API attend la disponibilité de la BDD

set -e

DB_HOST="db" # Nom du service BDD dans docker-compose.yml
DB_PORT="5432"

echo "Waiting for PostgreSQL ($DB_HOST:$DB_PORT) to be accessible..."

# Utilise netcat (nc) pour vérifier si le port est ouvert. 
# Si votre image Dockerfile n'a pas 'nc', vous devrez l'installer (ex: apt-get install -y netcat)
until nc -z $DB_HOST $DB_PORT; do
  echo "PostgreSQL est encore indisponible - attente 1s..."
  sleep 1
done

echo "PostgreSQL est accessible. Démarrage de l'application..."

# Exécute la commande principale spécifiée dans docker-compose.yml
exec "$@"