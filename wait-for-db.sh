#!/bin/sh

# Wait for database to be ready
set -e

host="${DB_HOST:-db}"
port="${DB_PORT:-3306}"

echo "Waiting for database at $host:$port..."

while ! nc -z "$host" "$port"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - continuing..."

exec "$@"
