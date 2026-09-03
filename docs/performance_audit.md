# SpinPlus — Complete Codebase Audit Report

**Audit Date:** 2026-09-03  
**Auditor:** Senior Django Architect & Performance/Security Engineering  
**Scope:** Architecture, Database Queries, Security, Privacy, Frontend, Spinner, and Capacity Engine

---

## 1. Executive Summary
The SpinPlus application has a robust architectural foundation with strong tenant isolation principles, server-authoritative spin mechanics, and an accessible Bento Design System. However, several optimization opportunities exist across query efficiency, static caching, canvas animation lifecycle, and system capacity reporting.

---

## 2. Detailed Findings by Domain

### A. Database & Query Patterns (N+1 & Redundancy)
1. **`public_shop_view` (Customer QR Landing)**:
   - Queries `Shop` by `public_token`, then separately queries `ShopBranding`, then queries `Campaign`, then queries `Prize` list, then queries `Subscription`, then context processor re-queries `Shop` and `ShopBranding`.
   - **Fix**: Use `Shop.objects.select_related('subscription', 'branding').prefetch_related('campaigns__prizes')` to collapse 17 queries into 3-4 queries.
2. **`shop_dashboard`**:
   - Queries total spins, total coupons, active campaigns, pending requests, and notifications across separate individual `count()` queries.
   - **Fix**: Consolidate statistics using conditional annotations and batch queries.
3. **Database Indexes**:
   - Verify indexes on foreign keys and lookup tokens:
     - `Shop.public_token` (Already indexed/unique)
     - `Coupon.verify_token` (Already indexed/unique)
     - `Subscription.status` (Missing index)
     - `Subscription.future_starts_at` (Missing index)
     - `Campaign.is_active` (Missing index)

### B. Security & Tenant Isolation
1. **Tenant Isolation**:
   - All tenant views enforce `@shop_access_required` and query `shop=request.user.shop` or `actor=request.user`. IDOR checks are properly structured.
2. **Server-Authoritative Spins**:
   - `spin_service.py` strictly executes prize calculation server-side with `transaction.atomic()` and `select_for_update()`. Probability cannot be altered by client scripts.
3. **Rate Limiting**:
   - Rate limiters exist for spins (`spin_rate_limiter`), coupon generation, and logins (`login_rate_limiter`). Ensure IP and session token fallbacks are consistent.

### C. Privacy & Data Minimization
1. **Customer Exposure**:
   - Customer landing pages (`/s/<token>/`) and public coupon views (`/coupon/<token>/`) never expose shop owner emails, passwords, phone numbers, or administrative metrics.
2. **Infrastructure Privacy**:
   - Super admin system capacity metrics (CPU, RAM, disk, database path) are strictly protected by `@superadmin_required`. No infrastructure telemetry is exposed publicly.

### D. Frontend, Canvas Spinner & Particle Engine
1. **Canvas Spinner (`static/js/wheel.js`)**:
   - Spinner redraws segments on requestAnimationFrame during active spin.
   - **Optimization**: Ensure geometry calculations (trigonometry, segment arc angles, slice path definitions) are cached rather than recalculated on every single tick.
   - Clean lifecycle: ensure `cancelAnimationFrame` is called immediately when the wheel stops or the tab is hidden.
2. **Particle Effects (`static/js/particles.js`)**:
   - Ensure particle count scales adaptively based on device pixel ratio and paused when `document.hidden == true`.

### E. System Capacity Engine (`admin_capacity_dashboard_view`)
1. **Legacy Hardcoded Fallbacks**:
   - Currently, if `benchmark_results.json` is missing or incomplete, the dashboard displays fallback constants (25 sessions, 21.25 RPS, 5000 spins/day).
   - **Requirement**: Replace with real-time environment detection (`LOCAL` vs `PYTHONANYWHERE` vs `RENDER` vs `CLOUD`) and live hardware telemetry (`psutil` CPU/RAM/Disk and real database ping latency).
2. **Benchmark Teardown Guarantee**:
   - Benchmarking suite must operate in a dedicated namespace (`CAPTEST_`) and automatically clean up all generated test records, leaving 0 leftover rows in the database.

---

## 3. Recommended Optimization Priorities
1. **Collapsing Customer QR Landing Queries**: Reduce query count from 17 to ≤ 5 to achieve sub-50ms TTFB.
2. **Real-Time Capacity Telemetry**: Implement dynamic environment detector and live system hardware profiler.
3. **Automated Clean Benchmark Engine**: Build Super Admin benchmark runner with guaranteed test record teardown.
4. **Static Caching**: Cache theme definitions and static branding in memory with invalidation signals.
