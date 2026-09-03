# Spin & Win SaaS Platform — Production Deployment Guide

> **Cloud Infrastructure Setup**: For complete Oracle Cloud Infrastructure step-by-step console instructions, see the dedicated [OCI Always Free Deployment Guide](file:///d:/Avadh/SpinPlus/docs/OCI_DEPLOYMENT_GUIDE.md).

## 1. Environment & Dependency Manifest (Ubuntu 22.04 LTS)

### A. Required System / Ubuntu 22.04 Packages (APT)
Run on the Ubuntu server before setting up Python virtual environment:
```bash
sudo apt update && sudo apt install -y \
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
    curl
```

### B. Required Python Runtime Dependencies (`requirements.txt`)
Install into the project virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
Contents of `requirements.txt`:
- `Django>=5.0.0,<6.0.0` — Core web framework & ORM
- `Pillow>=10.0.0` — Image processing (shop logos, wheel center art, poster assets)
- `qrcode>=7.4.2` — Dynamic QR code generator
- `gunicorn>=21.2.0` — Production WSGI application server
- `python-dotenv>=1.0.0` — Production `.env` environment loading

### C. Optional Development & Benchmark Dependencies
Only needed when running local benchmarks or load stress tests:
- `requests` (used by `scripts/load_test.py`)

---

## 2. Step-by-Step Production Setup

### Step 1: Environment Configuration
Copy `.env.example` to `.env` and configure production secrets:
```bash
cp .env.example .env
nano .env
```
Key production variables:
- `SECRET_KEY`: High-entropy random string (at least 50 chars).
- `DJANGO_DEBUG`: Keep `False`.
- `ALLOWED_HOSTS`: Domain names (e.g. `yourdomain.com,www.yourdomain.com`).
- `CSRF_TRUSTED_ORIGINS`: Comma-separated HTTPS origins (e.g. `https://yourdomain.com`).
- `SITE_URL`: Base domain (e.g. `https://yourdomain.com`).
- `SECURE_SSL_REDIRECT`: `True` (forces HTTPS).

### Step 2: Database Migration & Static Files
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 3: Gunicorn WSGI Execution & Systemd Service
The Gunicorn entry point is `spinplus.wsgi:application`.

Copy the verified systemd service file to `/etc/systemd/system/spinplus.service`:
```bash
sudo cp /var/www/spinplus/deployment/spinplus.service /etc/systemd/system/spinplus.service
```

Service file definition (`/etc/systemd/system/spinplus.service`):
```ini
[Unit]
Description=SpinPlus Django SaaS Platform (Gunicorn WSGI)
After=network.target

[Service]
Type=simple

# Run as dedicated non-root production user
User=www-data
Group=www-data

# Production Working Directory & Virtual Environment
WorkingDirectory=/var/www/spinplus
Environment="PATH=/var/www/spinplus/venv/bin"

# Securely load environment variables from protected .env file (chmod 600)
EnvironmentFile=/var/www/spinplus/.env

# Gunicorn Execution strictly on localhost loopback via config file
ExecStart=/var/www/spinplus/venv/bin/gunicorn spinplus.wsgi:application \
    --config /var/www/spinplus/gunicorn.conf.py

# Automatic Restart & Failure Recovery
Restart=always
RestartSec=5s
KillMode=mixed
TimeoutStopSec=30

# Security Isolation
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

#### Secure Permissions Setup
```bash
# Assign ownership to www-data non-root user
sudo chown -R www-data:www-data /var/www/spinplus

# Protect environment secrets (read-write only for owner)
sudo chmod 600 /var/www/spinplus/.env

# Ensure SQLite database & WAL files are writable by www-data
sudo chmod 664 /var/www/spinplus/db.sqlite3*
sudo chmod 775 /var/www/spinplus /var/www/spinplus/media
```

#### Systemd Management Commands
```bash
# Reload systemd manager configuration
sudo systemctl daemon-reload

# Enable service to start automatically on system boot
sudo systemctl enable spinplus

# Start service
sudo systemctl start spinplus

# Restart service (after code updates)
sudo systemctl restart spinplus

# Check service status and health
sudo systemctl status spinplus

# Inspect real-time service logs
sudo journalctl -u spinplus -f

# View last 100 log entries
sudo journalctl -u spinplus -n 100 --no-pager
```
### Step 4: Nginx Reverse Proxy Configuration
Copy the production Nginx configuration file:
```bash
sudo cp /var/www/spinplus/deployment/nginx_spinplus.conf /etc/nginx/sites-available/spinplus
sudo ln -s /etc/nginx/sites-available/spinplus /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

Edit the domain names to match your registered domain:
```bash
sudo nano /etc/nginx/sites-available/spinplus
# Replace 'yourdomain.com' and 'www.yourdomain.com' with your actual domain
```

#### Step 4A: Test Nginx Configuration Syntax
```bash
sudo nginx -t
```

#### Step 4B: Reload Nginx
```bash
sudo systemctl reload nginx
```

#### Step 4C: Obtain SSL/TLS Certificate (Certbot)
After DNS A records point to your Ubuntu server IP:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Certbot will automatically install TLS certificates and configure the HTTPS redirect in Nginx.

#### Step 4D: Verify Automated SSL Renewal
```bash
sudo certbot renew --dry-run
```

---

## 3. Database Backup & Disaster Recovery

### Automated Daily Database Backup Script (`backup_db.sh`)
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/spinplus"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
sqlite3 /var/www/spinplus/db.sqlite3 ".backup '$BACKUP_DIR/db_$TIMESTAMP.sqlite3'"
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +14 -exec rm {} \;
```

---

## 4. Health & Status Checks

- **Health Endpoint**: `GET /health/` -> returns HTTP 200 `{"status": "healthy", "database": "connected"}`.
- **Django Security Deployment Check**:
```bash
python manage.py check --deploy
```
