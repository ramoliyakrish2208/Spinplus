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
    # ── Normal migration (preserve existing data) ─────────────
    echo ""
    echo "[3/6] Running database migrations..."
    python manage.py migrate
    echo "      ✅ Migrations applied"
fi

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
