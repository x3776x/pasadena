#!/bin/sh
set -e

# Esperar a PostgreSQL
echo "Esperando a PostgreSQL..."
until pg_isready -h "postgres_db" -p 5432 -U "papu"; do
  sleep 2
done

echo " Ejecutando migraciones..."
alembic upgrade head

echo " Insertando datos iniciales..."
python -m app.seed_data

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001
