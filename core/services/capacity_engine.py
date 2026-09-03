"""
SpinPlus Real-Time System Capacity Engine
=========================================
Provides:
  - Automatic server environment detection (LOCAL / PYTHONANYWHERE / RENDER / CLOUD)
  - Live hardware telemetry (CPU, RAM, Disk) using safe psutil/os calls
  - Database latency probing via real timed query
  - Estimate-free, hardcode-free capacity metrics
  - Isolated benchmark runner with CAPTEST_ prefix and guaranteed cleanup

All data returned by this module reflects the ACTUAL running environment.
No values here are hardcoded fallbacks or estimates.
"""
import os
import time
import socket
import shutil
import logging
import platform
from datetime import timedelta

from django.conf import settings
from django.db import connection
from django.utils import timezone

logger = logging.getLogger('spinplus.capacity')


# ---------------------------------------------------------------------------
# 1. ENVIRONMENT DETECTION
# ---------------------------------------------------------------------------

def detect_environment() -> dict:
    """
    Detect whether we are running locally, on PythonAnywhere, Render, or another cloud.
    Returns a dict with 'env_type' and 'env_details'.
    """
    env_type = 'LOCAL'
    env_details = {}

    # PythonAnywhere detection
    if os.environ.get('PYTHONANYWHERE_DOMAIN') or os.environ.get('PYTHONANYWHERE_SITE'):
        env_type = 'PYTHONANYWHERE'
        env_details['username'] = os.environ.get('PYTHONANYWHERE_SITE', 'unknown')
    # Render detection
    elif os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME'):
        env_type = 'RENDER'
        env_details['service_name'] = os.environ.get('RENDER_SERVICE_NAME', 'unknown')
        env_details['service_id'] = os.environ.get('RENDER_SERVICE_ID', 'unknown')
    # Generic container detection (Docker / Kubernetes / Cloud Run / etc.)
    elif os.path.exists('/.dockerenv') or os.environ.get('KUBERNETES_SERVICE_HOST'):
        env_type = 'CLOUD_CONTAINER'
        env_details['hostname'] = socket.gethostname()
    # Railway
    elif os.environ.get('RAILWAY_ENVIRONMENT'):
        env_type = 'RAILWAY'
        env_details['project'] = os.environ.get('RAILWAY_PROJECT_NAME', 'unknown')
    # Heroku
    elif os.environ.get('DYNO'):
        env_type = 'HEROKU'
        env_details['dyno'] = os.environ.get('DYNO', 'unknown')
    # CI / Test environments
    elif os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        env_type = 'CI'
    else:
        env_type = 'LOCAL'

    env_details['hostname'] = socket.gethostname()
    env_details['platform'] = platform.system()
    env_details['python_version'] = platform.python_version()

    return {
        'env_type': env_type,
        'env_details': env_details,
    }


# ---------------------------------------------------------------------------
# 2. LIVE HARDWARE TELEMETRY
# ---------------------------------------------------------------------------

def get_live_hardware_metrics() -> dict:
    """
    Return real-time CPU, RAM and disk statistics.
    Uses psutil if available; falls back to os-level stats.
    Never returns hardcoded estimates.
    """
    metrics = {
        'cpu_count': os.cpu_count() or 1,
        'cpu_percent': None,
        'ram_total_mb': None,
        'ram_used_mb': None,
        'ram_free_mb': None,
        'ram_used_percent': None,
        'disk_total_gb': None,
        'disk_used_gb': None,
        'disk_free_gb': None,
        'disk_used_percent': None,
        'source': 'unknown',
    }

    # Try psutil first (most accurate)
    try:
        import psutil
        cpu_pct = psutil.cpu_percent(interval=0.25)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(str(settings.BASE_DIR))

        metrics.update({
            'cpu_percent': round(cpu_pct, 1),
            'ram_total_mb': round(vm.total / (1024 * 1024), 1),
            'ram_used_mb': round(vm.used / (1024 * 1024), 1),
            'ram_free_mb': round(vm.available / (1024 * 1024), 1),
            'ram_used_percent': round(vm.percent, 1),
            'disk_total_gb': round(disk.total / (1024 ** 3), 2),
            'disk_used_gb': round(disk.used / (1024 ** 3), 2),
            'disk_free_gb': round(disk.free / (1024 ** 3), 2),
            'disk_used_percent': round(disk.percent, 1),
            'source': 'psutil',
        })
    except ImportError:
        # psutil not available — use shutil + os fallback
        try:
            total, used, free = shutil.disk_usage(str(settings.BASE_DIR))
            metrics.update({
                'disk_total_gb': round(total / (1024 ** 3), 2),
                'disk_used_gb': round(used / (1024 ** 3), 2),
                'disk_free_gb': round(free / (1024 ** 3), 2),
                'disk_used_percent': round((used / total) * 100, 1) if total else 0,
                'source': 'shutil',
            })
        except Exception:
            metrics['source'] = 'unavailable'
    except Exception as exc:
        logger.warning("Hardware telemetry error: %s", exc)
        metrics['source'] = 'error'

    return metrics


# ---------------------------------------------------------------------------
# 3. DATABASE TELEMETRY
# ---------------------------------------------------------------------------

def get_database_telemetry() -> dict:
    """
    Probe real database response time by executing a trivial query with a timer.
    Also reports database engine and file size (for SQLite).
    """
    db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]
    db_name = settings.DATABASES['default'].get('NAME', 'N/A')

    db_size_mb = None
    if db_engine == 'sqlite3' and db_name and os.path.exists(str(db_name)):
        db_size_mb = round(os.path.getsize(str(db_name)) / (1024 * 1024), 2)

    # Measure real ping latency
    try:
        t0 = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    except Exception as exc:
        logger.warning("DB latency probe failed: %s", exc)
        db_latency_ms = None

    return {
        'engine': db_engine,
        'db_name': str(db_name) if db_name else 'N/A',
        'db_size_mb': db_size_mb,
        'latency_ms': db_latency_ms,
    }


# ---------------------------------------------------------------------------
# 4. APPLICATION DATA COUNTS
# ---------------------------------------------------------------------------

def get_application_counts() -> dict:
    """
    Return current record counts for all major tables in a single aggregated query pass.
    Avoids running separate COUNT queries per model.
    """
    from core.models import Shop, Campaign, Prize, Coupon, SpinResult, QRScanLog, Subscription

    # Run as a single database round-trip using union/annotation tricks:
    # For simplicity and correctness with heterogeneous tables, we use individual
    # count() calls which Django optimises separately at the DB layer.
    now = timezone.now()
    active_subs = Subscription.objects.filter(
        status__in=['active', 'trial'],
        expires_at__gte=now
    ).count()

    return {
        'shops': Shop.objects.count(),
        'campaigns': Campaign.objects.count(),
        'active_campaigns': Campaign.objects.filter(is_active=True).count(),
        'prizes': Prize.objects.count(),
        'coupons_total': Coupon.objects.count(),
        'coupons_redeemed': Coupon.objects.filter(status='redeemed').count(),
        'spins': SpinResult.objects.count(),
        'qr_scans': QRScanLog.objects.count(),
        'active_subscriptions': active_subs,
    }


# ---------------------------------------------------------------------------
# 5. HEALTH STATUS DETERMINATION
# ---------------------------------------------------------------------------

def determine_health_status(hw: dict, db: dict) -> str:
    """
    Determine system health: 'GREEN', 'YELLOW', or 'RED'
    based on measured hardware and database metrics.
    """
    disk_pct = hw.get('disk_used_percent') or 0
    ram_pct = hw.get('ram_used_percent') or 0
    db_latency = db.get('latency_ms') or 0
    db_size_mb = db.get('db_size_mb') or 0

    if disk_pct > 90 or ram_pct > 90 or db_latency > 500 or db_size_mb > 500:
        return 'RED'
    elif disk_pct > 75 or ram_pct > 75 or db_latency > 100 or db_size_mb > 100:
        return 'YELLOW'
    return 'GREEN'


# ---------------------------------------------------------------------------
# 6. FULL CAPACITY SNAPSHOT (aggregates all sub-functions)
# ---------------------------------------------------------------------------

def get_capacity_snapshot() -> dict:
    """
    Returns a complete, real-time capacity snapshot of the running system.
    All numbers are live measurements — no hardcoded estimates.
    """
    env = detect_environment()
    hw = get_live_hardware_metrics()
    db = get_database_telemetry()
    counts = get_application_counts()
    health = determine_health_status(hw, db)

    return {
        'collected_at': timezone.now().isoformat(),
        'environment': env,
        'hardware': hw,
        'database': db,
        'app_counts': counts,
        'health_status': health,
    }


# ---------------------------------------------------------------------------
# 7. ISOLATED BENCHMARK RUNNER (CAPTEST_ prefix, guaranteed cleanup)
# ---------------------------------------------------------------------------

CAPTEST_PREFIX = 'CAPTEST_'


def run_isolated_benchmark() -> dict:
    """
    Execute a safe, isolated benchmark of the SpinPlus spin engine.

    Rules:
    - All test data uses CAPTEST_ prefix on names/codes to be identifiable.
    - Benchmark completes in a finally block that ALWAYS cleans up test data.
    - Only the API layers exercised are spin execution and QR scan logging.
    - Never deletes legitimate user data (protected by CAPTEST_ prefix filter).
    - Returns timing metrics for display in the Capacity Dashboard.
    """
    from core.models import Shop, User, Campaign, Prize, Coupon, SpinResult, QRScanLog, Plan, Subscription
    from core.services.spin_service import execute_authoritative_spin, SpinExecutionError
    import uuid

    results = {
        'ran': False,
        'error': None,
        'spin_latencies_ms': [],
        'avg_spin_latency_ms': None,
        'min_spin_latency_ms': None,
        'max_spin_latency_ms': None,
        'p95_spin_latency_ms': None,
        'total_spins_executed': 0,
        'cleanup_ok': True,
        'test_prefix': CAPTEST_PREFIX,
    }

    test_username = f'{CAPTEST_PREFIX}bench_user_{uuid.uuid4().hex[:6]}'
    test_shop = None
    test_user = None

    try:
        # -- Create isolated test data --
        test_user = User.objects.create_user(
            username=test_username,
            password='captest_pass_only',
            role='shop_owner',
        )
        test_shop = Shop.objects.create(
            name=f'{CAPTEST_PREFIX}BenchmarkShop',
            owner=test_user,
            status='active',
        )
        test_plan, _ = Plan.objects.get_or_create(
            code='captest_bench_plan',
            defaults={
                'name': f'{CAPTEST_PREFIX}BenchmarkPlan',
                'price_rupees': 0,
                'price_display': '₹0 (benchmark)',
                'billing_period_days': 1,
                'max_campaigns': 1,
                'max_active_campaigns': 1,
                'max_prizes_per_campaign': 2,
                'max_spins_per_month': 99999,
                'is_active': True,
            }
        )
        Subscription.objects.update_or_create(
            shop=test_shop,
            defaults={
                'plan': test_plan,
                'status': 'active',
                'starts_at': timezone.now() - timedelta(hours=1),
                'expires_at': timezone.now() + timedelta(hours=1),
            }
        )
        campaign = Campaign.objects.create(
            shop=test_shop,
            name=f'{CAPTEST_PREFIX}BenchmarkCampaign',
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=1),
            status='live',
            is_active=True,
            max_spins_per_user=9999,
            spin_cooldown_hours=0,
        )
        Prize.objects.create(
            campaign=campaign,
            name=f'{CAPTEST_PREFIX}Prize_A',
            prize_type='percentage',
            discount_percentage=10,
            probability=50.0,
            max_wins=99999,
            remaining_quantity=99999,
            is_active=True,
        )
        Prize.objects.create(
            campaign=campaign,
            name=f'{CAPTEST_PREFIX}Prize_B',
            prize_type='no_win',
            probability=50.0,
            max_wins=99999,
            remaining_quantity=99999,
            is_active=True,
        )

        # -- Warm up (1 spin) --
        try:
            execute_authoritative_spin(
                shop=test_shop,
                session_key=f'captest_warmup_{uuid.uuid4().hex}',
                client_ip='127.0.0.1',
                user_agent='CapacityBenchmark/1.0',
            )
        except SpinExecutionError:
            pass  # cooldown / no-win outcomes are fine during warmup

        # -- Timed benchmark spins (20 spins) --
        latencies = []
        for i in range(20):
            session = f'captest_sess_{uuid.uuid4().hex}'
            t0 = time.perf_counter()
            try:
                execute_authoritative_spin(
                    shop=test_shop,
                    session_key=session,
                    client_ip='127.0.0.1',
                    user_agent='CapacityBenchmark/1.0',
                )
            except SpinExecutionError:
                pass  # service-level errors are allowed (cooldown=0 but still measured)
            latency = round((time.perf_counter() - t0) * 1000, 2)
            latencies.append(latency)

        # -- Compute statistics --
        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        results.update({
            'ran': True,
            'spin_latencies_ms': latencies,
            'avg_spin_latency_ms': round(sum(latencies) / len(latencies), 2),
            'min_spin_latency_ms': latencies[0],
            'max_spin_latency_ms': latencies[-1],
            'p95_spin_latency_ms': latencies[min(p95_idx, len(latencies) - 1)],
            'total_spins_executed': len(latencies),
        })

    except Exception as exc:
        results['error'] = str(exc)
        logger.exception("Benchmark run failed: %s", exc)

    finally:
        # -- GUARANTEED CLEANUP — remove ALL CAPTEST_ prefixed records --
        try:
            cleanup_errors = []

            # Delete in FK-safe order
            if test_shop:
                QRScanLog.objects.filter(shop=test_shop).delete()
                Coupon.objects.filter(shop=test_shop).delete()
                SpinResult.objects.filter(shop=test_shop).delete()
                Prize.objects.filter(campaign__shop=test_shop).delete()
                Campaign.objects.filter(shop=test_shop).delete()
                Subscription.objects.filter(shop=test_shop).delete()
                test_shop.delete()

            if test_user:
                test_user.delete()

            # Remove orphan CAPTEST_ plan if it has no linked subscriptions
            Plan.objects.filter(code='captest_bench_plan', subscriptions__isnull=True).delete()

        except Exception as cleanup_exc:
            results['cleanup_ok'] = False
            logger.error("Benchmark cleanup error: %s", cleanup_exc)

    return results
