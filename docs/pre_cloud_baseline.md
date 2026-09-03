# 📌 SpinPlus — Pre-Cloud Deployment Baseline
**Platform:** Google Cloud Starter Tier  
**Branch:** `deployment/google-starter-tier`  
**Base Commit:** `24a0c70` (`chore: baseline before Google Cloud Starter Tier preparation`)  
**Date:** September 3, 2026  

---

## 1. System & Runtime Baseline

| Component | Verified Specification |
| :--- | :--- |
| **Git Branch** | `deployment/google-starter-tier` (Clean working tree) |
| **Commit Hash** | `24a0c70` |
| **Python Version** | Python 3.11.0 (64-bit AMD64) |
| **Django Framework** | Django 5.2.9 |
| **WSGI Server** | Gunicorn 26.2.0 |
| **Image Processing** | Pillow 12.0.0 |
| **QR Code Engine** | qrcode 8.2 |
| **Static Server** | WhiteNoise 6.12.0 |
| **Local Database** | SQLite 3 with WAL Mode (`PRAGMA journal_mode=WAL`) |

---

## 2. Dependency State (`requirements.txt`)
```text
Django>=5.0.0,<6.0.0
Pillow>=10.0.0
qrcode>=7.4.2
gunicorn>=21.2.0
python-dotenv>=1.0.0
```

---

## 3. Migration State
- Command: `python manage.py makemigrations --check --dry-run`
- Output: `No changes detected`
- All 18 migrations applied and synchronized with `core/models.py`.

---

## 4. Static Collection State
- Command: `python manage.py collectstatic --noinput`
- Output: `0 static files copied to 'D:\Avadh\SpinPlus\staticfiles', 132 unmodified.`
- Total Collected Files: **132 files**
- Key Assets Verified:
  - `staticfiles/css/themes.css` (86 KB)
  - `staticfiles/js/wheel.js` (58 KB)
  - `staticfiles/js/theme-engine.js` (22 KB)
  - `staticfiles/js/ui.js` (11 KB)
  - `staticfiles/admin/` (Full Django Admin static tree)

---

## 5. Test Suite Results
- Command: `python manage.py test core`
- Result: **Ran 65 tests in 124.794s — OK (0 failures, 0 errors, 0 skipped)**
- Verified Modules:
  - `TenantIsolationTestCase` (Strict shop data isolation)
  - `SpinEngineConcurrencyTestCase` (`select_for_update()` & atomic inventory locking)
  - `CampaignLifecycleTestCase` (Date bounds & active campaign resolution)
  - `CouponRedemptionTestCase` (Single-use redemption & terminal checks)
  - `AdminSubscriptionTestCase` (Plan assignment & tier limits)

---

## 6. Safety Affirmations
1. Local `db.sqlite3` is preserved and uncorrupted.
2. Development workflow continues to support local SQLite/WAL.
3. No credentials or secrets committed.
4. Working tree is clean on `deployment/google-starter-tier`.
