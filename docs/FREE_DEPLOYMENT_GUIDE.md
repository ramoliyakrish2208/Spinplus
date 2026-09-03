# 🚀 SpinPlus — Zero-Cost Cloud Deployment Guide
**Architecture:** Render Free Web Service + Supabase Free PostgreSQL + DNSHE Free Domain  
**Total Target Cost:** Strictly ₹0 / $0 (No Credit Cards, No Debit Cards, No Billing Accounts)  

---

## 1. Architectural Blueprint
```text
Public User (HTTPS)
       │
       ▼
┌──────────────────────────────────────────┐
│  DNSHE Free Domain (e.g., spinplus.us.ci)│
│  CNAME -> spinplus.onrender.com          │
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│  Render Free Web Service                 │
│  • Auto-TLS Managed HTTPS                │
│  • Ephemeral Container ($PORT: 8000)     │
│  • Gunicorn WSGI Worker Pool             │
│  • WhiteNoise Static Serving (132 files) │
│  • Cold start sleep after 15m idle       │
└──────────────────┬───────────────────────┘
                   │
                   ▼ SSL / TLS Encrypted TCP
┌──────────────────────────────────────────┐
│  Supabase Free PostgreSQL Database       │
│  • 500 MB Persistent Relational Storage  │
│  • Atomic Locking (select_for_update)    │
│  • Multi-tenant Data Isolation           │
└──────────────────────────────────────────┘
```

---

## 2. Phase-by-Phase Execution Runbook

### Phase A: Supabase Free PostgreSQL Setup (5 Minutes)
1. In your browser, navigate to [https://supabase.com/dashboard](https://supabase.com/dashboard).
2. Click **Sign in with GitHub** or **Sign in with Google**.
3. Click **New Project**:
   - **Organization**: Choose your default organization.
   - **Name**: `spinplus-production`
   - **Database Password**: Choose a strong password (save it safely).
   - **Region**: Choose the region closest to your users (e.g., `Singapore` or `Frankfurt`).
   - **Pricing Plan**: Ensure **Free Plan** ($0/month) is selected.
   - **Important**: NEVER enter credit card information. Supabase Free requires NO payment card.
4. Click **Create new project** and wait ~2 minutes for provisioning.
5. In Project Settings > **Database** > **Connection string** > Select **URI**:
   - Copy the connection URI: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
   - Replace `[password]` with your database password.
   - This URI is your `DATABASE_URL`.

---

### Phase B: Render Free Web Service Setup (5 Minutes)
1. Push your repository to GitHub:
   ```bash
   # In terminal:
   git remote add origin https://github.com/your-username/spinplus.git
   git branch -M main
   git push -u origin main
   ```
2. In your browser, navigate to [https://dashboard.render.com/](https://dashboard.render.com/).
3. Click **Sign in with GitHub** or **Sign in with Google**.
4. Click **New +** > Select **Web Service**.
5. Connect your `spinplus` GitHub repository.
6. Configure the Service Settings:
   - **Name**: `spinplus`
   - **Region**: Oregon or Frankfurt
   - **Branch**: `main` or `deployment/free-render-supabase`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `sh scripts/entrypoint.sh`
   - **Instance Type**: Select **Free** (0.1 CPU, 512 MB RAM, $0/month).
7. Under **Environment Variables**, add:
   - `DJANGO_DEBUG`: `False`
   - `SECRET_KEY`: `<generate a random 50-character string>`
   - `DATABASE_URL`: `<paste your Supabase PostgreSQL URI>`
   - `ALLOWED_HOSTS`: `spinplus.onrender.com,spinplus.us.ci,127.0.0.1`
   - `CSRF_TRUSTED_ORIGINS`: `https://spinplus.onrender.com,https://spinplus.us.ci`
   - `SITE_URL`: `https://spinplus.onrender.com` (update to `https://spinplus.us.ci` once domain is mapped)
   - `ENABLE_HTTPS_REDIRECT`: `True`
   - `SESSION_COOKIE_SECURE`: `True`
   - `CSRF_COOKIE_SECURE`: `True`
8. Click **Create Web Service**. Render will build the image, collect static assets, run database migrations, and deploy the service.

---

### Phase C: DNSHE Free Domain Setup (5 Minutes)
1. Navigate to [https://dnshe.com/](https://dnshe.com/).
2. Search for available free domain name: `spinplus.us.ci` or `spinplus.de5.net`.
3. Register the domain (annual free renewal policy).
4. In DNS Management, add a **CNAME Record**:
   - **Host / Name**: `@` or `spinplus`
   - **Type**: `CNAME`
   - **Value / Target**: `spinplus.onrender.com`
   - **TTL**: `300` or `Auto`
5. In Render Dashboard > **Settings** > **Custom Domains**:
   - Add `spinplus.us.ci`
   - Render automatically provisions a Let's Encrypt TLS certificate for your free domain.
6. Update `SITE_URL` in Render environment variables to `https://spinplus.us.ci`.

---

## 3. Disaster Recovery & Rollback
- To run locally against SQLite:
  ```bash
  python manage.py runserver
  ```
- Local development database `db.sqlite3` is 100% untouched and preserved.
