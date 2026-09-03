#!/bin/bash
# ============================================================
# SpinPlus — PythonAnywhere Deployment Script
# Usage:
#   First-time / reset:  bash deploy.sh --fresh
#   Normal update:       bash deploy.sh
# ============================================================

set -e  # Exit on any error

WSGI_FILE="/var/www/spinplus_pythonanywhere_com_wsgi.py"
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$DEPLOY_DIR"

# ── Activate virtual environment ─────────────────────────────
echo ""
echo "[0/6] Activating virtual environment..."
if [ -f "$DEPLOY_DIR/venv/bin/activate" ]; then
    source "$DEPLOY_DIR/venv/bin/activate"
    echo "      ✅ Activated: $DEPLOY_DIR/venv"
elif [ -f "$HOME/.virtualenvs/spinplus/bin/activate" ]; then
    source "$HOME/.virtualenvs/spinplus/bin/activate"
    echo "      ✅ Activated: ~/.virtualenvs/spinplus"
elif [ -f "$HOME/.virtualenvs/SpinPlus/bin/activate" ]; then
    source "$HOME/.virtualenvs/SpinPlus/bin/activate"
    echo "      ✅ Activated: ~/.virtualenvs/SpinPlus"
else
    echo "      ⚠  No venv found — using system Python ($(which python))"
fi

echo ""
echo "============================================================"
echo "  SpinPlus Deployment — $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# ── 1. Pull latest code ──────────────────────────────────────
echo ""
echo "[1/6] Pulling latest code from GitHub..."
git pull origin main
echo "      ✅ Code updated → $(git log --oneline -1)"

# ── Ensure .env exists ─────────────────────────────────────────
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo ""
    echo "[!] .env not found. Creating production .env..."
    cat > "$DEPLOY_DIR/.env" << 'EOF'
SECRET_KEY=spinplus-production-secret-key-high-entropy-random-98127398127391
DJANGO_DEBUG=False
ALLOWED_HOSTS=spinplus.pythonanywhere.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://spinplus.pythonanywhere.com
SITE_URL=https://spinplus.pythonanywhere.com
ENABLE_HTTPS_REDIRECT=False
EOF
    echo "      ✅ .env created with production settings"
fi

# ── 2. Install / update dependencies ─────────────────────────
echo ""
echo "[2/6] Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "      ✅ Dependencies OK"

# ── 3. Handle --fresh flag (wipe DB for clean start) ─────────
if [[ "$1" == "--fresh" ]]; then
    echo ""
    echo "[3/6] --fresh flag detected: resetting database..."
    rm -f db.sqlite3
    echo "      ✅ Old database removed"

    python manage.py migrate
    echo "      ✅ All migrations applied"

    echo ""
    echo "      Creating superadmin account..."
    python manage.py shell -c "
from core.models import User
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@spinplus.com', 'Admin@123')
    u.role = 'super_admin'
    u.save()
    print('      ✅ Superadmin created: admin / Admin@123')
else:
    print('      ℹ  Superadmin already exists')
"
else
    # ── Normal update: 100% safe, preserves all existing data ──
    echo ""
    echo "[3/6] Safe update mode: Protecting database and applying migrations..."

    # 1. Automatic Database Snapshot Backup
    if [ -f "$DEPLOY_DIR/db.sqlite3" ]; then
        BACKUP_DIR="$DEPLOY_DIR/backups"
        mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
        cp "$DEPLOY_DIR/db.sqlite3" "$BACKUP_FILE"
        echo "      🛡️ Database snapshot created: $BACKUP_FILE"
        # Keep only the latest 5 backups to conserve disk space
        ls -t "$BACKUP_DIR"/db_backup_*.sqlite3 2>/dev/null | tail -n +6 | xargs -r rm -f
    fi

    # 2. Run migrations without touching existing data
    echo "      Running database schema migrations..."
    if python manage.py migrate --noinput; then
        echo "      ✅ Migrations applied successfully (all real data preserved)"
    else
        echo "      ❌ Migration failed! Rolling back to snapshot..."
        if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
            cp "$BACKUP_FILE" "$DEPLOY_DIR/db.sqlite3"
            echo "      ✅ Database restored from snapshot. Server remained safe."
        fi
        exit 1
    fi
fi

# ── 3.5. Ensure all SaaS Plans & Demo Merchant exist ─────────
echo ""
echo "[3.5/6] Seeding / updating SaaS plans & demoshop..."
python scripts/seed_demo_and_plans.py

# ── 4. Collect static files ───────────────────────────────────
echo ""
echo "[4/6] Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | tail -3
echo "      ✅ Static files collected"

# ── 5. Run system check ───────────────────────────────────────
echo ""
echo "[5/6] Running Django system check..."
python manage.py check --deploy 2>&1 | grep -E "^(System|ERROR|WARNING)" || true
echo "      ✅ System check done"

# ── 6. Reload web app ─────────────────────────────────────────
echo ""
echo "[6/6] Reloading web app..."
if [ -f "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "      ✅ Web app reloaded via WSGI touch"
else
    echo "      ⚠  WSGI file not found at $WSGI_FILE"
    echo "      → Please reload manually from the PythonAnywhere Web tab"
fi

echo ""
echo "============================================================"
echo "  ✅ DEPLOYMENT COMPLETE"
echo "  🌐 https://spinplus.pythonanywhere.com/"
echo "============================================================"
echo ""
