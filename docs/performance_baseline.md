# SpinPlus — Performance Baseline Report

**Execution Timestamp:** 2026-09-03 20:07:18 IST  
**Environment:** Local Development (Windows 11 / Python 3.11.9 / Django 5.0.3)  
**Database:** SQLite 3 (WAL mode enabled)

---

## 1. Automated Test Suite Baseline
| Metric | Baseline Value |
| :--- | :--- |
| **Total Test Cases** | 65 |
| **Passing Tests** | 65 (100%) |
| **Failing Tests** | 0 |
| **Errors** | 0 |
| **Django System Check (`python manage.py check`)** | 0 issues |
| **Django Deploy Check (`check --deploy`)** | 1 warning (`SECURE_SSL_REDIRECT`) |
| **Migrations Dry-Run (`makemigrations --check`)** | 0 pending changes |

---

## 2. Endpoint Latency & Database Query Counts
| Critical Endpoint | Route | Status Code | Latency (ms) | Query Count |
| :--- | :--- | :--- | :--- | :--- |
| **Customer QR Landing** | `/s/<token>/` | 200 OK | 155.69 ms | 17 queries |
| **Public Coupon View** | `/coupon/<token>/` | 200 OK | 11.12 ms | 6 queries |
| **Shop Owner Dashboard** | `/dashboard/shop/` | 200 OK | 21.98 ms | 21 queries |
| **Campaign Management List** | `/dashboard/shop/campaigns/` | 200 OK | 10.37 ms | 9 queries |
| **Billing & Upgrade Center** | `/dashboard/billing/` | 200 OK | 16.99 ms | 13 queries |
| **Super Admin Capacity** | `/dashboard/admin/capacity/` | 200 OK | 12.80 ms | 13 queries |

---

## 3. Initial Identified Bottlenecks & Audit Findings
1. **Customer QR Landing View (`public_shop_view`)**:
   - Executes 17 queries per request due to separate queries for `Shop`, `ShopBranding`, `Campaign`, `Prize` filter, `SpinResult` check, and repeated context processor theme lookups.
   - Target: Reduce to ≤ 6 queries via `select_related()` and cached theme defaults.
2. **Shop Owner Dashboard (`shop_dashboard`)**:
   - Executes 21 queries on every load calculating aggregate stats, active campaign, prize counts, and recent spins without batching.
   - Target: Reduce to ≤ 8 queries using consolidated aggregation.
3. **System Capacity Dashboard**:
   - Relies on static fallback numbers (e.g. 25 sessions, 21.25 RPS, 5000 spins/day).
   - Lacks runtime platform detection (`LOCAL` vs `PYTHONANYWHERE` vs `RENDER` vs `CLOUD`).
   - Needs empirical live server telemetry and real benchmark execution with automatic cleanup.
