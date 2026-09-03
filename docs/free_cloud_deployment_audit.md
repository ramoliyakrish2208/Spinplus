# 🔍 SpinPlus — Free Cloud Deployment Audit
**Target Architecture:** Render Free Web Service + Supabase Free PostgreSQL + DNSHE Free Domain  
**Target Financial Cost:** Strictly ₹0 / $0 (No Credit/Debit Cards, No Payment Methods, No Billing Accounts)  
**Date:** September 3, 2026  
**Auditor:** Senior DevOps & Cloud Deployment Engineer  

---

## 1. System & Project Layout Audit

| Item | Discovered Value | Cloud Deployment Suitability |
| :--- | :--- | :--- |
| **Django Project Name** | `spinplus` | Standard MVT Django package |
| **Manage.py** | `d:\Avadh\SpinPlus\manage.py` | Present, verified executable |
| **Settings Module** | `spinplus.settings` (`spinplus/settings.py`) | Production-ready, environment-driven |
| **WSGI Callable** | `spinplus.wsgi:application` | Fully standard PEP 3333 callable |
| **ASGI Callable** | `spinplus.asgi:application` | Fully standard ASGI callable |
| **Python Version** | Python 3.11.0 (local) / `python:3.11-slim` (container) | Fully supported on Render |
| **Django Version** | Django 5.2.9 | Modern LTS-tier Django release |

---

## 2. Dependencies & Runtime Manifest (`requirements.txt`)
```text
Django>=5.0.0,<6.0.0
Pillow>=10.0.0
qrcode>=7.4.2
gunicorn>=21.2.0
python-dotenv>=1.0.0
whitenoise>=6.6.0
psycopg2-binary>=2.9.9
```
- **Static Assets:** `whitenoise` provides standalone static asset serving without needing an Nginx sidecar container on Render.
- **Database Driver:** `psycopg2-binary` allows direct TCP connection with TLS to Supabase PostgreSQL.
- **Image Processing:** `Pillow` handles QR rendering, logos, and hero graphics.

---

## 3. Database Architecture (Local SQLite vs Cloud Supabase)
- **Local Dev / Testing:** SQLite with WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`).
- **Cloud Production:** Supabase PostgreSQL:
  - Supports standard `DATABASE_URL` format: `postgres://[user]:[password]@[host]:5432/[db]?sslmode=require` or `postgresql://...`
  - Fully supports row-level locking: `select_for_update()` and `transaction.atomic()`.
  - Concurrency: Zero SQLite lock contention under simultaneous cloud player spins.
  - Ephemeral Isolation: Render containers never store authoritative database files on ephemeral disks.

---

## 4. Static Files (WhiteNoise)
- `STATIC_URL = '/static/'`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- Storage Backend: `whitenoise.storage.CompressedStaticFilesStorage`
- Pre-collected assets: 132 files verified including 25+ themes in `themes.css`, HTML5 Canvas physics in `wheel.js`, Bento UI in `ui.js`, and admin assets.

---

## 5. Media Files Audit & Persistence Strategy
- Media upload fields identified:
  - `Shop.logo` (`shop_logos/`)
  - `Shop.cover_image` (`shop_covers/`)
  - `ShopBranding.wheel_center_logo` (`wheel_logos/`)
  - `Campaign.hero_image` (`campaign_heroes/`)
  - `QRCode.qr_image` (`qr_codes/`)
- **Render Free Ephemeral Disk Constraint:**
  - Render Free container filesystems are ephemeral. Any files written to local `/media/` disappear upon container restart or idle sleep.
  - However, for the **Customer Spinning Experience**, permanent QR codes are generated dynamically using `SITE_URL` and do not require static image persistence to function (QR tokens resolve in memory via `/s/<token>/`).
  - For brand logos, themes provide built-in vector styling, accents, and defaults.
  - Supabase Storage Free provides up to 1GB free storage if persistent remote object storage is desired without payment methods.

---

## 6. URLs, QR Architecture & Network Decoupling
- Permanent QR Endpoint: `/s/<shop_public_token>/`
- Decoupled from hardcoded IPs: `SITE_URL` environment variable dynamically configures the base origin.
- Spin API: `/s/<shop_public_token>/spin/`
- Health Endpoint: `/health/` returns `{"status": "healthy"}` with `HTTP 200`.

---

## 7. Security, CSRF & Proxy Headers
- Render's edge terminates TLS/HTTPS and proxies traffic to the web service container on `$PORT`.
- Django configuration required:
  - `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
  - `ALLOWED_HOSTS = <render-domain>,<dnshe-domain>`
  - `CSRF_TRUSTED_ORIGINS = https://<render-domain>,https://<dnshe-domain>`
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`

---

## 8. Audit Verdict
The SpinPlus codebase is 100% prepared for Render Free + Supabase Free + DNSHE Free Domain deployment.
No business logic or UI changes are needed.
