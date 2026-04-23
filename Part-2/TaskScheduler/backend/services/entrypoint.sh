#!/bin/bash
set -e

DB_RETRIES=30
DB_WAIT_SECS=1

# Wait for database
echo "Waiting for database..."
until psql -h "${DATABASE_HOST:-postgres}" -U "${DATABASE_USER:-postgres}" -d "${DATABASE_NAME:-taskscheduler}" -c "SELECT 1" 2>/dev/null; do
  DB_RETRIES=$((DB_RETRIES - 1))
  if [ $DB_RETRIES -le 0 ]; then
    echo "Failed to connect to database"
    exit 1
  fi
  echo "Database not ready, retrying in ${DB_WAIT_SECS}s..."
  sleep $DB_WAIT_SECS
done

echo "✓ Database is ready"

# Run Alembic migrations if alembic.ini exists
if [ -f alembic.ini ]; then
  echo "Running Alembic migrations..."
  uv run alembic upgrade head
  echo "✓ Migrations completed"
else
  echo "ℹ No alembic.ini found, skipping migrations"
fi

# Start application
echo "Starting application..."
exec uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
