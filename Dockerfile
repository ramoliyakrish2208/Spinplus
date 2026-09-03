# ==============================================================================
# SpinPlus Django SaaS — Cloud Run Production Dockerfile
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install minimal OS dependencies for Pillow and PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python production dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Collect static assets into /app/staticfiles for WhiteNoise serving
RUN DJANGO_DEBUG=False python manage.py collectstatic --noinput

# Create dedicated non-root user and assign permissions
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/logs && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Cloud Run Container Contract: Listen on $PORT and respond to SIGTERM gracefully
CMD ["sh", "-c", "exec gunicorn spinplus.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 2 --timeout 60 --access-logfile - --error-logfile -"]
