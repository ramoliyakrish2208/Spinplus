# 🚀 Spin & Win SaaS Platform — Production Deployment Guide
**Target Architecture:** Ubuntu 22.04 LTS + Nginx + Gunicorn + Django 5.x + SQLite (Always Free Tier Compatible)

---

## 📋 Table of Contents
1. [Server Provisioning (OCI / Ubuntu)](#1-server-provisioning)
2. [System Environment & Dependencies](#2-system-environment--dependencies)
3. [Project Deployment & Virtualenv](#3-project-deployment--virtualenv)
4. [Environment & Security Configuration](#4-environment--security-configuration)
5. [Database Initialization & Static Files](#5-database-initialization--static-files)
6. [Gunicorn Systemd Service](#6-gunicorn-systemd-service)
7. [Nginx Reverse Proxy & SSL (HTTPS)](#7-nginx-reverse-proxy--ssl-https)
8. [Automated Backup & Log Rotation](#8-automated-backup--log-rotation)
9. [Health Check Verification](#9-health-check-verification)
10. [Rollback & Maintenance Commands](#10-rollback--maintenance-commands)

---

## 1. Server Provisioning
Recommended Provider: **Oracle Cloud Infrastructure (OCI) Always Free** or any Ubuntu 22.04 LTS instance (Ampere A1 / AMD E2.1.Micro).
- **RAM:** 1GB–4GB (Always Free eligible)
- **Disk:** 50GB Block Storage
- **Static IP:** Attach a reserved public IP address.

---

## 2. System Environment & Dependencies
Connect to your Ubuntu server via SSH and execute:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git ufw curl sqlite3
```

---

## 3. Project Deployment & Virtualenv
Clone the project into `/var/www/SpinPlus`:

```bash
sudo mkdir -p /var/www/SpinPlus
sudo chown -R $USER:$USER /var/www/SpinPlus
git clone https://github.com/your-username/SpinPlus.git /var/www/SpinPlus
cd /var/www/SpinPlus

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Environment & Security Configuration
Create the production `.env` file:

```bash
cp .env.example .env
nano .env
```

Set production parameters:
```env
SECRET_KEY=your-custom-high-entropy-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SITE_URL=https://your-domain.com
ENABLE_HTTPS_REDIRECT=True
```

---

## 5. Database Initialization & Static Files
```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 6. Gunicorn Systemd Service
Create `/etc/systemd/system/spinplus.service`:

```ini
[Unit]
Description=Spin & Win SaaS Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/SpinPlus
ExecStart=/var/www/SpinPlus/venv/bin/gunicorn --config /var/www/SpinPlus/gunicorn.conf.py spinplus.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl enable spinplus
sudo systemctl start spinplus
sudo systemctl status spinplus
```

---

## 7. Nginx Reverse Proxy & SSL (HTTPS)
Create Nginx configuration `/etc/nginx/sites-available/spinplus`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/SpinPlus/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /var/www/SpinPlus/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Enable site and configure Let's Encrypt SSL:
```bash
sudo ln -s /etc/nginx/sites-available/spinplus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL Certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 8. Automated Backup & Log Rotation
Set up a daily SQLite backup cron job:

```bash
crontab -e
```
Add the line:
```cron
0 3 * * * /var/www/SpinPlus/venv/bin/python /var/www/SpinPlus/scripts/backup_sqlite.py >> /var/www/SpinPlus/logs/backup.log 2>&1
```

---

## 9. Health Check Verification
Verify endpoint health:
```bash
curl -I https://your-domain.com/health/
# Returns HTTP 200 OK with {"status": "healthy"}
```

---

## 10. Rollback & Maintenance Commands
- **Restart Application:** `sudo systemctl restart spinplus`
- **View Live Application Logs:** `tail -f /var/www/SpinPlus/logs/spinplus.log`
- **Restore SQLite Backup:** `cp /var/www/SpinPlus/backups/spinplus_backup_YYYYMMDD_HHMMSS.sqlite3 /var/www/SpinPlus/db.sqlite3`
