#!/bin/sh

# Exit on error
set -e

# Debug
set -x

# Wait for database
echo "Waiting for database"
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.1
done
echo "Database started"

# 2. Apply database migrations
echo "Apply database migrations"
python manage.py migrate
echo "Apply database migrations done"

# https://docs.gunicorn.org/en/stable/design.html#how-many-workers
num_cores=$(nproc --all)
workers=$((2 * num_cores + 1))

# 3. Start server
echo "Starting server with $workers workers"
gunicorn --workers=$workers --bind=0.0.0.0:8000 feedvault.wsgi:application --log-level=info --access-logfile=- --error-logfile=- --forwarded-allow-ips="172.*,192.*" --proxy-allow-from="172.*,192.*"
echo "Bye, love you"
