# ⚠️ Free Cloud Deployment Limitations & Operational Disclosures
**Platform Stack:** Render Free + Supabase Free + DNSHE Free  

---

## 1. Mandatory Free Tier Operational Disclosures

### A. Render Free Web Service
1. **Idle Spin-Down (Cold Starts):**
   - Render Free services automatically spin down after 15 minutes of inactivity.
   - When a customer scans a QR code after an idle period, the first incoming HTTP request takes **30 to 50 seconds** to wake up the container.
   - Subsequent requests are served immediately with low latency (~50ms–150ms).
2. **Bandwidth & Compute Limits:**
   - Free plan provides 0.1 vCPU and 512 MB RAM.
   - Monthly free outbound bandwidth: 100 GB.
3. **No Persistent Local Disk:**
   - The container filesystem is completely ephemeral. Files written to local disk are wiped on sleep/redeploy.
   - The authoritative business database is safely hosted on Supabase, completely decoupled from Render's disk.

---

### B. Supabase Free PostgreSQL
1. **Inactivity Pausing:**
   - Free tier Supabase projects pause after 7 days of total inactivity.
   - Unpausing takes ~2 minutes via the Supabase dashboard.
2. **Capacity Quotas:**
   - Database storage: 500 MB (sufficient for ~200,000 spin transactions and coupons).
   - Egress bandwidth: 5 GB / month.

---

### C. DNSHE Free Domain
1. **Annual Renewal:**
   - Under current policy, free domains are valid for 1 year.
   - Free renewal is available within 180 days before expiration via the DNSHE console.
   - Ensure the domain continues to be used for legitimate SpinPlus SaaS operations.
