#!/bin/bash
# wait-for-db.sh

set -e

host="$DB_HOST"
name="$DB_NAME"
user="$DB_USER"
password="$DB_PASS"
cmd="$@"

echo "Waiting for PostgreSQL at $host..."

# Boucle d'attente pour la base de données
until PGPASSWORD=$password pg_isready -h "$host" -p 5432 -U "$user" -d "$name"; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"
exec $cmd