#!/usr/bin/env bash
set -e

echo "==> SpinPlus Cloud Startup Engine"
if [ -n "$DATABASE_URL" ]; then
    echo "==> Connecting to cloud PostgreSQL database and running migrations..."
    python manage.py migrate --noinput
else
    echo "==> No DATABASE_URL specified. Running on local SQLite database..."
    python manage.py migrate --noinput
fi

echo "==> Launching Gunicorn WSGI Server on port ${PORT:-8000}..."
exec gunicorn spinplus.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2 --timeout 60 --access-logfile - --error-logfile -
