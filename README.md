# Spin & Win — Multi-Tenant Promotional SaaS Platform

Spin & Win is a multi-tenant promotional wheel-of-fortune platform built with **Django 5.2**, **Vanilla CSS custom properties**, and **HTML5 High-DPI Canvas**. It empowers retail shops and businesses to create custom seasonal offers accessible via permanent QR codes.

---

## 🌟 Key Platform Features

- **Multi-Tenant SaaS Architecture**: Independent Shop Owners, Super Admin oversight, strict tenant data isolation.
- **Permanent QR Architecture (`/s/<public_token>/`)**: Customer QR stickers never change when seasonal campaigns update.
- **Production Spin Engine**: Deterministic server-side prize selection, session spin cooldowns (`HTTP 429`), atomic inventory locks (`select_for_update`).
- **Interactive Shop Onboarding Wizard**: Guided 4-step setup for new shop owners.
- **SaaS Tier Billing & Usage**: Real-time meters for active campaigns, prize limits, and spin volume.
- **Campaign Preview Engine (`is_preview`)**: Safe customer experience wheel preview mode without inventory consumption.
- **Health Check & Monitoring (`GET /health/`)**: Production health status endpoint checking DB connectivity.

---

## 🚀 Quick Start Guide

### 1. Requirements & Setup
```bash
git clone https://github.com/your-org/spinplus.git
cd spinplus
python -m venv venv
venv\Scripts\activate
pip install django pillow
```

### 2. Environment Configuration
Copy environment configuration template:
```bash
cp .env.example .env
```

### 3. Database Initialization & Seed Data
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 4. Running Development Server
```bash
python manage.py runserver 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🧪 Testing & Verification

Run Django system checks and automated test suite:
```bash
python manage.py check
python manage.py test core
```

Run deployment security checks:
```bash
python manage.py check --deploy
```

---

## 📜 Deployment & Operations

For Gunicorn, Nginx, SSL, and backup configuration, refer to [DEPLOYMENT.md](file:///d:/Avadh/SpinPlus/DEPLOYMENT.md).
