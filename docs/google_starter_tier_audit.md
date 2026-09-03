# 🔍 SpinPlus — Google Cloud Starter Tier Comprehensive Project Audit
**Target Platform:** Google Cloud Starter Tier (Strictly ₹0 / No Card / No Payment Method / No Cloud Billing)  
**Date:** September 3, 2026  
**Auditor:** Senior Django + Cloud Platform Deployment Engineer  
**Document Status:** Complete Pre-Deployment Audit Baseline (Phase 0)

---

## 1. Executive Summary

This audit establishes the definitive baseline of the **SpinPlus Django SaaS platform** prior to Google Cloud Starter Tier containerization and deployment. SpinPlus is an active, production-hardened, multi-tenant SaaS application featuring a customer wheel engine, dynamic seasonal themes, QR code resolution, and atomic inventory management.

The goal is to prepare and deploy SpinPlus to Google Cloud Starter Tier while strictly honoring:
- **Total Cost:** ₹0
- **Payment Methods:** ZERO cards (credit/debit) entered or requested
- **Billing Account:** NO Cloud Billing account created or attached
- **Preservation:** 100% preservation of all existing business logic, UI/UX, and tenant security

---

## 2. Comprehensive 28-Point Project Audit

### 1. Repository Structure & Root
- **Absolute Path:** `d:\Avadh\SpinPlus`
- **Root Directory Layout:**
  - `core/` — Primary application package (models, views, services, QR, context processors, tests, migrations).
  - `spinplus/` — Django project package (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`).
  - `templates/` — UI templates (`base.html`, `auth/`, `customer/`, `dashboard/`, `errors/`).
  - `static/` — Source static assets (`css/themes.css`, `js/wheel.js`, `js/theme-engine.js`, `js/ui.js`, `js/theme-engine-saas.js`).
  - `staticfiles/` — Pre-collected static production assets (132 files).
  - `media/` — User-uploaded and generated media (`qr_codes/`, `shop_logos/`, `shop_covers/`, `campaign_heroes/`).
  - `deployment/` — Systemd service and Nginx reverse proxy configs.
  - `docs/` — Deployment guides (`OCI_DEPLOYMENT_GUIDE.md`, `deployment_guide.md`).
  - `scripts/` — Operational scripts (`backup_sqlite.py`, `load_test.py`, `seed_production_shops.py`).
  - `logs/` — Application logs (`spinplus.log`, `benchmark_results.json`).
  - `backups/` — SQLite online database backups (`spinplus_backup_*.sqlite3`).

### 2. Django Project Root
- Detected at `d:\Avadh\SpinPlus` containing `manage.py` and project configuration directories.

### 3. Settings Module
- **Module:** `spinplus.settings` (`spinplus/settings.py`).
- **Framework Version:** Django 5.2.9 on Python 3.11.0.
- **Key Modules Configured:** `core`, `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.

### 4. Manage.py Entrypoint
- Present at `d:\Avadh\SpinPlus\manage.py`.
- Sets `DJANGO_SETTINGS_MODULE = 'spinplus.settings'`.

### 5. Requirements & Dependency Manifest
- `requirements.txt` currently specifies:
  - `Django>=5.0.0,<6.0.0`
  - `Pillow>=10.0.0`
  - `qrcode>=7.4.2`
  - `gunicorn>=21.2.0`
  - `python-dotenv>=1.0.0`
- **Cloud Run Requirements Needed:**
  - `psycopg2-binary>=2.9.9` (PostgreSQL client driver)
  - `whitenoise>=6.6.0` (Production container static file server)

### 6. Templates & View Layer
- Total Templates: 20 template files.
- Uses semantic HTML5, Bento grid layouts, vanilla CSS variables, Lucide icons, and Google Fonts (Inter + Cinzel).
- Custom Error Pages: `400.html`, `403.html`, `404.html`, `500.html` configured via `handler400`, `handler403`, `handler404`, `handler500` in `spinplus/urls.py`.

### 7. Static Files Architecture
- `STATIC_URL = '/static/'`
- `STATICFILES_DIRS = [BASE_DIR / 'static']`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- **Assets:**
  - `themes.css` (86 KB, 2800+ lines): Contains 25+ curated theme definitions (Royal, Luxury, Coffee, Sports, Festival, etc.).
  - `wheel.js` (58 KB): HTML5 Canvas physics engine with elastic deceleration and high-DPI scaling.
  - `theme-engine.js` (22 KB): Particle canvas effects and atmospheric lighting.
  - `ui.js` (11 KB): Global double-submission prevention and toast alert engine.

### 8. Media Files & Storage Handling
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`
- Models with file uploads:
  - `Shop.logo` (`shop_logos/`)
  - `Shop.cover_image` (`shop_covers/`)
  - `ShopBranding.wheel_center_logo` (`wheel_logos/`)
  - `Campaign.hero_image` (`campaign_heroes/`)
  - `QRCode.qr_image` (`qr_codes/`)
- All upload fields use `models.ImageField`, enforcing Pillow image validation.

### 9. Database Configuration & Concurrency
- Current default database: SQLite 3 with WAL mode enabled:
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
          'OPTIONS': {
              'timeout': 20.0,
              'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;',
          }
      }
  }
  ```
- **Cloud Run Implication:** Cloud Run instances are stateless and ephemeral. Local SQLite files cannot serve as persistent multi-instance cloud storage. An environment-driven abstraction is required to support PostgreSQL in the cloud while preserving SQLite locally.

### 10. Environment Variable Handling
- Loads `.env` file via custom parser in `spinplus/settings.py` with fallback defaults.
- Environment variables supported:
  - `SECRET_KEY`
  - `DJANGO_DEBUG` / `DEBUG`
  - `ALLOWED_HOSTS`
  - `CSRF_TRUSTED_ORIGINS`
  - `SITE_URL`
  - `SECURE_SSL_REDIRECT` / `ENABLE_HTTPS_REDIRECT`
  - `SESSION_COOKIE_SECURE`
  - `CSRF_COOKIE_SECURE`
  - `SECURE_HSTS_SECONDS`
  - `X_FRAME_OPTIONS`

### 11. Authentication & Role Authorization
- Custom user model: `core.User` (`AUTH_USER_MODEL = 'core.User'`).
- Roles: `super_admin` (`is_superuser=True`, access to `/dashboard/admin/`), `shop_owner` (access to `/dashboard/shop/`).
- **No staff role** is used, adhering to the architecture.
- Public/customer players do not require authentication to spin or view coupons.

### 12. CSRF Configuration
- `CsrfViewMiddleware` active.
- `CSRF_TRUSTED_ORIGINS` dynamically loaded from environment.
- Form submissions protected with `{% csrf_token %}`.
- CSRF cookies secured (`CSRF_COOKIE_SECURE = True` in production).

### 13. Allowed Hosts
- Configurable via `ALLOWED_HOSTS` environment variable.
- Clean fallback: `127.0.0.1,localhost,testserver` (no wildcard `*` fallback).

### 14. URL Routing
- `spinplus/urls.py` delegates to `core.urls`.
- Permanent QR pattern: `path('s/<str:public_token>/', views.public_shop_view, name='public_shop')`.
- Spin API: `path('s/<str:public_token>/spin/', views.spin_wheel_api, name='spin_wheel_api')`.
- Health Check: `path('health/', views.health_check_view, name='health_check')`.

### 15. WSGI / ASGI Callables
- WSGI: `spinplus.wsgi:application` (`spinplus/wsgi.py`).
- ASGI: `spinplus.asgi:application` (`spinplus/asgi.py`).
- Fully PEP 3333 compliant.

### 16. Background Tasks
- Zero asynchronous task queues (Celery/Redis) present.
- All operations (QR generation, coupon redemption, logging, and atomic spin calculations) run synchronously inside Django view handlers.

### 17. Scheduled Tasks
- Currently handled via system cron executing `scripts/backup_sqlite.py`.

### 18. Filesystem Writes
- `QRCode.qr_image.save(...)` in `core/qr.py` writes generated QR PNGs to disk.
- User logo and hero image uploads write to `media/`.
- `spinplus.log` writes to `logs/`.
- SQLite database writes to `db.sqlite3`, `db.sqlite3-wal`, and `db.sqlite3-shm`.

### 19. SQLite-Specific Code
- Zero custom SQLite code in `core/models.py`, `core/views.py`, or `core/services/`.
- Code uses 100% standard Django ORM methods (`select_for_update()`, `transaction.atomic()`, `F()` expressions).
- Only `settings.py` (PRAGMA pragmas) and `scripts/backup_sqlite.py` reference SQLite.

### 20. Third-Party Packages
- `Django` (5.2.9)
- `Pillow` (12.0.0)
- `qrcode` (8.2)
- `gunicorn` (26.2.0)
- `python-dotenv` (1.0.0)
- `whitenoise` (6.12.0 in virtual environment)

### 21. Deployment Files
- `deployment/spinplus.service` (systemd unit file).
- `deployment/nginx_spinplus.conf` (Nginx reverse proxy config).
- `gunicorn.conf.py` (Gunicorn production config).
- `DEPLOYMENT.md` (Base deployment guide).
- `docs/OCI_DEPLOYMENT_GUIDE.md` (OCI Always Free runbook).

### 22. Docker Configuration
- Currently **absent**.
- Need to create `Dockerfile` and `.dockerignore` for Cloud Run containerization.

### 23. Test Suite
- Comprehensive suite in `core/tests.py`.
- **65 tests** covering tenant isolation, atomic spin inventory, campaign dates, coupon verification, and subscription plans.
- Test execution time: ~115–125 seconds.
- Status: **65/65 passing (0 failures, 0 errors)**.

### 24. Hardcoded Localhost URLs
- **Identified in `core/views.py`**:
  - Line 360: `defaults={'target_url': f"http://127.0.0.1:8000/s/{shop.public_token}/"}`
  - Line 984: `defaults={'target_url': f"http://127.0.0.1:8000/s/{shop.public_token}/"}`
- **Resolution Plan:** Refactor to use `getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')` to match `core/qr.py`.

### 25. Hardcoded HTTP/HTTPS URLs
- Templates use `{% url '...' %}` exclusively.
- External CDN scripts (Lucide, JsBarcode, Confetti, Google Fonts) all use HTTPS.

### 26. Service-Worker Caching
- No service-worker caching present; no offline cache corruption risks.

### 27. Absolute Static / Media URLs
- Templates use `{% static '...' %}` and `{{ object.field.url }}` correctly.

### 28. Ephemeral vs Persistent Local Storage Assumptions
- **Assumption 1:** `db.sqlite3` stored on local disk. (Must support PostgreSQL via env vars for Cloud Run).
- **Assumption 2:** `media/` uploads written to local container disk. (Requires cloud storage adapter or graceful media handling).
- **Assumption 3:** `logs/spinplus.log` written to local disk. (Cloud Run requires standard output / `StreamHandler` for Google Cloud Logging).

---

## 3. Google Cloud Starter Tier Constraint Analysis

| Resource | Cloud Standard (Paid) | Starter Tier (₹0 Target) | Feasibility / Mitigation |
| :--- | :--- | :--- | :--- |
| **Compute / Serving** | Cloud Run (Billed / Free tier quota) | Cloud Run Starter Tier | **Fully Supported**: Stateless container, auto-scaling to zero, HTTP/HTTPS serving on `$PORT`. |
| **Database** | Cloud SQL for PostgreSQL | Typically requires Cloud Billing | **Abstraction Required**: Add PostgreSQL database configuration driven by `DATABASE_URL` / `DB_ENGINE`. If Cloud SQL requires billing, report blocker honestly without creating billing. |
| **Media Storage** | Google Cloud Storage (GCS) | Typically requires Cloud Billing | **Report Requirement**: If GCS is unavailable without billing, report limitation honestly. |
| **Network & SSL** | Custom domain with Cloud SSL | Provided `*.run.app` HTTPS domain | **Fully Supported**: Google provides automated TLS/HTTPS for free on Cloud Run URLs. |

---

## 4. Phase 0 Audit Conclusion & Next Steps
- **Codebase Integrity:** Excellent. Clean Django MVT architecture with zero vendor lock-in.
- **Next Phase:** Phase 1 (Create Git baseline branch `deployment/google-starter-tier` and document baseline state in `docs/pre_cloud_baseline.md`).
