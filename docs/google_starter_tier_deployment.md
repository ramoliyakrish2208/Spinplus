# 📋 Google Cloud Starter Tier Deployment Guide & Architecture

## 1. Cloud Architecture Overview
```text
Public User (HTTPS :443)
       │
       ▼
┌──────────────────────────────────────────┐
│ Google Cloud Run (Container Service)      │
│ • SSL Termination (Google-managed TLS)    │
│ • WhiteNoise Static Files (Gzip/Brotli)  │
│ • Gunicorn WSGI Worker Pool ($PORT: 8080) │
│ • Python 3.11-slim Base Container        │
│ • Non-root execution (`appuser`)         │
└──────────────────┬───────────────────────┘
                   │
                   ▼ (Database Network)
┌──────────────────────────────────────────┐
│ Cloud SQL for PostgreSQL / Free DB       │
│ • Configured via DATABASE_URL env var    │
│ • Atomic spin locking (select_for_update)│
│ • Multi-tenant schema isolation          │
└──────────────────────────────────────────┘
```

## 2. Environment Variables Configuration for Cloud Run
When deploying to Cloud Run, set the following environment variables:
```dotenv
SECRET_KEY=<generate-high-entropy-secret>
DJANGO_DEBUG=False
SITE_URL=https://<your-service-name>-<hash>-<region>.a.run.app
ALLOWED_HOSTS=<your-service-name>-<hash>-<region>.a.run.app,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://<your-service-name>-<hash>-<region>.a.run.app
DATABASE_URL=postgres://<user>:<password>@<host>:5432/<dbname>
ENABLE_HTTPS_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## 3. Local vs Cloud Database Portability
- **Local Development**: Continues using SQLite WAL mode (`db.sqlite3`) with zero setup needed.
- **Cloud Run**: Automatically switches to PostgreSQL when `DATABASE_URL` is passed.

## 4. Container Build & Deployment Command (gcloud)
```bash
# Build container image using Cloud Build
gcloud builds submit --tag gcr.io/inlaid-marker-464014-i1/spinplus

# Deploy service to Cloud Run
gcloud run deploy spinplus \
    --image gcr.io/inlaid-marker-464014-i1/spinplus \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080
```
*(Note: Requires billing enablement per Google Cloud policy).*
