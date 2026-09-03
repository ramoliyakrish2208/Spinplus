# 🌐 Oracle Cloud Infrastructure (OCI) Always Free — SpinPlus Production Deployment Guide

This guide provides step-by-step instructions for deploying the **SpinPlus Django SaaS Platform** onto an **Oracle Cloud Infrastructure (OCI) Always Free** Ubuntu 22.04 LTS instance.

---

## 📑 Table of Contents
1. [Overview & Architecture](#1-overview--architecture)
2. [OCI Cloud Infrastructure Setup (Web Console)](#2-oci-cloud-infrastructure-setup-web-console)
   - [A. Compartment Setup](#a-compartment-setup)
   - [B. Virtual Cloud Network (VCN) & Ingress Rules](#b-virtual-cloud-network-vcn--ingress-rules)
   - [C. Provision Compute Instance](#c-provision-compute-instance)
   - [D. Reserve Static Public IP](#d-reserve-static-public-ip)
3. [Server Access & Ubuntu OS Preparation](#3-server-access--ubuntu-os-preparation)
   - [A. SSH Connection](#a-ssh-connection)
   - [B. System Update & Dependencies](#b-system-update--dependencies)
   - [C. Crucial: OCI Ubuntu Firewall (iptables / UFW) Fix](#c-crucial-oci-ubuntu-firewall-iptables--ufw-fix)
4. [Application Setup](#4-application-setup)
   - [A. Application Directory & User Permissions](#a-application-directory--user-permissions)
   - [B. Code Deployment](#b-code-deployment)
   - [C. Python Virtual Environment & Dependencies](#c-python-virtual-environment--dependencies)
   - [D. Environment Configuration (.env)](#d-environment-configuration-env)
   - [E. Database Migration & SQLite WAL Verification](#e-database-migration--sqlite-wal-verification)
   - [F. Static Files Collection](#f-static-files-collection)
5. [Process Management (Systemd & Gunicorn)](#5-process-management-systemd--gunicorn)
6. [Nginx Reverse Proxy & SSL (HTTPS)](#6-nginx-reverse-proxy--ssl-https)
7. [Automated Disaster Recovery (Daily SQLite WAL Backup)](#7-automated-disaster-recovery-daily-sqlite-wal-backup)
8. [End-to-End Verification](#8-end-to-end-verification)
9. [Comprehensive Troubleshooting Guide](#9-comprehensive-troubleshooting-guide)
10. [Manual Execution Checklist](#10-manual-execution-checklist)

---

## 1. Overview & Architecture

```text
Public User Request (HTTPS :443)
           │
           ▼
┌──────────────────────────────────────────┐
│  OCI Virtual Cloud Network (VCN)         │
│  Ingress Rules: Ports 22, 80, 443        │
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│  OCI Ubuntu 22.04 LTS Compute Instance   │
│                                          │
│  [iptables / UFW Firewall]               │
│  Allows :22 (SSH), :80 (HTTP), :443 (SSL)│
│                   │                      │
│                   ▼                      │
│  [Nginx Reverse Proxy]                   │
│  • Terminates TLS/HTTPS (Certbot)        │
│  • Serves /static/ & /media/ directly    │
│  • Blocks .env, .git, db.sqlite3, *.py   │
│  • Forbids script execution in uploads   │
│                   │                      │
│                   ▼ (Private Loopback)   │
│  [Gunicorn WSGI Application Server]      │
│  • Bound to 127.0.0.1:8000               │
│  • Managed by systemd (spinplus.service) │
│  • Runs as non-root user (www-data)      │
│                   │                      │
│                   ▼                      │
│  [Django Core Application (SpinPlus)]    │
│  • Tenant isolation & Campaign engine    │
│  • SQLite WAL High-Concurrency Database  │
└──────────────────────────────────────────┘
```

---

## 2. OCI Cloud Infrastructure Setup (Web Console)

### What Each OCI Resource Does
- **Compartment**: A logical container that isolates your SpinPlus cloud resources for security and organization.
- **Virtual Cloud Network (VCN)**: A virtual private software-defined network in Oracle Cloud.
- **Subnet**: A subdivision of the VCN where your compute instance resides.
- **Security List / Ingress Rules**: Virtual firewall rules in OCI that allow or block internet traffic before it reaches your VM.
- **Compute Instance**: The actual virtual server (CPU, RAM, Disk) running Ubuntu 22.04 LTS.
- **Reserved Public IP**: A permanent public IP address attached to your server that never changes on reboots.

---

### A. Compartment Setup
1. Log into your **Oracle Cloud Console**.
2. Navigate to **Identity & Security** > **Compartments**.
3. Use the default root compartment or click **Create Compartment** (e.g., `SpinPlus-Production`).

---

### B. Virtual Cloud Network (VCN) & Ingress Rules
1. Navigate to **Networking** > **Virtual Cloud Networks**.
2. Click **Start VCN Wizard** > Select **Create VCN with Internet Connectivity** > Click **Start VCN Wizard**.
3. Name: `spinplus-vcn`.
4. Leave CIDR blocks default (`10.0.0.0/16` for VCN, `10.0.0.0/24` for Public Subnet).
5. Click **Next** > **Create**.
6. Once created, click on `spinplus-vcn` > Click **Security Lists** > Click **Default Security List for spinplus-vcn**.
7. Under **Ingress Rules**, click **Add Ingress Rules** to open ports **80** and **443**:

| Source Type | Source CIDR | IP Protocol | Source Port Range | Destination Port Range | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CIDR | `0.0.0.0/0` | TCP | All | `80` | Allow HTTP traffic |
| CIDR | `0.0.0.0/0` | TCP | All | `443` | Allow HTTPS traffic |
| CIDR | `0.0.0.0/0` | TCP | All | `22` | (Already present by default) |

---

### C. Provision Compute Instance
1. Navigate to **Compute** > **Instances** > Click **Create Instance**.
2. **Name**: `spinplus-server`.
3. **Compartment**: Select your compartment.
4. **Placement**: Choose any Availability Domain.
5. **Image and Shape**:
   - **Image**: Click **Change Image** > Select **Canonical Ubuntu** > Choose **Ubuntu 22.04 Minimal** or **Ubuntu 22.04**.
   - **Shape**: Click **Change Shape** > Select **Ampere (ARM)** (`VM.Standard.A1.Flex`) with 2–4 OCPUs and 12–24 GB RAM (Always Free Eligible) **OR** **AMD** (`VM.Standard.E2.1.Micro`) with 1 OCPU and 1 GB RAM.
6. **Networking**:
   - Select your existing `spinplus-vcn` and **Public Subnet**.
   - Ensure **Assign a public IPv4 address** is selected.
7. **Add SSH Keys**:
   - Select **Generate a key pair for me** and click **Save private key** (save as `spinplus_key.key` on your computer) **OR** select **Upload public key** and provide your existing `id_rsa.pub`.
8. **Boot Volume**: Default 50 GB is Always Free eligible.
9. Click **Create** and wait 60–90 seconds until status changes from *PROVISIONING* to *RUNNING*.

---

### D. Reserve Static Public IP
1. In the instance details page, under **Resources** (bottom left), click **Attached VNICs**.
2. Click the VNIC name > Click **IPv4 Addresses**.
3. Click the three dots on the assigned address > Select **Edit**.
4. Change from *Ephemeral* to **Reserved Public IP** > Click **Create a New Reserved IP** > Save.
5. Note your **Public IP Address** (referred to in this guide as `YOUR_OCI_PUBLIC_IP`).

---

## 3. Server Access & Ubuntu OS Preparation

### A. SSH Connection
On your local machine (Terminal / PowerShell):
```bash
# Set secure file permissions on your private key (Linux/macOS)
chmod 400 spinplus_key.key

# Connect as ubuntu user
ssh -i spinplus_key.key ubuntu@YOUR_OCI_PUBLIC_IP
```

---

### B. System Update & Dependencies
Once logged into your Ubuntu instance:
```bash
# 1. Update package indices and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# 2. Install all required runtime dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    sqlite3 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    iptables-persistent
```

---

### C. Crucial: OCI Ubuntu Firewall (iptables / UFW) Fix
> [!IMPORTANT]
> **OCI CRITICAL GOTCHA**: OCI Ubuntu images include default host-level `iptables` rules that **reject** incoming traffic on ports 80 and 443 even when allowed in the OCI Security List. You MUST run the following commands on the server:

# Open Ports 80 and 443 in the host iptables firewall
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Save iptables rules so they persist across server reboots
sudo netfilter-persistent save

# If using UFW (Uncomplicated Firewall), also allow SSH, HTTP, and HTTPS:
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

*Verification:*
```bash
# Verify iptables:
sudo iptables -L INPUT -n --line-numbers | grep -E "dpt:(80|443)"

# Verify UFW status:
sudo ufw status verbose
```
Expected output: Shows ACCEPT rules for `dpt:80` and `dpt:443`, and UFW status shows `22/tcp`, `80/tcp`, and `443/tcp` ALLOWED.

---

## 4. Application Setup

### A. Application Directory & User Permissions
```bash
# Create target web root
sudo mkdir -p /var/www/spinplus

# Assign temporary ownership to ubuntu user for deployment
sudo chown -R ubuntu:www-data /var/www/spinplus
sudo chmod -R 775 /var/www/spinplus
```

---

### B. Code Deployment
Clone or copy your SpinPlus repository into `/var/www/spinplus`:
```bash
cd /var/www/spinplus

# Option A: Clone from private/public Git repository
git clone https://github.com/your-username/SpinPlus.git .

# Option B: Or copy files via SCP from your local machine:
# scp -i spinplus_key.key -r /path/to/SpinPlus/* ubuntu@YOUR_OCI_PUBLIC_IP:/var/www/spinplus/
```

---

### C. Python Virtual Environment & Dependencies
```bash
cd /var/www/spinplus

# Create virtual environment
python3 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt
```

*Verification:*
```bash
pip check
```
Expected output: `No broken requirements found.`

---

### D. Environment Configuration (.env)
```bash
cd /var/www/spinplus
cp .env.example .env
nano .env
```

Populate the `.env` file with your production parameters:
```dotenv
SECRET_KEY=generate-a-random-50-character-string-here
DJANGO_DEBUG=False
SITE_URL=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_OCI_PUBLIC_IP,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
X_FRAME_OPTIONS=DENY
```

Secure the `.env` file permissions:
```bash
sudo chmod 600 /var/www/spinplus/.env
sudo chown www-data:www-data /var/www/spinplus/.env
```

---

### E. Database Migration & SQLite WAL Verification
```bash
cd /var/www/spinplus
source venv/bin/activate

# Apply migrations
python manage.py migrate

# Create initial super admin account
python manage.py createsuperuser

# Seed default stores (optional)
# python scripts/seed_production_shops.py
```

*Verify SQLite WAL mode:*
```bash
sqlite3 /var/www/spinplus/db.sqlite3 "PRAGMA journal_mode;"
```
Expected output: `wal`.

---

### F. Static Files Collection
```bash
cd /var/www/spinplus
source venv/bin/activate

# Collect all static files to /var/www/spinplus/staticfiles
python manage.py collectstatic --noinput
```

*Verify collection:*
```bash
ls -l /var/www/spinplus/staticfiles/css/themes.css
```
Expected output: File exists and is readable.

---

## 5. Process Management (Systemd & Gunicorn)

### Install the Systemd Service
```bash
# 1. Copy service configuration to systemd directory
sudo cp /var/www/spinplus/deployment/spinplus.service /etc/systemd/system/spinplus.service

# 2. Assign production ownership to www-data
sudo chown -R www-data:www-data /var/www/spinplus

# 3. Reload systemd daemon
sudo systemctl daemon-reload

# 4. Enable automatic start on boot
sudo systemctl enable spinplus

# 5. Start the service
sudo systemctl start spinplus

# 6. Check status
sudo systemctl status spinplus
```

*Verification:*
```bash
curl -I http://127.0.0.1:8000/health/
```
Expected output: `HTTP/1.1 200 OK` with JSON `{"status": "healthy", ...}`.

---

## 6. Nginx Reverse Proxy & SSL (HTTPS)

### A. Deploy Nginx Configuration
```bash
# 1. Copy Nginx site configuration
sudo cp /var/www/spinplus/deployment/nginx_spinplus.conf /etc/nginx/sites-available/spinplus

# 2. Enable site via symlink
sudo ln -s /etc/nginx/sites-available/spinplus /etc/nginx/sites-enabled/

# 3. Remove default Nginx welcome site
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Edit server_name to match your real domain
sudo nano /etc/nginx/sites-available/spinplus
```
*Change `yourdomain.com www.yourdomain.com;` to your real domain (e.g. `spinwin.in www.spinwin.in;`).*

```bash
# 5. Test syntax
sudo nginx -t

# 6. Reload Nginx
sudo systemctl reload nginx
```

---

### B. Obtain Let's Encrypt SSL/TLS Certificate (Certbot)
Ensure your domain's DNS `A` records point to `YOUR_OCI_PUBLIC_IP`.
```bash
# Run Certbot to acquire SSL and automatically configure HTTPS in Nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

*Verify automatic certificate renewal:*
```bash
sudo certbot renew --dry-run
```
Expected output: `Congratulations, all simulated renewals succeeded!`

---

## 7. Automated Disaster Recovery (Daily SQLite WAL Backup)

Set up a daily automated backup using SQLite's online backup API:
```bash
# Ensure backups directory exists with correct ownership
sudo mkdir -p /var/www/spinplus/backups
sudo chown -R www-data:www-data /var/www/spinplus/backups

# Add cron job under www-data user
sudo crontab -u www-data -e
```
Add the following line to schedule daily backup at 03:00 AM:
```cron
0 3 * * * /var/www/spinplus/venv/bin/python /var/www/spinplus/scripts/backup_sqlite.py >> /var/www/spinplus/logs/backup.log 2>&1
```

---

## 8. End-to-End Verification

Execute the following verification suite from outside the server (e.g. your local terminal):

```bash
# 1. Health check over HTTPS
curl -I https://yourdomain.com/health/
# Expected: HTTP/2 200 OK

# 2. Permanent QR resolution test
curl -I https://yourdomain.com/s/<shop_public_token>/
# Expected: HTTP/2 200 OK

# 3. Static CSS asset delivery test
curl -I https://yourdomain.com/static/css/themes.css
# Expected: HTTP/2 200 OK, cache-control: public

# 4. Security isolation test (.env blocking)
curl -I https://yourdomain.com/.env
# Expected: HTTP/2 404 Not Found (blocked by Nginx)

# 5. Security isolation test (db.sqlite3 blocking)
curl -I https://yourdomain.com/db.sqlite3
# Expected: HTTP/2 404 Not Found (blocked by Nginx)
```

---

## 9. Comprehensive Troubleshooting Guide

### 1. SSH Connection Timeout / Connection Refused
- **Cause**: OCI Security List does not have an ingress rule for Port 22, or you are using the wrong username/key.
- **Fix**:
  1. In OCI Console > VCN > Security Lists, ensure an Ingress Rule exists for Port 22 with Source `0.0.0.0/0`.
  2. Verify login user: Ubuntu images **always** use user `ubuntu` (not `root` or `admin`).
  3. Verify key permissions: `chmod 400 spinplus_key.key`.

---

### 2. Port 80 / 443 Unreachable from the Internet (Connection Timed Out)
- **Cause**: OCI host-level `iptables` rules are dropping traffic before it reaches Nginx.
- **Fix**:
  Run on the server:
  ```bash
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
  sudo netfilter-persistent save
  ```

---

### 3. Nginx 502 Bad Gateway
- **Cause**: Gunicorn is not running or crashed on startup.
- **Fix**:
  Check systemd status and real-time logs:
  ```bash
  sudo systemctl status spinplus
  sudo journalctl -u spinplus -n 50 --no-pager
  ```
  Common causes: Missing environment variables in `.env`, virtualenv path typo, or missing dependency.

---

### 4. Django 400 Bad Request
- **Cause**: The incoming `Host` header does not match any entry in `ALLOWED_HOSTS`.
- **Fix**:
  Edit `/var/www/spinplus/.env` and add your exact domain and public IP to `ALLOWED_HOSTS`:
  ```dotenv
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_OCI_PUBLIC_IP,127.0.0.1
  ```
  Restart service: `sudo systemctl restart spinplus`.

---

### 5. CSRF Verification Failed / Origin Insecure
- **Cause**: Request scheme was forwarded over HTTP internally or `CSRF_TRUSTED_ORIGINS` is missing the HTTPS origin.
- **Fix**:
  Ensure `/var/www/spinplus/.env` has:
  ```dotenv
  CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```
  Ensure Nginx has `proxy_set_header X-Forwarded-Proto $scheme;`.

---

### 6. SQLite Permission Denied / Database is Locked
- **Cause**: The `www-data` user does not have write permissions to `db.sqlite3` **or** to the parent directory `/var/www/spinplus/` (SQLite WAL mode requires creating `-wal` and `-shm` files in the directory).
- **Fix**:
  ```bash
  sudo chown -R www-data:www-data /var/www/spinplus
  sudo chmod 664 /var/www/spinplus/db.sqlite3*
  sudo chmod 775 /var/www/spinplus
  sudo systemctl restart spinplus
  ```

---

## 10. Manual Execution Checklist

Use this checklist to track your manual steps in OCI:

- [ ] **OCI Console**: Create compartment `SpinPlus-Production`
- [ ] **OCI Console**: Create VCN `spinplus-vcn` with Internet Connectivity
- [ ] **OCI Console**: Add Ingress Rules for Ports **80** (HTTP) and **443** (HTTPS) in Default Security List
- [ ] **OCI Console**: Launch Ubuntu 22.04 instance with downloaded SSH private key
- [ ] **OCI Console**: Attach a Reserved Public IP to the instance VNIC
- [ ] **DNS Registrar**: Point `A` records (`@` and `www`) to `YOUR_OCI_PUBLIC_IP`
- [ ] **Server SSH**: Log in: `ssh -i spinplus_key.key ubuntu@YOUR_OCI_PUBLIC_IP`
- [ ] **Server Firewall**: Run OCI `iptables` fix for Ports 80 & 443 and save via `netfilter-persistent save`
- [ ] **Server APT**: Install Python 3, pip, venv, sqlite3, nginx, certbot, and libraries
- [ ] **Server Code**: Deploy repository to `/var/www/spinplus`
- [ ] **Server Environment**: Create `/var/www/spinplus/.env` (`chmod 600`) with custom `SECRET_KEY` and domains
- [ ] **Server Django**: Run `python manage.py migrate` and `collectstatic`
- [ ] **Server Systemd**: Install `spinplus.service`, enable, and start service
- [ ] **Server Nginx**: Install `nginx_spinplus.conf`, test with `nginx -t`, and reload
- [ ] **Server Certbot**: Execute `sudo certbot --nginx -d yourdomain.com`
- [ ] **Verification**: Confirm `https://yourdomain.com/health/` returns `HTTP 200 OK`
- [ ] **Verification**: Confirm `https://yourdomain.com/.env` returns `HTTP 404`
