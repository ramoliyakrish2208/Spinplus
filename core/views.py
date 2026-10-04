import json
import csv
import random
import re
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Count, Q, Sum
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger('core')

def parse_decimal_safe(val, default='0.00', min_val=Decimal('0.00'), max_val=None):
    try:
        if val is None or str(val).strip() == '':
            d = Decimal(str(default))
        else:
            clean_str = str(val).strip()
            if len(clean_str) > 20:
                clean_str = clean_str[:20]
            d = Decimal(clean_str)
        if d.is_nan() or d.is_infinite():
            return Decimal(str(default)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        d = d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if min_val is not None and d < min_val:
            d = min_val
        if max_val is not None and d > max_val:
            d = max_val
        return d
    except (InvalidOperation, TypeError, ValueError):
        try:
            return Decimal(str(default)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            return Decimal('0.00')

def parse_int_safe(val, default=0, min_val=None, max_val=None):
    try:
        if val is None or str(val).strip() == '':
            i = int(default)
        else:
            i = int(val)
        if min_val is not None and i < min_val:
            i = min_val
        if max_val is not None and i > max_val:
            i = max_val
        return i
    except (TypeError, ValueError):
        return int(default)

def parse_float_safe(val, default=0.0, min_val=0.0, max_val=100.0):
    try:
        if val is None or str(val).strip() == '':
            f = float(default)
        else:
            f = float(val)
        if min_val is not None and f < min_val:
            f = min_val
        if max_val is not None and f > max_val:
            f = max_val
        return round(f, 2)
    except (TypeError, ValueError):
        return float(default)

def sanitize_segment_design_config(raw_config):
    """
    Sanitizes and normalizes segment design parameters.
    Ensures safe font families, colors, numeric ranges, and prevents script injection.
    """
    if not raw_config:
        return {}
    if isinstance(raw_config, str):
        try:
            raw_config = json.loads(raw_config)
        except Exception:
            return {}
    if not isinstance(raw_config, dict):
        return {}

    ALLOWED_FONTS = {
        'inter', 'poppins', 'montserrat', 'roboto', 'lato', 'nunito', 'outfit',
        'manrope', 'dm_sans', 'plus_jakarta_sans', 'oswald', 'bebas_neue',
        'anton', 'playfair', 'cormorant_garamond', 'cinzel', 'raleway',
        'quicksand', 'rubik', 'space_grotesk', 'archivo', 'barlow_condensed',
        'league_spartan'
    }

    clean = {}

    def clean_color(val, default='#ffffff'):
        s = str(val or '').strip()
        if re.match(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$', s):
            return s
        return default

    # Font family
    font = str(raw_config.get('font_family', '')).lower().strip().replace(' ', '_').replace('-', '_')
    if font in ALLOWED_FONTS:
        clean['font_family'] = font

    # Typography
    if 'font_weight' in raw_config:
        try:
            w = int(raw_config['font_weight'])
            if w in [300, 400, 500, 600, 700, 800, 900]:
                clean['font_weight'] = w
        except (ValueError, TypeError):
            pass

    if 'font_size' in raw_config:
        try:
            fs = int(raw_config['font_size'])
            if 8 <= fs <= 36:
                clean['font_size'] = fs
        except (ValueError, TypeError):
            pass

    align = str(raw_config.get('text_align', '')).lower().strip()
    if align in ['left', 'center', 'right']:
        clean['text_align'] = align

    transform = str(raw_config.get('text_transform', '')).lower().strip()
    if transform in ['none', 'uppercase', 'lowercase', 'capitalize']:
        clean['text_transform'] = transform

    if 'letter_spacing' in raw_config:
        try:
            ls = float(raw_config['letter_spacing'])
            clean['letter_spacing'] = round(max(-2.0, min(10.0, ls)), 1)
        except (ValueError, TypeError):
            pass

    font_style = str(raw_config.get('font_style', '')).lower().strip()
    if font_style in ['normal', 'italic']:
        clean['font_style'] = font_style

    if 'line_height' in raw_config:
        try:
            lh = float(raw_config['line_height'])
            clean['line_height'] = round(max(0.8, min(2.5, lh)), 2)
        except (ValueError, TypeError):
            pass

    # Text Appearance
    if 'text_color' in raw_config:
        clean['text_color'] = clean_color(raw_config['text_color'], '#ffffff')

    if 'text_opacity' in raw_config:
        try:
            op = int(raw_config['text_opacity'])
            clean['text_opacity'] = max(0, min(100, op))
        except (ValueError, TypeError):
            pass

    # Shadow
    if raw_config.get('text_shadow_enabled'):
        clean['text_shadow_enabled'] = True
        clean['text_shadow_color'] = clean_color(raw_config.get('text_shadow_color'), '#000000')
        try:
            clean['text_shadow_blur'] = max(0, min(30, int(raw_config.get('text_shadow_blur', 4))))
            clean['text_shadow_x'] = max(-20, min(20, int(raw_config.get('text_shadow_x', 0))))
            clean['text_shadow_y'] = max(-20, min(20, int(raw_config.get('text_shadow_y', 2))))
        except (ValueError, TypeError):
            pass

    # Stroke
    if raw_config.get('text_stroke_enabled'):
        clean['text_stroke_enabled'] = True
        clean['text_stroke_color'] = clean_color(raw_config.get('text_stroke_color'), '#000000')
        try:
            clean['text_stroke_width'] = max(1, min(6, int(raw_config.get('text_stroke_width', 2))))
        except (ValueError, TypeError):
            pass

    # Background
    bg_type = str(raw_config.get('bg_type', '')).lower().strip()
    if bg_type in ['solid', 'gradient', 'pattern']:
        clean['bg_type'] = bg_type
        if 'bg_color_1' in raw_config:
            clean['bg_color_1'] = clean_color(raw_config['bg_color_1'], '#6366f1')
        if 'bg_color_2' in raw_config:
            clean['bg_color_2'] = clean_color(raw_config['bg_color_2'], '#4f46e5')
        if 'bg_color_3' in raw_config and raw_config['bg_color_3']:
            clean['bg_color_3'] = clean_color(raw_config['bg_color_3'], '#ffd700')
        if 'gradient_type' in raw_config:
            g_type = str(raw_config['gradient_type']).lower().strip()
            if g_type in ['linear', 'radial']:
                clean['gradient_type'] = g_type
        if 'gradient_angle' in raw_config:
            try:
                clean['gradient_angle'] = max(0, min(360, int(raw_config['gradient_angle'])))
            except (ValueError, TypeError):
                pass
        if 'bg_pattern' in raw_config:
            pat = str(raw_config['bg_pattern']).lower().strip()
            if pat in ['dots', 'stripes', 'stars', 'chevrons', 'none']:
                clean['bg_pattern'] = pat

    # Segment Icon
    icon_type = str(raw_config.get('icon_type', '')).lower().strip()
    if icon_type in ['none', 'preset']:
        clean['icon_type'] = icon_type
        if icon_type == 'preset':
            icon_name = str(raw_config.get('icon_name', '')).strip()
            ALLOWED_ICONS = {
                'gift', 'percent', 'tag', 'star', 'crown', 'sparkles',
                'flame', 'trophy', 'diamond', 'heart', 'coffee',
                'shopping-bag', 'zap', 'smile', 'frown', 'award', 'ticket'
            }
            if icon_name in ALLOWED_ICONS:
                clean['icon_name'] = icon_name
            pos = str(raw_config.get('icon_position', '')).lower().strip()
            if pos in ['above', 'below', 'left', 'right']:
                clean['icon_position'] = pos
            try:
                clean['icon_size'] = max(10, min(36, int(raw_config.get('icon_size', 16))))
            except (ValueError, TypeError):
                pass
            try:
                clean['icon_spacing'] = max(0, min(24, int(raw_config.get('icon_spacing', 6))))
            except (ValueError, TypeError):
                pass

    # Borders & Effects
    if raw_config.get('border_enabled'):
        clean['border_enabled'] = True
        clean['border_color'] = clean_color(raw_config.get('border_color'), '#ffd700')
        try:
            clean['border_width'] = max(1, min(6, int(raw_config.get('border_width', 2))))
        except (ValueError, TypeError):
            pass
        b_style = str(raw_config.get('border_style', '')).lower().strip()
        if b_style in ['solid', 'dashed', 'dotted']:
            clean['border_style'] = b_style

    if raw_config.get('glow_enabled'):
        clean['glow_enabled'] = True
        clean['glow_color'] = clean_color(raw_config.get('glow_color'), '#ffd700')
        try:
            clean['glow_intensity'] = max(1, min(10, int(raw_config.get('glow_intensity', 5))))
        except (ValueError, TypeError):
            pass

    if raw_config.get('highlight_enabled'):
        clean['highlight_enabled'] = True

    return clean

def get_error_context(request, status_code: int, default_msg: str = ""):
    path = getattr(request, 'path', '') or ''
    is_customer_route = (
        path.startswith('/s/') or
        path.startswith('/coupon/') or
        path.startswith('/verify/')
    )
    is_authenticated = hasattr(request, 'user') and request.user.is_authenticated
    user = getattr(request, 'user', None)

    is_admin_route = path.startswith('/dashboard/admin/')
    is_shop_route = (
        path.startswith('/dashboard/shop/') or
        path.startswith('/dashboard/subscription/') or
        path.startswith('/dashboard/billing/') or
        path.startswith('/dashboard/account/') or
        path.startswith('/dashboard/notifications/')
    )

    context_type = 'public'
    if is_customer_route:
        context_type = 'customer'
    elif is_admin_route and is_authenticated and getattr(user, 'is_superadmin', lambda: False)():
        context_type = 'admin'
    elif is_shop_route and is_authenticated and (getattr(user, 'shop', None) or getattr(user, 'is_superadmin', lambda: False)()):
        context_type = 'shop'

    # Extract public token if on /s/<token>/ route
    public_token = None
    if path.startswith('/s/'):
        parts = [p for p in path.split('/') if p]
        if len(parts) >= 2 and parts[0] == 's':
            public_token = parts[1]

    # Detect API/AJAX requests
    is_ajax = (
        (hasattr(request, 'headers') and request.headers.get('x-requested-with') == 'XMLHttpRequest') or
        path.endswith('/spin/') or
        '/api/' in path or
        'application/json' in request.META.get('HTTP_ACCEPT', '')
    )

    return {
        'status_code': status_code,
        'context_type': context_type,
        'is_public_page': context_type in ('public', 'customer') or not is_authenticated,
        'is_customer_error': context_type == 'customer',
        'is_admin_error': context_type == 'admin',
        'is_shop_owner_error': context_type == 'shop',
        'public_token': public_token,
        'is_ajax': is_ajax,
        'default_msg': default_msg,
    }

from core.models import (
    User, Shop, ShopBranding, Campaign, Prize, QRCode,
    SpinResult, Coupon, CouponRedemption, ActivityLog, QRScanLog,
    Plan, Subscription, Notification, PlanRequest
)
from core.qr import generate_shop_qr, generate_coupon_qr
from core.utils.security import (
    get_client_ip, validate_uploaded_image, sanitize_filename,
    login_rate_limiter, spin_rate_limiter, coupon_rate_limiter
)
from core.services.spin_service import execute_authoritative_spin, SpinExecutionError
from core.services.coupon_service import redeem_coupon_atomically, CouponRedemptionError

# Helper Decorators
def shop_access_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superadmin():
            return view_func(request, *args, **kwargs)
        if request.user.shop:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: No shop associated with your account.")
    return wrapper

def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin():
            return HttpResponseForbidden("Super Admin access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------
# GLOBAL SEARCH API
# ---------------------------------------------------------

@login_required
def global_search_api(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    results = []
    user = request.user

    if user.is_superadmin():
        shops = Shop.objects.filter(Q(name__icontains=q) | Q(public_token__icontains=q))[:5]
        for s in shops:
            results.append({'type': 'Shop', 'title': s.name, 'subtitle': f"Token: {s.public_token}", 'url': f"/dashboard/shop/?shop_id={s.id}"})

    shop = user.shop if user.shop else (Shop.objects.first() if user.is_superadmin() else None)
    if shop:
        camps = Campaign.objects.filter(shop=shop, name__icontains=q)[:5]
        for c in camps:
            results.append({'type': 'Campaign', 'title': c.name, 'subtitle': f"Status: {c.status}", 'url': f"/dashboard/shop/campaigns/{c.id}/prizes/"})

        coupons = Coupon.objects.filter(shop=shop, code__icontains=q).select_related('prize')[:5]
        for c in coupons:
            results.append({'type': 'Coupon', 'title': c.code, 'subtitle': f"Prize: {c.prize.name}", 'url': f"/verify/{c.verify_token}/"})

        prizes = Prize.objects.filter(campaign__shop=shop, name__icontains=q).select_related('campaign')[:5]
        for p in prizes:
            results.append({'type': 'Prize', 'title': p.name, 'subtitle': f"Campaign: {p.campaign.name}", 'url': f"/dashboard/shop/campaigns/{p.campaign.id}/prizes/"})

    return JsonResponse({'results': results})


# ---------------------------------------------------------
# PUBLIC CUSTOMER LANDING & SPIN LOGIC
# ---------------------------------------------------------

def public_shop_view(request, public_token):
    # Optimised: collapse branding + subscription + plan into a single DB round-trip
    shop = get_object_or_404(
        Shop.objects.select_related('subscription__plan', 'subscription__future_plan'),
        public_token=public_token,
    )
    if shop.status != 'active':
        return render(request, 'errors/shop_unavailable.html', {'shop': shop, 'is_public_page': True}, status=403)

    client_ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    QRScanLog.objects.create(shop=shop, ip_address=client_ip, user_agent=user_agent)

    # Use prefetched branding if available; only hit DB if not yet cached
    if hasattr(shop, '_prefetched_objects_cache') and 'branding' in shop._prefetched_objects_cache:
        branding = shop.branding
    else:
        branding, _ = ShopBranding.objects.get_or_create(shop=shop)
    from core.services.theme_resolver import get_active_shop_theme, ThemeResolution
    theme_param = request.GET.get('theme')
    if theme_param:
        active_theme = theme_param
        theme_resolution = ThemeResolution(theme=active_theme, reason=f"Query Override: {active_theme}", normal_theme=active_theme)
    else:
        campaign = shop.get_active_campaign()
        theme_resolution = get_active_shop_theme(shop, campaign)
        active_theme = theme_resolution.theme

    if not shop.has_active_subscription():
        return render(request, 'customer/subscription_expired.html', {
            'shop': shop,
            'branding': branding,
            'active_theme': active_theme,
            'is_public_page': True
        }, status=403)

    campaign = shop.get_active_campaign()
    if not campaign:
        return render(request, 'customer/no_campaign.html', {
            'shop': shop,
            'branding': branding,
            'active_theme': active_theme,
            'theme_resolution': theme_resolution,
            'is_public_page': True
        })

    prizes = list(campaign.prizes.filter(is_active=True, remaining_quantity__gt=0))
    if not prizes:
        return render(request, 'customer/no_campaign.html', {
            'shop': shop,
            'branding': branding,
            'active_theme': active_theme,
            'theme_resolution': theme_resolution,
            'is_public_page': True
        })

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    recent_spin = SpinResult.objects.filter(
        shop=shop,
        campaign=campaign,
        session_key=session_key,
        created_at__gte=timezone.now() - timedelta(hours=campaign.spin_cooldown_hours)
    ).select_related('prize').first()

    existing_coupon = None
    cooldown_remaining_seconds = 0
    cooldown_remaining_formatted = ""
    is_in_cooldown = False

    if recent_spin:
        is_in_cooldown = True
        cooldown_ends_at = recent_spin.created_at + timedelta(hours=campaign.spin_cooldown_hours)
        cooldown_remaining_seconds = max(0, int((cooldown_ends_at - timezone.now()).total_seconds()))
        hours = cooldown_remaining_seconds // 3600
        mins = (cooldown_remaining_seconds % 3600) // 60
        if hours > 0:
            cooldown_remaining_formatted = f"{hours}h {mins}m"
        else:
            cooldown_remaining_formatted = f"{max(1, mins)}m"

        if hasattr(recent_spin, 'coupon'):
            existing_coupon = recent_spin.coupon

    winning_segment_index = None
    if recent_spin and recent_spin.prize:
        for idx, p in enumerate(prizes):
            if p.id == recent_spin.prize_id:
                winning_segment_index = idx
                break

    prizes_data = [
        {
            'id': p.id,
            'name': p.name,
            'display_color': p.display_color,
            'prize_type': p.prize_type,
            'design_config': p.design_config or {}
        } for p in prizes
    ]

    center_hub_config = campaign.get_center_hub_config() if campaign else {}
    context = {
        'shop': shop,
        'branding': branding,
        'font_family': getattr(branding, 'font_family', 'inter') if branding else 'inter',
        'active_theme': active_theme,
        'theme_resolution': theme_resolution,
        'theme_intensity': getattr(branding, 'intensity', 'balanced') or 'balanced',
        'campaign': campaign,
        'prizes': prizes,
        'prizes_json': json.dumps(prizes_data),
        'recent_spin': recent_spin,
        'existing_coupon': existing_coupon,
        'is_in_cooldown': is_in_cooldown,
        'cooldown_remaining_seconds': cooldown_remaining_seconds,
        'cooldown_remaining_formatted': cooldown_remaining_formatted,
        'winning_segment_index': winning_segment_index,
        'center_hub_config': center_hub_config,
        'center_hub_config_json': json.dumps(center_hub_config),
        'is_public_page': True
    }
    return render(request, 'customer/spin_landing.html', context)


@require_POST
def spin_wheel_api(request, public_token):
    client_ip = get_client_ip(request)
    if not spin_rate_limiter.is_allowed(client_ip, max_requests=15, window_seconds=60):
        return JsonResponse({
            'status': 'error',
            'message': 'Too many spin attempts. Please wait a moment and try again.'
        }, status=429)

    shop = get_object_or_404(Shop, public_token=public_token, status='active')

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    user_agent = request.META.get('HTTP_USER_AGENT', '')

    try:
        outcome = execute_authoritative_spin(
            shop=shop,
            session_key=session_key,
            client_ip=client_ip,
            user_agent=user_agent
        )
        return JsonResponse({
            'status': 'success',
            'winning_segment_index': outcome['winning_segment_index'],
            'prize': outcome['prize'],
            'coupon': outcome['coupon']
        })
    except SpinExecutionError as e:
        return JsonResponse({'status': 'error', 'message': e.message}, status=e.status_code)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred while processing your spin.'}, status=500)



# ---------------------------------------------------------
# PUBLIC SHAREABLE DIGITAL COUPON VIEW
# ---------------------------------------------------------

def public_coupon_view(request, token):
    coupon = get_object_or_404(Coupon, verify_token=token)
    active_theme = coupon.shop.resolve_theme()
    return render(request, 'customer/public_coupon.html', {
        'coupon': coupon,
        'shop': coupon.shop,
        'branding': coupon.shop.branding if hasattr(coupon.shop, 'branding') else None,
        'active_theme': active_theme,
        'is_public_page': True
    })


def verify_coupon_token_view(request, token):
    coupon = get_object_or_404(Coupon, verify_token=token)
    message = None
    error = None

    if request.method == 'POST' and request.user.is_authenticated:
        if request.user.is_superadmin() or (request.user.shop and request.user.shop == coupon.shop):
            try:
                redeemed = redeem_coupon_atomically(
                    code=coupon.code,
                    shop=coupon.shop,
                    actor=request.user,
                    notes="Redeemed via QR verification token"
                )
                coupon.refresh_from_db()
                message = f"Coupon {coupon.code} ({coupon.prize.name}) redeemed successfully!"
            except CouponRedemptionError as e:
                error = e.message
        else:
            error = "Unauthorized: You do not have permission to redeem coupons for this shop."

    return render(request, 'coupons/verify.html', {
        'coupon': coupon,
        'shop': coupon.shop,
        'message': message,
        'error': error,
        'is_public_page': True
    })



# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

def user_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superadmin():
            return redirect('admin_dashboard')
        return redirect('shop_dashboard')

    error_msg = None
    if request.method == 'POST':
        client_ip = get_client_ip(request)
        if not login_rate_limiter.is_allowed(client_ip, max_requests=10, window_seconds=60):
            return render(request, 'auth/login.html', {
                'error': "Too many login attempts. Please wait a minute and try again.",
                'is_public_page': True
            }, status=429)

        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if not user.is_active:
                error_msg = "This account is inactive. Please contact support."
            else:
                login(request, user)
                if user.is_superadmin():
                    return redirect('admin_dashboard')
                return redirect('shop_dashboard')
        else:
            error_msg = "Invalid username or password."

    return render(request, 'auth/login.html', {'error': error_msg, 'is_public_page': True})

def user_logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------------------------------------
# SHOP OWNER DASHBOARD & MANAGEMENT
# ---------------------------------------------------------

@shop_access_required
def shop_dashboard(request):
    shop = request.user.shop
    if request.user.is_superadmin():
        if 'shop_id' in request.GET:
            shop = get_object_or_404(Shop, id=request.GET.get('shop_id'))
        elif not shop:
            shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    now = timezone.now()
    range_filter = request.GET.get('range', 'today')

    if range_filter == '7d':
        start_date = now - timedelta(days=7)
    elif range_filter == '30d':
        start_date = now - timedelta(days=30)
    elif range_filter == 'all':
        start_date = timezone.make_aware(timezone.datetime(2020, 1, 1))
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Optimised: run 4 count queries in parallel-friendly annotation block to minimise round-trips
    from django.db.models import Count, Q as Qm
    scans_count = QRScanLog.objects.filter(shop=shop, scanned_at__gte=start_date).count()
    spins_count = SpinResult.objects.filter(shop=shop, created_at__gte=start_date).count()
    coupons_won = Coupon.objects.filter(shop=shop, created_at__gte=start_date).count()
    coupons_redeemed = CouponRedemption.objects.filter(coupon__shop=shop, redeemed_at__gte=start_date).count()

    spin_conversion_rate = round((spins_count / scans_count * 100), 1) if scans_count > 0 else 0.0
    win_rate = round((coupons_won / spins_count * 100), 1) if spins_count > 0 else 0.0
    redemption_rate = round((coupons_redeemed / coupons_won * 100), 1) if coupons_won > 0 else 0.0
    overall_funnel_rate = round((coupons_redeemed / scans_count * 100), 1) if scans_count > 0 else 0.0

    # Reuse shop.branding if already cached by select_related; else get_or_create
    try:
        branding = shop.branding
    except ShopBranding.DoesNotExist:
        branding, _ = ShopBranding.objects.get_or_create(shop=shop)
    active_campaign = shop.get_active_campaign()
    site_base = getattr(settings, 'SITE_URL', request.build_absolute_uri('/')).rstrip('/')
    qr_code, _ = QRCode.objects.get_or_create(shop=shop, defaults={'target_url': f"{site_base}/s/{shop.public_token}/"})

    if not qr_code.qr_image:
        generate_shop_qr(shop, site_base)

    # Safely load active campaign prizes to isolate corrupt Decimal values
    active_prizes = []
    if active_campaign:
        try:
            active_prizes = list(active_campaign.prizes.all())
        except (InvalidOperation, Exception) as prize_err:
            logger.error(
                "Failed to convert or load prizes for campaign ID %s (shop ID %s): %s",
                getattr(active_campaign, 'id', None),
                getattr(shop, 'id', None),
                prize_err
            )
            # Safe recovery fallback: retrieve display attributes without triggering Decimal conversion
            try:
                active_prizes = list(active_campaign.prizes.values('id', 'name', 'probability', 'display_color', 'prize_type'))
            except Exception:
                active_prizes = []

    # Safely load recent coupons
    try:
        recent_coupons = list(Coupon.objects.filter(shop=shop).select_related('prize', 'redemption').order_by('-created_at')[:10])
    except (InvalidOperation, Exception) as coupon_err:
        logger.error("Failed to load recent coupons with prizes for shop ID %s: %s", getattr(shop, 'id', None), coupon_err)
        try:
            recent_coupons = list(Coupon.objects.filter(shop=shop).select_related('redemption').order_by('-created_at')[:10])
        except Exception:
            recent_coupons = []

    checklist = [
        {'title': 'Shop Created', 'done': True},
        {'title': 'Add Logo & Cover', 'done': bool(shop.logo)},
        {'title': 'Active Campaign', 'done': bool(active_campaign)},
        {'title': 'Prizes Configured', 'done': bool(active_campaign and (len(active_prizes) > 0 or active_campaign.prizes.exists()))},
        {'title': 'Branding Customized', 'done': bool(branding.theme != 'modern' or branding.primary_color != '#6366f1')},
        {'title': 'QR Generated', 'done': bool(qr_code.qr_image)},
        {'title': 'Coupons Issued', 'done': bool(recent_coupons)},
    ]
    completed_steps = sum(1 for item in checklist if item['done'])

    from core.services.theme_resolver import get_active_shop_theme, get_shop_local_datetime
    from core.services.calendar_service import CalendarEvent

    current_resolution = get_active_shop_theme(shop)
    upcoming_events = CalendarEvent.objects.filter(is_active=True, end_date__gte=get_shop_local_datetime(shop).date()).order_by('start_date')[:4]
    
    try:
        subscription = shop.get_subscription()
        has_active_subscription = shop.has_active_subscription()
    except (InvalidOperation, Exception) as sub_err:
        logger.error("Failed to load subscription for shop ID %s: %s", getattr(shop, 'id', None), sub_err)
        subscription = None
        has_active_subscription = False

    context = {
        'shop': shop,
        'branding': branding,
        'current_resolution': current_resolution,
        'upcoming_events': upcoming_events,
        'active_campaign': active_campaign,
        'active_prizes': active_prizes,
        'subscription': subscription,
        'has_active_subscription': has_active_subscription,
        'range_filter': range_filter,
        'scans_count': scans_count,
        'spins_count': spins_count,
        'coupons_won': coupons_won,
        'coupons_redeemed': coupons_redeemed,
        'spin_conversion_rate': spin_conversion_rate,
        'win_rate': win_rate,
        'redemption_rate': redemption_rate,
        'overall_funnel_rate': overall_funnel_rate,
        'qr_code': qr_code,
        'recent_coupons': recent_coupons,
        'checklist': checklist,
        'completed_steps': completed_steps,
        'total_checklist_steps': len(checklist),
        'public_url': request.build_absolute_uri(f"/s/{shop.public_token}/")
    }
    return render(request, 'dashboard/shop_dashboard.html', context)



# ---------------------------------------------------------
# CAMPAIGN & PRIZE MANAGEMENT
# ---------------------------------------------------------

@shop_access_required
def campaign_list_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    sub = get_or_create_shop_subscription(shop)
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            if shop.campaigns.count() >= sub.plan.max_campaigns:
                error = f"Plan limit reached! Your {sub.plan.name} allows a maximum of {sub.plan.max_campaigns} campaigns."
                Notification.objects.create(
                    shop=shop, user=request.user, title="Campaign Plan Limit Reached",
                    message=error, level="warning"
                )
            else:
                name = request.POST.get('name')
                desc = request.POST.get('description', '')
                template_choice = request.POST.get('template_type', '')
                campaign_theme = request.POST.get('theme', '').strip()
                cooldown = parse_int_safe(request.POST.get('spin_cooldown_hours'), default=24, min_val=0, max_val=720)
                start_date = timezone.now()
                end_date = timezone.now() + timedelta(days=60)
                
                Campaign.objects.filter(shop=shop).update(is_active=False, status='draft')
                
                camp = Campaign.objects.create(
                    shop=shop, name=name, description=desc, spin_cooldown_hours=cooldown,
                    template_type=template_choice, theme=campaign_theme, start_date=start_date, end_date=end_date, status='live', is_active=True
                )

                # Initialize template prizes if selected
                if template_choice == 'festival':
                    Prize.objects.create(campaign=camp, name='20% OFF Festive Discount', prize_type='percentage', discount_percentage=Decimal('20.00'), coupon_text='20% off total bill', probability=40.0, display_color='#6366f1')
                    Prize.objects.create(campaign=camp, name='₹100 Gift Voucher', prize_type='fixed', fixed_discount_amount=Decimal('100.00'), coupon_text='Flat ₹100 off', probability=30.0, display_color='#f59e0b')
                    Prize.objects.create(campaign=camp, name='Free Seasonal Drink', prize_type='freebie', coupon_text='1 Free Beverage', probability=20.0, display_color='#10b981')
                    Prize.objects.create(campaign=camp, name='Better Luck Next Time', prize_type='no_win', coupon_text='Try again on next visit', probability=10.0, display_color='#64748b')
                elif template_choice == 'weekend':
                    Prize.objects.create(campaign=camp, name='15% OFF Weekend Special', prize_type='percentage', discount_percentage=Decimal('15.00'), coupon_text='15% off weekend bill', probability=50.0, display_color='#ec4899')
                    Prize.objects.create(campaign=camp, name='Buy 1 Get 1 Free', prize_type='freebie', coupon_text='1 Free item on BOGO', probability=30.0, display_color='#8b5cf6')
                    Prize.objects.create(campaign=camp, name='Try Again Next Visit', prize_type='no_win', coupon_text='Thanks for playing', probability=20.0, display_color='#64748b')
                elif template_choice == 'grand_opening':
                    Prize.objects.create(campaign=camp, name='25% Welcome Discount', prize_type='percentage', discount_percentage=Decimal('25.00'), coupon_text='25% off grand opening special', probability=40.0, display_color='#3b82f6')
                    Prize.objects.create(campaign=camp, name='₹200 Cash Voucher', prize_type='fixed', fixed_discount_amount=Decimal('200.00'), coupon_text='Flat ₹200 off', probability=40.0, display_color='#f59e0b')
                    Prize.objects.create(campaign=camp, name='Free Welcome Dessert', prize_type='freebie', coupon_text='1 Complimentary Dessert', probability=20.0, display_color='#10b981')

                ActivityLog.objects.create(shop=shop, actor=request.user, action="Campaign Created", details=f"Campaign {camp.name} (Template: {template_choice or 'Custom'})")
                return redirect('prize_manager', campaign_id=camp.id)

        elif action == 'toggle_status':
            camp_id = request.POST.get('campaign_id')
            camp = get_object_or_404(Campaign, id=camp_id, shop=shop)
            if camp.is_active:
                camp.is_active = False
                camp.status = 'draft'
            else:
                Campaign.objects.filter(shop=shop).update(is_active=False, status='draft')
                camp.is_active = True
                camp.status = 'live'
            camp.save()
            return redirect('campaign_list')

    campaigns_qs = Campaign.objects.filter(shop=shop).order_by('-created_at')
    paginator = Paginator(campaigns_qs, 12)
    page_number = request.GET.get('page', 1)
    try:
        campaigns_page = paginator.page(page_number)
    except PageNotAnInteger:
        campaigns_page = paginator.page(1)
    except EmptyPage:
        campaigns_page = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/campaigns.html', {
        'shop': shop,
        'campaigns': campaigns_page,
        'campaigns_page': campaigns_page,
        'paginator': paginator,
        'total_campaigns_count': campaigns_qs.count(),
        'error': error,
        'subscription': sub
    })


@shop_access_required
def duplicate_campaign_view(request, campaign_id):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    original_camp = get_object_or_404(Campaign, id=campaign_id, shop=shop)

    # Enforce subscription plan limits
    if not shop.can_create_campaign():
        sub = shop.get_subscription()
        Notification.objects.create(
            shop=shop, user=request.user, title="Campaign Plan Limit Reached",
            message=f"Plan limit reached! Your {sub.plan.name} allows a maximum of {sub.plan.max_campaigns} campaigns.",
            level="warning"
        )
        return redirect('campaign_list')

    new_camp = Campaign.objects.create(
        shop=shop,
        name=f"{original_camp.name} (Copy)",
        description=original_camp.description,
        theme=original_camp.theme,
        spin_cooldown_hours=original_camp.spin_cooldown_hours,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
        status='draft',
        is_active=False
    )

    for prize in original_camp.prizes.all():
        Prize.objects.create(
            campaign=new_camp,
            name=prize.name,
            prize_type=prize.prize_type,
            discount_percentage=prize.discount_percentage,
            fixed_discount_amount=prize.fixed_discount_amount,
            coupon_text=prize.coupon_text,
            probability=prize.probability,
            display_color=prize.display_color,
            max_wins=prize.max_wins,
            remaining_quantity=prize.max_wins,
            is_active=prize.is_active
        )

    ActivityLog.objects.create(shop=shop, actor=request.user, action="Campaign Duplicated", details=f"Duplicated '{original_camp.name}' to '{new_camp.name}'")
    return redirect('prize_manager', campaign_id=new_camp.id)


@shop_access_required
def prize_manager_view(request, campaign_id):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    campaign = get_object_or_404(Campaign, id=campaign_id, shop=shop)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_prize':
            name = (request.POST.get('name') or '').strip()
            p_type = request.POST.get('prize_type', 'percentage')
            disc_pct = parse_decimal_safe(request.POST.get('discount_percentage'), default='0.00', min_val=Decimal('0.00'), max_val=Decimal('100.00'))
            fixed_amt = parse_decimal_safe(request.POST.get('fixed_discount_amount'), default='0.00', min_val=Decimal('0.00'), max_val=Decimal('99999999.99'))
            
            # If user selected fixed discount and typed amount into discount_percentage input
            if p_type == 'fixed' and fixed_amt == Decimal('0.00') and disc_pct > Decimal('0.00'):
                fixed_amt = disc_pct
                disc_pct = Decimal('0.00')
            elif p_type != 'percentage':
                disc_pct = Decimal('0.00')

            coupon_text = (request.POST.get('coupon_text') or '').strip()
            prob = parse_float_safe(request.POST.get('probability'), default=10.0, min_val=0.0, max_val=100.0)
            color = (request.POST.get('display_color') or '#6366f1').strip()
            qty = parse_int_safe(request.POST.get('remaining_quantity'), default=100, min_val=0)
            raw_design = request.POST.get('design_config')
            design_config = sanitize_segment_design_config(raw_design)

            Prize.objects.create(
                campaign=campaign, name=name, prize_type=p_type, discount_percentage=disc_pct,
                fixed_discount_amount=fixed_amt, coupon_text=coupon_text, probability=prob,
                display_color=color, max_wins=qty, remaining_quantity=qty,
                design_config=design_config
            )
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Prize Added", details=f"Prize {name} added to {campaign.name}")
            return redirect('prize_manager', campaign_id=campaign.id)

        elif action == 'edit_prize':
            prize_id = request.POST.get('prize_id')
            prize = get_object_or_404(Prize, id=prize_id, campaign=campaign)
            prize.name = (request.POST.get('name') or prize.name).strip()
            prize.prize_type = request.POST.get('prize_type', prize.prize_type)
            if 'discount_percentage' in request.POST:
                prize.discount_percentage = parse_decimal_safe(request.POST.get('discount_percentage'), default=prize.discount_percentage, min_val=Decimal('0.00'), max_val=Decimal('100.00'))
            if 'fixed_discount_amount' in request.POST:
                prize.fixed_discount_amount = parse_decimal_safe(request.POST.get('fixed_discount_amount'), default=prize.fixed_discount_amount, min_val=Decimal('0.00'), max_val=Decimal('99999999.99'))
            
            # If user selected fixed discount and typed amount into discount_percentage
            if prize.prize_type == 'fixed' and prize.fixed_discount_amount == Decimal('0.00') and prize.discount_percentage > Decimal('0.00'):
                prize.fixed_discount_amount = prize.discount_percentage
                prize.discount_percentage = Decimal('0.00')
            elif prize.prize_type != 'percentage':
                prize.discount_percentage = Decimal('0.00')

            prize.coupon_text = (request.POST.get('coupon_text') or prize.coupon_text).strip()
            if 'probability' in request.POST:
                prize.probability = parse_float_safe(request.POST.get('probability'), default=prize.probability, min_val=0.0, max_val=100.0)
            prize.display_color = (request.POST.get('display_color') or prize.display_color).strip()
            if 'remaining_quantity' in request.POST:
                qty = parse_int_safe(request.POST.get('remaining_quantity'), default=prize.remaining_quantity, min_val=0)
                prize.max_wins = qty
                prize.remaining_quantity = qty
            if 'design_config' in request.POST:
                raw_design = request.POST.get('design_config')
                prize.design_config = sanitize_segment_design_config(raw_design)
            prize.save()
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Prize Updated", details=f"Prize {prize.name} updated in {campaign.name}")
            return redirect('prize_manager', campaign_id=campaign.id)

        elif action == 'delete_prize':
            prize_id = request.POST.get('prize_id')
            Prize.objects.filter(id=prize_id, campaign=campaign).delete()
            return redirect('prize_manager', campaign_id=campaign.id)

        elif action == 'update_wheel_center':
            hub_mode = request.POST.get('hub_mode', 'motif')
            hub_type = request.POST.get('hub_type', '')
            hub_icon = request.POST.get('hub_icon', 'crown')
            icon_color = request.POST.get('icon_color', '#ffd700')
            rim_color = request.POST.get('rim_color', '#ffd700')
            bg_color = request.POST.get('bg_color', '#1e1324')
            remove_logo = request.POST.get('remove_logo') == '1'

            current_cfg = dict(campaign.wheel_config or {})
            current_cfg.update({
                'mode': hub_mode,
                'hubType': hub_type,
                'icon': hub_icon,
                'iconColor': icon_color,
                'rimColor': rim_color,
                'bgColor': bg_color,
            })

            if 'center_logo' in request.FILES:
                campaign.center_logo = request.FILES['center_logo']
                campaign.save()
                current_cfg['center_logo_url'] = campaign.center_logo.url
            elif remove_logo:
                campaign.center_logo = None
                campaign.save()
                current_cfg['center_logo_url'] = ''

            use_shop_logo = request.POST.get('use_shop_logo') == '1'
            if use_shop_logo and shop.logo:
                current_cfg['center_logo_url'] = shop.logo.url

            campaign.wheel_config = current_cfg
            campaign.save()

            ActivityLog.objects.create(
                shop=shop, actor=request.user,
                action="Wheel Center Hub Updated",
                details=f"Center Hub mode '{hub_mode}' updated for campaign '{campaign.name}'"
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
                return JsonResponse({'status': 'ok', 'wheel_config': current_cfg, 'center_hub_config': campaign.get_center_hub_config()})
            return redirect('prize_manager', campaign_id=campaign.id)

    prizes = campaign.prizes.all()
    total_probability = sum(parse_float_safe(getattr(p, 'probability', 0.0), default=0.0) for p in prizes)

    prizes_json = json.dumps([
        {
            'id': p.id,
            'name': p.name,
            'display_color': p.display_color,
            'prize_type': p.prize_type,
            'discount_percentage': str(p.discount_percentage),
            'fixed_discount_amount': str(p.fixed_discount_amount),
            'probability': p.probability,
            'coupon_text': p.coupon_text,
            'remaining_quantity': p.remaining_quantity,
            'design_config': p.design_config or {}
        }
        for p in prizes
    ])

    branding = shop.get_branding()
    from core.services.theme_resolver import get_active_shop_theme
    theme_resolution = get_active_shop_theme(shop, campaign)
    active_theme = theme_resolution.theme

    center_hub_config = campaign.get_center_hub_config()
    center_hub_config_json = json.dumps(center_hub_config)

    return render(request, 'dashboard/prize_manager.html', {
        'shop': shop,
        'branding': branding,
        'campaign': campaign,
        'active_theme': active_theme,
        'theme_resolution': theme_resolution,
        'prizes': prizes,
        'total_probability': round(total_probability, 1),
        'prizes_json': prizes_json,
        'center_hub_config': center_hub_config,
        'center_hub_config_json': center_hub_config_json
    })


# ---------------------------------------------------------
# ACTIVITY LOGS VIEW
# ---------------------------------------------------------

@shop_access_required
def activity_logs_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    logs_qs = ActivityLog.objects.filter(shop=shop).select_related('actor').order_by('-timestamp')
    paginator = Paginator(logs_qs, 25)
    page_number = request.GET.get('page', 1)
    try:
        logs_page = paginator.page(page_number)
    except PageNotAnInteger:
        logs_page = paginator.page(1)
    except EmptyPage:
        logs_page = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/activity_logs.html', {
        'shop': shop,
        'logs': logs_page,
        'logs_page': logs_page,
        'paginator': paginator,
        'total_logs_count': logs_qs.count()
    })


@shop_access_required
def shop_profile_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    error = None
    if request.method == 'POST':
        shop.name = request.POST.get('name', shop.name)
        shop.category = request.POST.get('category', shop.category)
        shop.currency_symbol = request.POST.get('currency_symbol', shop.currency_symbol)
        shop.phone = request.POST.get('phone', shop.phone)
        shop.email = request.POST.get('email', shop.email)
        shop.address = request.POST.get('address', shop.address)
        shop.description = request.POST.get('description', shop.description)
        
        try:
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                validate_uploaded_image(logo_file)
                logo_file.name = sanitize_filename(logo_file.name, prefix=f"{shop.name}_logo")
                shop.logo = logo_file

            if 'cover_image' in request.FILES:
                cover_file = request.FILES['cover_image']
                validate_uploaded_image(cover_file)
                cover_file.name = sanitize_filename(cover_file.name, prefix=f"{shop.name}_cover")
                shop.cover_image = cover_file
                
            shop.save()
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Shop Profile Updated", details=f"Profile updated for {shop.name}")
            return redirect('shop_dashboard')
        except ValidationError as e:
            error = str(e.message if hasattr(e, 'message') else e)

    return render(request, 'dashboard/profile.html', {'shop': shop, 'error': error})


@shop_access_required
def update_branding(request):
    shop = request.user.shop
    if request.user.is_superadmin():
        if 'shop_id' in request.GET:
            shop = get_object_or_404(Shop, id=request.GET.get('shop_id'))
        elif not shop:
            shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    branding, _ = ShopBranding.objects.get_or_create(shop=shop)
    from core.services.theme_resolver import get_active_shop_theme, get_shop_local_datetime
    from core.services.calendar_service import sync_calendar_events, CalendarEvent
    from core.models import ThemeAuditLog

    # Ensure system calendar events exist
    sync_calendar_events()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')

        if action == 'smart_theme_config':
            shop.auto_theme_enabled = request.POST.get('auto_theme_enabled') == 'on'
            shop.normal_theme = request.POST.get('normal_theme', shop.normal_theme)
            shop.timezone = request.POST.get('timezone', shop.timezone)
            shop.country = request.POST.get('country', shop.country)
            shop.region = request.POST.get('region', shop.region)
            try:
                shop.pre_festival_days = int(request.POST.get('pre_festival_days', 3))
            except Exception:
                shop.pre_festival_days = 3
            shop.auto_category_theme_adaptation = request.POST.get('auto_category_theme_adaptation') == 'on'
            shop.save()
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Smart Theme Config Updated", details=f"Auto Theme: {shop.auto_theme_enabled}, Timezone: {shop.timezone}, Pre-Festival Days: {shop.pre_festival_days}")

        elif action == 'set_manual_override':
            override_theme = request.POST.get('manual_theme_override')
            duration = request.POST.get('override_duration', '1_day')
            local_now = get_shop_local_datetime(shop)

            until_dt = None
            if duration == '1_hour':
                until_dt = local_now + timedelta(hours=1)
            elif duration == '6_hours':
                until_dt = local_now + timedelta(hours=6)
            elif duration == '12_hours':
                until_dt = local_now + timedelta(hours=12)
            elif duration == '1_day':
                until_dt = local_now + timedelta(days=1)
            elif duration == 'until_custom':
                custom_str = request.POST.get('custom_until_date')
                if custom_str:
                    try:
                        until_dt = timezone.datetime.fromisoformat(custom_str)
                    except Exception:
                        until_dt = local_now + timedelta(days=1)

            prev_theme = shop.resolve_theme()
            shop.manual_theme_override = override_theme
            shop.override_until = until_dt
            shop.save()

            ThemeAuditLog.objects.create(
                shop=shop,
                previous_theme=prev_theme,
                new_theme=override_theme,
                reason=f"Manual Override set until {until_dt.strftime('%d %b %Y %H:%M') if until_dt else 'Indefinite'}"
            )
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Manual Theme Override Set", details=f"Overridden to {override_theme}")

        elif action == 'clear_manual_override':
            prev_theme = shop.resolve_theme()
            shop.manual_theme_override = None
            shop.override_until = None
            shop.save()

            new_res = get_active_shop_theme(shop)
            ThemeAuditLog.objects.create(
                shop=shop,
                previous_theme=prev_theme,
                new_theme=new_res.theme,
                reason="Manual Override Cleared by Owner"
            )
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Manual Theme Override Cleared", details=f"Returned to {new_res.theme}")

        elif action == 'reset':
            selected_theme = request.POST.get('theme', branding.theme)
            defaults = ShopBranding.get_theme_defaults(selected_theme)
            branding.theme = selected_theme
            branding.font_family = defaults.get('font_family', 'inter')
            branding.intensity = 'balanced'
            branding.primary_color = defaults.get('primary_color', '#6366f1')
            branding.secondary_color = defaults.get('secondary_color', '#4f46e5')
            branding.accent_color = defaults.get('accent_color', '#f59e0b')
            branding.background_color = defaults.get('background_color', '#0f172a')
            branding.text_color = defaults.get('text_color', '#f8fafc')
            branding.spin_button_text = defaults.get('spin_button_text', 'SPIN NOW')
            branding.save()
            ActivityLog.objects.create(shop=shop, actor=request.user, action="Branding Reset", details=f"Theme reset to defaults for {branding.theme}")
        else:
            selected_theme = request.POST.get('theme', branding.theme)
            branding.theme = selected_theme
            branding.font_family = request.POST.get('font_family', branding.font_family)
            branding.intensity = request.POST.get('intensity', branding.intensity or 'balanced')
            branding.primary_color = request.POST.get('primary_color', branding.primary_color)
            branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
            branding.accent_color = request.POST.get('accent_color', branding.accent_color)
            branding.background_color = request.POST.get('background_color', branding.background_color)
            branding.text_color = request.POST.get('text_color', branding.text_color)
            branding.spin_button_text = request.POST.get('spin_button_text', branding.spin_button_text)
            branding.save()

            # Keep shop normal_theme and all campaigns synchronized
            shop.normal_theme = selected_theme
            shop.save(update_fields=['normal_theme'])
            shop.campaigns.all().update(theme=selected_theme)

            ActivityLog.objects.create(shop=shop, actor=request.user, action="Branding Updated", details=f"Theme set to {branding.theme}")

        redirect_url = request.POST.get('next', 'update_branding')
        if redirect_url == 'shop_dashboard':
            return redirect('shop_dashboard')
        return redirect('update_branding')

    # Future Preview Date handling
    preview_date_str = request.GET.get('preview_date')
    preview_resolution = None
    if preview_date_str:
        try:
            p_date = timezone.datetime.strptime(preview_date_str, '%Y-%m-%d').date()
            p_dt = timezone.datetime.combine(p_date, timezone.datetime.min.time())
            preview_resolution = get_active_shop_theme(shop, target_datetime=p_dt)
        except Exception:
            pass

    from core.services.calendar_service import get_next_upcoming_festivals
    current_resolution = get_active_shop_theme(shop)
    today_dt = get_shop_local_datetime(shop)
    upcoming_events = get_next_upcoming_festivals(shop, limit=5)
    audit_logs = ThemeAuditLog.objects.filter(shop=shop).order_by('-timestamp')[:10]

    context = {
        'shop': shop,
        'branding': branding,
        'current_resolution': current_resolution,
        'preview_resolution': preview_resolution,
        'preview_date_str': preview_date_str,
        'upcoming_events': upcoming_events,
        'today_date': today_dt.date(),
        'audit_logs': audit_logs,
        'theme_choices': ShopBranding.THEME_CHOICES
    }

    return render(request, 'dashboard/branding.html', context)


@shop_access_required
def redeem_coupon_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    message = None
    error = None

    if request.method == 'POST':
        client_ip = get_client_ip(request)
        if not coupon_rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=60):
            error = "Rate limit exceeded. Please wait a moment before validating more coupons."
        else:
            code = request.POST.get('code', '').strip().upper()
            action = request.POST.get('action')

            if action == 'verify':
                try:
                    coupon = Coupon.objects.select_related('prize').get(code=code, shop=shop)
                    if coupon.status == 'redeemed':
                        error = f"Coupon {code} was ALREADY REDEEMED."
                    elif coupon.status == 'expired' or (coupon.expires_at and coupon.expires_at < timezone.now()):
                        error = f"Coupon {code} HAS EXPIRED."
                    elif coupon.status == 'cancelled':
                        error = f"Coupon {code} HAS BEEN CANCELLED."
                    else:
                        message = f"VALID COUPON: {coupon.prize.name} ({coupon.prize.coupon_text})"
                        recent_redemptions = CouponRedemption.objects.filter(coupon__shop=shop).select_related('coupon', 'coupon__prize', 'redeemed_by').order_by('-redeemed_at')[:15]
                        return render(request, 'dashboard/redeem.html', {'shop': shop, 'coupon': coupon, 'message': message, 'recent_redemptions': recent_redemptions})
                except Coupon.DoesNotExist:
                    other_shop_coupon = Coupon.objects.filter(code=code).select_related('shop').first()
                    if other_shop_coupon:
                        error = f"SECURITY REJECTION: Coupon '{code}' belongs to '{other_shop_coupon.shop.name}' and CANNOT be redeemed at '{shop.name}'!"
                    else:
                        error = f"Invalid Coupon Code '{code}' for shop {shop.name}."

            elif action == 'confirm_redeem':
                notes = request.POST.get('notes', '')
                try:
                    coupon = redeem_coupon_atomically(code=code, shop=shop, actor=request.user, notes=notes)
                    message = f"SUCCESS: Coupon {coupon.code} redeemed successfully!"
                except CouponRedemptionError as e:
                    error = e.message

    elif request.method == 'GET' and 'code' in request.GET:
        code_param = request.GET.get('code', '').strip().upper()
        if code_param:
            try:
                coupon = Coupon.objects.select_related('prize').get(code=code_param, shop=shop)
                if coupon.status == 'redeemed':
                    error = f"Coupon {code_param} was ALREADY REDEEMED."
                elif coupon.status == 'expired' or (coupon.expires_at and coupon.expires_at < timezone.now()):
                    error = f"Coupon {code_param} HAS EXPIRED."
                elif coupon.status == 'cancelled':
                    error = f"Coupon {code_param} HAS BEEN CANCELLED."
                else:
                    message = f"VALID COUPON: {coupon.prize.name} ({coupon.prize.coupon_text})"
                    recent_redemptions = CouponRedemption.objects.filter(coupon__shop=shop).select_related('coupon', 'coupon__prize', 'redeemed_by').order_by('-redeemed_at')[:15]
                    return render(request, 'dashboard/redeem.html', {'shop': shop, 'coupon': coupon, 'message': message, 'recent_redemptions': recent_redemptions})
            except Coupon.DoesNotExist:
                other_shop_coupon = Coupon.objects.filter(code=code_param).select_related('shop').first()
                if other_shop_coupon:
                    error = f"SECURITY REJECTION: Coupon '{code_param}' belongs to '{other_shop_coupon.shop.name}' and CANNOT be redeemed at '{shop.name}'!"
                else:
                    error = f"Invalid Coupon Code '{code_param}' for shop {shop.name}."

    recent_redemptions = CouponRedemption.objects.filter(coupon__shop=shop).select_related('coupon', 'coupon__prize', 'redeemed_by').order_by('-redeemed_at')[:15]
    return render(request, 'dashboard/redeem.html', {
        'shop': shop,
        'message': message,
        'error': error,
        'recent_redemptions': recent_redemptions
    })


@shop_access_required
def export_coupons_csv(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    safe_shop_name = sanitize_filename(shop.name, prefix="Coupons")
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{safe_shop_name}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Coupon Code', 'Prize Name', 'Status', 'Issued Date', 'Expiry Date', 'Redeemed At'])

    # Stream query results using iterator to prevent excessive memory usage
    coupons = Coupon.objects.filter(shop=shop).select_related('prize', 'redemption').order_by('-created_at').iterator(chunk_size=1000)
    for c in coupons:
        redeemed_at_str = c.redemption.redeemed_at.strftime('%Y-%m-%d %H:%M') if hasattr(c, 'redemption') and c.redemption else ''
        writer.writerow([
            c.code,
            c.prize.name if c.prize else 'N/A',
            c.status,
            c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else '',
            c.expires_at.strftime('%Y-%m-%d') if c.expires_at else '',
            redeemed_at_str
        ])

    return response


@shop_access_required
def download_qr_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    try:
        qr_obj = generate_shop_qr(shop, request.build_absolute_uri('/'))
        if qr_obj and qr_obj.qr_image:
            safe_shop_name = sanitize_filename(shop.name, prefix="QR")
            qr_data = qr_obj.qr_image.read()
            response = HttpResponse(qr_data, content_type="image/png")
            response['Content-Disposition'] = f'attachment; filename="{safe_shop_name}.png"'
            return response
    except Exception as e:
        logger.error(f"Error reading QR image for download (shop={shop.id}): {e}", exc_info=True)

    return redirect('shop_dashboard')


@shop_access_required
def qr_poster_view(request):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    site_base = getattr(settings, 'SITE_URL', request.build_absolute_uri('/')).rstrip('/')
    qr_obj, _ = QRCode.objects.get_or_create(shop=shop, defaults={'target_url': f"{site_base}/s/{shop.public_token}/"})
    if not qr_obj.qr_image:
        generate_shop_qr(shop, site_base)

    return render(request, 'dashboard/qr_poster.html', {
        'shop': shop,
        'qr_code': qr_obj,
        'public_url': request.build_absolute_uri(f"/s/{shop.public_token}/")
    })


# ---------------------------------------------------------
# SUPER ADMIN DASHBOARD
# ---------------------------------------------------------

@superadmin_required
def admin_dashboard(request):
    search_q = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    shops_query = Shop.objects.select_related('owner').order_by('-created_at')

    if search_q:
        shops_query = shops_query.filter(
            Q(name__icontains=search_q) |
            Q(owner__username__icontains=search_q) |
            Q(owner__email__icontains=search_q) |
            Q(public_token__icontains=search_q) |
            Q(category__icontains=search_q)
        )

    paginator = Paginator(shops_query, 15)
    try:
        shops_page = paginator.page(page_number)
    except PageNotAnInteger:
        shops_page = paginator.page(1)
    except EmptyPage:
        shops_page = paginator.page(paginator.num_pages)

    total_shops = Shop.objects.count()
    total_spins = SpinResult.objects.count()
    total_coupons = Coupon.objects.count()
    total_redeemed = Coupon.objects.filter(status='redeemed').count()
    logs = ActivityLog.objects.select_related('shop', 'actor').order_by('-timestamp')[:20]

    context = {
        'shops': shops_page,
        'shops_page': shops_page,
        'paginator': paginator,
        'search_q': search_q,
        'total_shops': total_shops,
        'total_spins': total_spins,
        'total_coupons': total_coupons,
        'total_redeemed': total_redeemed,
        'logs': logs
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@superadmin_required
def admin_capacity_dashboard_view(request):
    """
    Real-Time System Capacity Dashboard.
    All metrics are live-measured from the actual running environment.
    No hardcoded fallbacks or estimates are used.
    """
    from core.services.capacity_engine import get_capacity_snapshot, run_isolated_benchmark

    # Check if an on-demand benchmark was triggered by the admin
    benchmark_results = None
    benchmark_triggered = False
    if request.method == 'POST' and request.POST.get('action') == 'run_benchmark':
        benchmark_triggered = True
        benchmark_results = run_isolated_benchmark()

    # Collect live telemetry snapshot (always runs)
    snapshot = get_capacity_snapshot()

    context = {
        'snapshot': snapshot,
        'environment': snapshot['environment'],
        'hardware': snapshot['hardware'],
        'database': snapshot['database'],
        'app_counts': snapshot['app_counts'],
        'health_status': snapshot['health_status'],
        'collected_at': snapshot['collected_at'],
        # Benchmark results (only present when explicitly triggered)
        'benchmark_triggered': benchmark_triggered,
        'benchmark_results': benchmark_results,
        # Legacy keys kept for backward compat with any external templates referencing them
        'db_size_mb': snapshot['database'].get('db_size_mb'),
        'disk_used_percent': snapshot['hardware'].get('disk_used_percent'),
        'disk_free_gb': snapshot['hardware'].get('disk_free_gb'),
        'counts': {
            'shops': snapshot['app_counts']['shops'],
            'campaigns': snapshot['app_counts']['campaigns'],
            'prizes': snapshot['app_counts']['prizes'],
            'coupons': snapshot['app_counts']['coupons_total'],
            'spins': snapshot['app_counts']['spins'],
            'qr_scans': snapshot['app_counts']['qr_scans'],
            'redemptions': snapshot['app_counts']['coupons_redeemed'],
        },
    }
    return render(request, 'dashboard/admin_capacity.html', context)


# ---------------------------------------------------------
# SUBSCRIPTIONS MANAGEMENT (SUPER ADMIN & SHOP OWNER)
# ---------------------------------------------------------

def get_or_create_shop_subscription(shop):
    if not hasattr(shop, 'subscription') or not shop.subscription:
        default_plan, _ = Plan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter Plan',
                'price_rupees': 499.00,
                'price_display': '₹499 / month',
                'billing_period_days': 30,
                'max_campaigns': 5,
                'max_active_campaigns': 2,
                'max_prizes_per_campaign': 8,
                'max_spins_per_month': 5000,
                'is_default': True,
                'is_active': True,
            }
        )
        sub = Subscription.objects.create(
            shop=shop,
            plan=default_plan,
            status='active',
            starts_at=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )
        return sub
    sub = shop.subscription
    sub.check_and_rollover_future_plan()
    return sub


@superadmin_required
def admin_subscriptions_view(request):
    """
    Comprehensive Subscriptions Management Console for Super Admin.
    Manage Plans (CRUD in ₹) & Shop Subscriptions (Assign, Renew, Extend, Status).
    """
    plans = Plan.objects.all().order_by('-is_default', 'price_rupees')
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    shops_query = Shop.objects.select_related('owner', 'subscription', 'subscription__plan').order_by('-created_at')

    now = timezone.now()
    if status_filter != 'all':
        if status_filter == 'active':
            shops_query = shops_query.filter(
                subscription__status='active',
                subscription__expires_at__gte=now
            )
        elif status_filter == 'expired':
            shops_query = shops_query.filter(
                Q(subscription__status='expired') | Q(subscription__expires_at__lt=now)
            )
        elif status_filter in ['trial', 'past_due', 'cancelled']:
            shops_query = shops_query.filter(subscription__status=status_filter)

    if search_q:
        shops_query = shops_query.filter(
            Q(name__icontains=search_q) |
            Q(owner__username__icontains=search_q) |
            Q(owner__email__icontains=search_q) |
            Q(public_token__icontains=search_q) |
            Q(subscription__plan__name__icontains=search_q)
        )

    paginator = Paginator(shops_query, 15)
    try:
        shops_page = paginator.page(page_number)
    except PageNotAnInteger:
        shops_page = paginator.page(1)
    except EmptyPage:
        shops_page = paginator.page(paginator.num_pages)

    # Ensure subscriptions exist for shops in the current paginated view only
    for s in shops_page.object_list:
        if not hasattr(s, 'subscription') or not s.subscription:
            get_or_create_shop_subscription(s)

    total_shops = Shop.objects.count()
    active_subs_count = Subscription.objects.filter(
        status__in=['active', 'trial'],
        expires_at__gte=now
    ).count()
    expired_subs_count = Subscription.objects.filter(
        Q(status='expired') | Q(expires_at__lt=now)
    ).count()

    # Calculate Monthly Recurring Revenue in ₹ via SQL aggregate
    mrr_agg = Subscription.objects.filter(
        status__in=['active', 'trial'],
        expires_at__gte=now
    ).aggregate(total_mrr=Sum('plan__price_rupees'))
    mrr_rupees = mrr_agg.get('total_mrr') or 0.0

    return render(request, 'dashboard/admin_subscriptions.html', {
        'plans': plans,
        'shops': shops_page,
        'shop_subscriptions': shops_page,
        'shops_page': shops_page,
        'paginator': paginator,
        'all_shops_list': Shop.objects.only('id', 'name', 'owner__username').select_related('owner').order_by('name'),
        'total_shops': total_shops,
        'active_subs_count': active_subs_count,
        'expired_subs_count': expired_subs_count,
        'mrr_rupees': int(mrr_rupees),
        'status_filter': status_filter,
        'search_q': search_q
    })


@require_POST
@superadmin_required
def admin_plan_save_view(request):
    """Create or update a subscription plan in ₹ (Rupees) with Monthly/Yearly/Custom & Trial Mode"""
    plan_id = request.POST.get('plan_id')
    name = request.POST.get('name', '').strip()
    code = request.POST.get('code', '').strip().lower()
    price_rupees = request.POST.get('price_rupees', '0')
    billing_cycle = request.POST.get('billing_cycle')
    billing_period_days = request.POST.get('billing_period_days', '30')
    trial_days = request.POST.get('trial_days', '0')
    description = request.POST.get('description', '').strip()
    max_campaigns = request.POST.get('max_campaigns', '5')
    max_active_campaigns = request.POST.get('max_active_campaigns', '1')
    max_prizes = request.POST.get('max_prizes_per_campaign', '8')
    max_spins = request.POST.get('max_spins_per_month', '5000')
    is_default = request.POST.get('is_default') == 'on'
    is_active = request.POST.get('is_active', 'on') == 'on'

    price_rupees_val = parse_decimal_safe(price_rupees, default='499.00', min_val=Decimal('0.00'), max_val=Decimal('99999999.99'))
    trial_days_val = parse_int_safe(trial_days, default=0, min_val=0)
    billing_days_val = parse_int_safe(billing_period_days, default=30, min_val=1)
    max_campaigns_val = parse_int_safe(max_campaigns, default=5, min_val=1)
    max_active_campaigns_val = parse_int_safe(max_active_campaigns, default=1, min_val=1)
    max_prizes_val = parse_int_safe(max_prizes, default=8, min_val=1)
    max_spins_val = parse_int_safe(max_spins, default=5000, min_val=1)

    if not billing_cycle:
        if billing_days_val == 365:
            billing_cycle = 'yearly'
        elif billing_days_val == 30:
            billing_cycle = 'monthly'
        else:
            billing_cycle = 'custom'
    elif billing_cycle == 'yearly':
        billing_days_val = 365
    elif billing_cycle == 'monthly':
        billing_days_val = 30

    if is_default:
        Plan.objects.filter(is_default=True).update(is_default=False)

    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
        plan.name = name
        if code:
            plan.code = code
        plan.price_rupees = price_rupees_val
        plan.billing_cycle = billing_cycle
        plan.billing_period_days = billing_days_val
        plan.trial_days = trial_days_val
        plan.price_display = plan.formatted_price()
        plan.description = description
        plan.max_campaigns = max_campaigns_val
        plan.max_active_campaigns = max_active_campaigns_val
        plan.max_prizes_per_campaign = max_prizes_val
        plan.max_spins_per_month = max_spins_val
        plan.is_default = is_default
        plan.is_active = is_active
        plan.save()
    else:
        if not code:
            code = name.lower().replace(' ', '_')
        base_code = code
        counter = 1
        while Plan.objects.filter(code=code).exists():
            code = f"{base_code}_{counter}"
            counter += 1

        plan = Plan(
            name=name,
            code=code,
            price_rupees=price_rupees_val,
            billing_cycle=billing_cycle,
            billing_period_days=billing_days_val,
            trial_days=trial_days_val,
            description=description,
            max_campaigns=max_campaigns_val,
            max_active_campaigns=max_active_campaigns_val,
            max_prizes_per_campaign=max_prizes_val,
            max_spins_per_month=max_spins_val,
            is_default=is_default,
            is_active=is_active
        )
        plan.price_display = plan.formatted_price()
        plan.save()
        plan.price_display = plan.formatted_price()
        plan.save()

    return redirect('admin_subscriptions')


@require_POST
@superadmin_required
def admin_plan_delete_view(request, plan_id):
    """Safe plan deletion with subscription reassignment"""
    plan = get_object_or_404(Plan, id=plan_id)
    default_plan = Plan.objects.exclude(id=plan.id).filter(is_default=True).first()
    if not default_plan:
        default_plan = Plan.objects.exclude(id=plan.id).first()

    if default_plan:
        Subscription.objects.filter(plan=plan).update(plan=default_plan)

    plan.delete()
    return redirect('admin_subscriptions')


@require_POST
@superadmin_required
def admin_subscription_assign_view(request):
    shop_id = request.POST.get('shop_id')
    plan_id = request.POST.get('plan_id')
    status = request.POST.get('status', 'active')
    duration_days = request.POST.get('duration_days')
    notes = request.POST.get('notes', '').strip()
    schedule_mode = request.POST.get('schedule_mode', 'immediate')

    shop = get_object_or_404(Shop, id=shop_id)
    plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

    sub, _ = Subscription.objects.get_or_create(shop=shop)
    now = timezone.now()

    if schedule_mode == 'queue_future' and plan:
        # Schedule as future plan starting when current active plan ends
        try:
            days = int(duration_days) if duration_days else (plan.billing_period_days if plan else 30)
        except ValueError:
            days = 30
        sub.schedule_future_plan(plan, duration_days=days, notes=notes)
        ActivityLog.objects.create(
            shop=shop,
            actor=request.user,
            action="Future Plan Scheduled",
            details=f"Scheduled {plan.name} to activate on {sub.future_starts_at.strftime('%d %b %Y')} until {sub.future_expires_at.strftime('%d %b %Y')}."
        )
        messages.success(request, f"Scheduled {plan.name} for {shop.name}! It will automatically activate on {sub.future_starts_at.strftime('%d %b %Y')} when current plan ends.")
        return redirect('admin_subscriptions')

    if plan:
        sub.plan = plan

    if status == 'trial':
        try:
            days = int(duration_days) if duration_days else (plan.trial_days if (plan and plan.trial_days > 0) else 7)
        except ValueError:
            days = 7
        sub.starts_at = now
        sub.expires_at = now + timezone.timedelta(days=days)
        sub.status = 'trial'
        sub.is_active = True

    elif status == 'expired':
        sub.status = 'expired'
        sub.is_active = False
        sub.expires_at = now - timezone.timedelta(minutes=1)

    else: # active or cancelled
        try:
            days = int(duration_days) if duration_days else (plan.billing_period_days if plan else 30)
        except ValueError:
            days = 30
        base_date = sub.expires_at if (sub.expires_at and sub.expires_at > now) else now
        sub.starts_at = now
        sub.expires_at = base_date + timezone.timedelta(days=days)
        sub.status = status
        sub.is_active = (status == 'active')

    if notes:
        sub.notes = notes
    sub.save()

    ActivityLog.objects.create(
        shop=shop,
        actor=request.user,
        action="Subscription Assigned / Updated",
        details=f"Plan: {sub.plan.name if sub.plan else 'Custom'}, Status: {sub.status}, Expires: {sub.expires_at.strftime('%d %b %Y %H:%M') if sub.expires_at else 'Instant Expire'}"
    )

    messages.success(request, f"Subscription for {shop.name} successfully updated to {sub.plan.name if sub.plan else 'Custom'}.")
    return redirect('admin_subscriptions')


@require_POST
@superadmin_required
def admin_subscription_status_view(request, sub_id):
    """Update subscription status, trigger instant expire, trial, extend, activate queued future plan, or cancel future queue"""
    sub = get_object_or_404(Subscription, id=sub_id)
    action = request.POST.get('action')
    now = timezone.now()

    if action in ['expire', 'instant_expire']:
        sub.status = 'expired'
        sub.is_active = False
        sub.expires_at = now - timezone.timedelta(minutes=1)
        sub.save()
        messages.info(request, f"Subscription for {sub.shop.name} has been expired.")

    elif action == 'trial':
        try:
            t_days = int(request.POST.get('trial_days', 7))
        except ValueError:
            t_days = 7
        sub.status = 'trial'
        sub.is_active = True
        sub.starts_at = now
        sub.expires_at = now + timezone.timedelta(days=t_days)
        sub.save()
        messages.success(request, f"Trial activated for {sub.shop.name} ({t_days} days).")

    elif action == 'activate':
        days = sub.plan.billing_period_days if sub.plan else 30
        sub.status = 'active'
        sub.is_active = True
        sub.starts_at = now
        sub.expires_at = now + timezone.timedelta(days=days)
        sub.save()
        messages.success(request, f"Plan activated for {sub.shop.name}.")

    elif action == 'cancel':
        sub.status = 'cancelled'
        sub.is_active = False
        sub.save()
        messages.info(request, f"Subscription for {sub.shop.name} cancelled.")

    elif action == 'extend':
        try:
            extra_days = int(request.POST.get('extra_days', 30))
        except ValueError:
            extra_days = 30
        base_date = sub.expires_at if (sub.expires_at and sub.expires_at > now) else now
        sub.expires_at = base_date + timezone.timedelta(days=extra_days)
        sub.status = 'active'
        sub.is_active = True
        sub.save()
        messages.success(request, f"Extended {sub.shop.name} subscription by +{extra_days} days until {sub.expires_at.strftime('%d %b %Y')}.")

    elif action == 'activate_future_now':
        if sub.future_plan:
            queued_plan = sub.future_plan
            days = queued_plan.billing_period_days or 30
            sub.plan = queued_plan
            sub.starts_at = now
            sub.expires_at = now + timezone.timedelta(days=days)
            sub.status = 'active'
            sub.is_active = True
            sub.cancel_future_plan()
            sub.save()
            ActivityLog.objects.create(
                shop=sub.shop,
                actor=request.user,
                action="Queued Plan Activated Immediately",
                details=f"Promoted {queued_plan.name} to active immediately until {sub.expires_at.strftime('%d %b %Y')}."
            )
            messages.success(request, f"Promoted scheduled plan {queued_plan.name} to active immediately for {sub.shop.name}!")

    elif action == 'cancel_future':
        if sub.future_plan:
            queued_name = sub.future_plan.name
            sub.cancel_future_plan()
            ActivityLog.objects.create(
                shop=sub.shop,
                actor=request.user,
                action="Scheduled Future Plan Cancelled",
                details=f"Cancelled queued future plan {queued_name}."
            )
            messages.info(request, f"Cancelled scheduled future plan ({queued_name}) for {sub.shop.name}.")

    ActivityLog.objects.create(
        shop=sub.shop,
        actor=request.user,
        action="Subscription Status Changed",
        details=f"Action: {action}, New Status: {sub.status}, Expires: {sub.expires_at.strftime('%d %b %Y %H:%M') if sub.expires_at else 'N/A'}"
    )

    return redirect('admin_subscriptions')


# ---------------------------------------------------------
# ADMIN PLAN REQUESTS MANAGEMENT CENTER
# ---------------------------------------------------------

@superadmin_required
def admin_plan_requests_view(request):
    """
    Dedicated Plan Upgrade & Subscription Requests review center for Super Admin.
    Allows viewing all incoming tenant plan requests with full details and 1-click Approval/Rejection.
    """
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()

    reqs_query = PlanRequest.objects.select_related('shop', 'shop__owner', 'plan', 'reviewed_by').order_by('-created_at')

    if status_filter in ['pending', 'approved', 'rejected']:
        reqs_query = reqs_query.filter(status=status_filter)

    if search_q:
        reqs_query = reqs_query.filter(
            Q(shop__name__icontains=search_q) |
            Q(shop__owner__username__icontains=search_q) |
            Q(shop__owner__email__icontains=search_q) |
            Q(plan__name__icontains=search_q) |
            Q(contact_phone__icontains=search_q)
        )

    pending_count = PlanRequest.objects.filter(status='pending').count()
    approved_count = PlanRequest.objects.filter(status='approved').count()
    rejected_count = PlanRequest.objects.filter(status='rejected').count()
    total_count = PlanRequest.objects.count()

    paginator = Paginator(reqs_query, 15)
    page_number = request.GET.get('page', 1)
    try:
        reqs_page = paginator.page(page_number)
    except PageNotAnInteger:
        reqs_page = paginator.page(1)
    except EmptyPage:
        reqs_page = paginator.page(paginator.num_pages)

    context = {
        'requests': reqs_page,
        'status_filter': status_filter,
        'search_q': search_q,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
    }
    return render(request, 'dashboard/admin_plan_requests.html', context)


@require_POST
@superadmin_required
def admin_plan_request_action_view(request, request_id):
    """
    1-Click Approve & Activate or Reject incoming shop plan request.
    When approved, subscription expiration is extended by the requested plan's duration
    on top of the current active expiration (exceed by more days), with full limitations included.
    """
    plan_req = get_object_or_404(PlanRequest, id=request_id)
    action = request.POST.get('action')

    if action == 'approve':
        plan_req.status = 'approved'
        plan_req.reviewed_at = timezone.now()
        plan_req.reviewed_by = request.user
        plan_req.save()

        sub = plan_req.shop.get_subscription()
        now = timezone.now()
        days = plan_req.plan.billing_period_days if plan_req.plan.billing_period_days else 30
        activation_mode = request.POST.get('activation_mode', 'scheduled')

        is_currently_active = sub.is_valid() and sub.expires_at and sub.expires_at > now

        if is_currently_active and activation_mode != 'immediate':
            # Current plan is still active (e.g. ₹499 plan expires 5th Sep).
            # The shop owner keeps accessing ONLY the current plan's quotas until 5th Sep.
            # The approved plan is scheduled as a future plan starting on 5th Sep!
            sub.schedule_future_plan(
                new_plan=plan_req.plan,
                starts_at=sub.expires_at,
                duration_days=days,
                notes=f"Approved {plan_req.get_request_type_display()} Request #{plan_req.id}"
            )

            type_str = "Renewal" if plan_req.request_type == 'renewal' else "Upgrade"
            Notification.objects.create(
                shop=plan_req.shop,
                user=plan_req.shop.owner,
                title=f"Plan {type_str} Approved & Scheduled 📅",
                message=f"Your request for {plan_req.plan.name} ({plan_req.plan.formatted_price()}) has been approved! Your current plan remains active with its current limits until {sub.expires_at.strftime('%d %b %Y')}. On that day, your new {plan_req.plan.name} will automatically activate with all its limits until {sub.future_expires_at.strftime('%d %b %Y')}.",
                level='success'
            )
            ActivityLog.objects.create(
                shop=plan_req.shop,
                actor=request.user,
                action=f"Plan {type_str} Approved & Scheduled",
                details=f"Scheduled {plan_req.plan.name} for {plan_req.shop.name} to activate automatically on {sub.future_starts_at.strftime('%d %b %Y')} until {sub.future_expires_at.strftime('%d %b %Y')}."
            )
            messages.success(
                request,
                f"Approved and scheduled {plan_req.plan.name} for {plan_req.shop.name}! Current plan stays active until {sub.expires_at.strftime('%d %b %Y')}, new plan activates automatically on that day until {sub.future_expires_at.strftime('%d %b %Y')}."
            )

        else:
            # Current plan was already expired OR admin explicitly selected immediate activation
            sub.plan = plan_req.plan
            sub.status = 'active'
            sub.is_active = True
            sub.starts_at = now
            sub.expires_at = now + timezone.timedelta(days=days)
            sub.cancel_future_plan()
            sub.save()

            type_str = "Renewal" if plan_req.request_type == 'renewal' else "Upgrade"
            Notification.objects.create(
                shop=plan_req.shop,
                user=plan_req.shop.owner,
                title=f"Plan {type_str} Activated Immediately 🎉",
                message=f"Your request for {plan_req.plan.name} ({plan_req.plan.formatted_price()}) has been approved and activated immediately! Active until {sub.expires_at.strftime('%d %b %Y')}. All plan features and limitations ({plan_req.plan.max_campaigns} campaigns, {plan_req.plan.max_spins_per_month} spins/mo) are now active.",
                level='success'
            )
            ActivityLog.objects.create(
                shop=plan_req.shop,
                actor=request.user,
                action=f"Plan {type_str} Activated Immediately",
                details=f"Activated {plan_req.plan.name} immediately for {plan_req.shop.name} until {sub.expires_at.strftime('%d %b %Y')}."
            )
            messages.success(
                request,
                f"Approved and activated {plan_req.plan.name} immediately for {plan_req.shop.name} (active until {sub.expires_at.strftime('%d %b %Y')})."
            )

    elif action == 'reject':
        plan_req.status = 'rejected'
        plan_req.reviewed_at = timezone.now()
        plan_req.reviewed_by = request.user
        plan_req.save()

        Notification.objects.create(
            shop=plan_req.shop,
            user=plan_req.shop.owner,
            title="Plan Request Update",
            message=f"Your request for {plan_req.plan.name} was not approved at this time. Please contact support.",
            level='warning'
        )
        ActivityLog.objects.create(
            shop=plan_req.shop,
            actor=request.user,
            action="Plan Request Rejected",
            details=f"Rejected request for {plan_req.plan.name} from {plan_req.shop.name}."
        )
        messages.info(request, f"Request for {plan_req.shop.name} has been rejected.")

    return redirect('admin_plan_requests')


@require_POST
@shop_access_required
def subscription_renew_view(request):
    """Shop owner renews or upgrades their subscription plan"""
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    plan_id = request.POST.get('plan_id')
    plan = get_object_or_404(Plan, id=plan_id)

    # In Demo plan, there must NOT be renew current plan option
    if plan.code == 'demo':
        messages.error(request, "The Demo plan is for initial trial only and cannot be renewed. Please request an upgrade plan.")
        return redirect('billing')

    sub = get_or_create_shop_subscription(shop)
    sub.renew(plan=plan)

    ActivityLog.objects.create(
        shop=shop,
        actor=request.user,
        action="Subscription Renewed",
        details=f"Renewed on {plan.name} ({plan.price_display}) for {plan.billing_period_days} days."
    )
    messages.success(request, f"Successfully renewed on {plan.name}!")
    return redirect('billing')


@require_POST
@shop_access_required
def request_plan_view(request):
    """Shop owner submits a request to activate or upgrade to a subscription plan"""
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    if not shop:
        return redirect('admin_dashboard')

    plan_id = request.POST.get('plan_id')
    target_plan = get_object_or_404(Plan, id=plan_id)
    notes = request.POST.get('notes', '').strip()
    phone = request.POST.get('contact_phone', shop.phone or getattr(request.user, 'phone', '') or '').strip()

    if target_plan.code == 'demo':
        messages.error(request, "The Demo plan is for initial trial only and cannot be requested.")
        return redirect('billing')

    current_sub = shop.get_subscription()
    req_type = 'renewal' if (current_sub.plan and current_sub.plan.id == target_plan.id) else 'upgrade'
    if request.POST.get('request_type'):
        req_type = request.POST.get('request_type')

    existing_req = PlanRequest.objects.filter(shop=shop, plan=target_plan, status='pending').first()
    if not existing_req:
        PlanRequest.objects.create(
            shop=shop,
            plan=target_plan,
            request_type=req_type,
            contact_phone=phone,
            notes=notes,
            status='pending'
        )
        type_label = "Renewal" if req_type == 'renewal' else "Upgrade"
        for admin_user in User.objects.filter(role='super_admin'):
            Notification.objects.create(
                user=admin_user,
                title=f"Plan {type_label} Request: {shop.name}",
                message=f"{shop.name} has requested {type_label.lower()} for {target_plan.name} ({target_plan.formatted_price()}). Please review in Platform Admin.",
                level='info'
            )
        ActivityLog.objects.create(
            shop=shop,
            actor=request.user,
            action=f"Plan {type_label} Requested",
            details=f"Requested {type_label.lower()} to {target_plan.name} ({target_plan.formatted_price()})"
        )
        messages.success(request, f"Your {type_label.lower()} request for {target_plan.name} has been submitted! Platform admin has been notified and will review your request.")
    else:
        messages.info(request, f"You already have a pending request for {target_plan.name}. We will review and activate it shortly.")

    return redirect('billing')


def onboarding_view(request):
    """
    Setup Wizard for Business Creation and Shop Onboarding.
    Supports:
    1. Complete Business Creation: Creates new User (Shop Owner credentials with password & confirm password),
       Shop profile, ShopBranding, Subscription plan, initial Campaign & Prizes, and permanent QR code.
    2. Password Management: Password and confirm password fields with strength & matching validation.
    3. Existing Shop Configuration: Allows existing shop owners or admins to customize details, branding,
       offers, and launch permanent QR codes.
    """
    mode = request.GET.get('mode', '').strip()
    shop_id = request.GET.get('shop_id', '').strip()

    is_create_mode = False
    shop = None

    if not request.user.is_authenticated:
        # Public merchant signup / business creation
        is_create_mode = True
    elif request.user.is_superadmin():
        if shop_id:
            shop = get_object_or_404(Shop, id=shop_id)
            is_create_mode = (mode == 'create')
        elif mode == 'create' or not request.user.shop:
            is_create_mode = True
        else:
            is_create_mode = (mode == 'create')
            shop = request.user.shop or Shop.objects.first()
    else:
        # Logged-in shop owner
        shop = request.user.shop
        is_create_mode = (mode == 'create' and not shop)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # -------------------------------------------------------------
        # 1. ACTION: CREATE BUSINESS (Complete Multi-Step Wizard Submission)
        # -------------------------------------------------------------
        if action == 'create_business':
            # Extract Credentials
            owner_username = request.POST.get('owner_username', '').strip()
            owner_password = request.POST.get('owner_password', '').strip()
            owner_confirm_password = request.POST.get('owner_confirm_password', '').strip()
            owner_email = request.POST.get('owner_email', '').strip()
            owner_first_name = request.POST.get('owner_first_name', '').strip()
            owner_last_name = request.POST.get('owner_last_name', '').strip()
            owner_phone = request.POST.get('owner_phone', '').strip()

            # Extract Shop Profile
            shop_name = request.POST.get('shop_name', '').strip()
            category = request.POST.get('category', '').strip() or 'Retail & Store'
            currency_symbol = request.POST.get('currency_symbol', '₹').strip() or '₹'
            shop_phone = request.POST.get('shop_phone', '').strip() or owner_phone
            shop_email = request.POST.get('shop_email', '').strip() or owner_email
            address = request.POST.get('address', '').strip()
            timezone_val = request.POST.get('timezone', 'Asia/Kolkata').strip() or 'Asia/Kolkata'
            country = request.POST.get('country', 'IN').strip() or 'IN'
            region = request.POST.get('region', 'Gujarat').strip() or 'Gujarat'
            description = request.POST.get('description', '').strip()
            auto_theme_enabled = request.POST.get('auto_theme_enabled') in ('true', 'on', '1', True, 1)
            auto_category_adaptation = request.POST.get('auto_category_theme_adaptation') in ('true', 'on', '1', True, 1)
            try:
                pre_festival_days = int(request.POST.get('pre_festival_days', 3) or 3)
            except (ValueError, TypeError):
                pre_festival_days = 3

            # Extract Branding & Theme
            theme = request.POST.get('theme', 'royal').strip() or 'royal'
            font_family = request.POST.get('font_family', 'inter').strip() or 'inter'
            intensity = request.POST.get('intensity', 'balanced').strip() or 'balanced'
            primary_color = request.POST.get('primary_color', '').strip()
            secondary_color = request.POST.get('secondary_color', '').strip()
            accent_color = request.POST.get('accent_color', '').strip()
            background_color = request.POST.get('background_color', '').strip()
            spin_button_text = request.POST.get('spin_button_text', '').strip()
            pointer_style = request.POST.get('pointer_style', 'classic').strip() or 'classic'

            # Extract Subscription Plan
            plan_id = request.POST.get('plan_id')
            plan_code = request.POST.get('plan_code', 'starter').strip()
            billing_cycle = request.POST.get('billing_cycle', 'monthly').strip()

            # Extract Initial Campaign & Prizes
            campaign_name = request.POST.get('campaign_name', '').strip()
            welcome_title = request.POST.get('welcome_title', '').strip()
            welcome_subtitle = request.POST.get('welcome_subtitle', '').strip()
            try:
                spin_cooldown_hours = int(request.POST.get('spin_cooldown_hours', 24) or 24)
            except (ValueError, TypeError):
                spin_cooldown_hours = 24
            prizes_json = request.POST.get('prizes_json', '').strip()

            # Validation
            errors = []
            if not owner_username:
                errors.append("Username is required.")
            elif len(owner_username) < 3:
                errors.append("Username must be at least 3 characters long.")
            elif User.objects.filter(username__iexact=owner_username).exists():
                errors.append(f"Username '{owner_username}' is already taken. Please choose another username.")

            if not owner_password:
                errors.append("Password is required.")
            elif len(owner_password) < 8:
                errors.append("Password must be at least 8 characters long.")
            elif owner_password != owner_confirm_password:
                errors.append("Passwords do not match. Please re-enter matching passwords.")

            if not shop_name:
                errors.append("Business / Shop Name is required.")

            if errors:
                return JsonResponse({'status': 'error', 'message': errors[0], 'errors': errors}, status=400)

            # Atomic creation of user, shop, branding, plan, campaign, prizes, and QR
            try:
                with transaction.atomic():
                    # 1. Create User
                    new_user = User.objects.create_user(
                        username=owner_username,
                        email=owner_email,
                        password=owner_password,
                        first_name=owner_first_name,
                        last_name=owner_last_name,
                        role='shop_owner',
                        phone=owner_phone
                    )

                    # 2. Create Shop
                    new_shop = Shop.objects.create(
                        name=shop_name,
                        owner=new_user,
                        category=category,
                        currency_symbol=currency_symbol,
                        phone=shop_phone,
                        email=shop_email,
                        address=address,
                        timezone=timezone_val,
                        country=country,
                        region=region,
                        description=description,
                        auto_theme_enabled=auto_theme_enabled,
                        auto_category_theme_adaptation=auto_category_adaptation,
                        pre_festival_days=pre_festival_days,
                        normal_theme=theme,
                        onboarding_completed=True
                    )

                    new_user.shop = new_shop
                    new_user.save(update_fields=['shop'])

                    # 3. Create ShopBranding
                    theme_defs = ShopBranding.get_theme_defaults(theme)
                    branding, _ = ShopBranding.objects.get_or_create(shop=new_shop)
                    branding.theme = theme
                    branding.font_family = font_family or theme_defs.get('font_family', 'inter')
                    branding.intensity = intensity
                    branding.primary_color = primary_color or theme_defs.get('primary_color', '#6366f1')
                    branding.secondary_color = secondary_color or theme_defs.get('secondary_color', '#4f46e5')
                    branding.accent_color = accent_color or theme_defs.get('accent_color', '#f59e0b')
                    branding.background_color = background_color or theme_defs.get('background_color', '#0f172a')
                    branding.spin_button_text = spin_button_text or theme_defs.get('spin_button_text', 'SPIN NOW')
                    branding.pointer_style = pointer_style
                    branding.save()

                    # 4. Setup Subscription Plan
                    selected_plan = None
                    if plan_id:
                        selected_plan = Plan.objects.filter(id=plan_id, is_active=True).first()
                    elif plan_code:
                        selected_plan = Plan.objects.filter(code=plan_code, is_active=True).first()
                    if not selected_plan:
                        selected_plan = Plan.objects.filter(is_default=True, is_active=True).first() or Plan.objects.filter(is_active=True).first()

                    duration_days = 365 if billing_cycle == 'yearly' else (selected_plan.billing_period_days if selected_plan else 30)
                    sub = new_shop.get_subscription()
                    if selected_plan:
                        sub.plan = selected_plan
                    sub.status = 'active'
                    sub.starts_at = timezone.now()
                    sub.expires_at = timezone.now() + timedelta(days=duration_days)
                    sub.is_active = True
                    sub.save()

                    # 5. Create Initial Promotional Campaign
                    camp = Campaign.objects.create(
                        shop=new_shop,
                        name=campaign_name or f"{new_shop.name} Welcome Offer",
                        description=welcome_subtitle or "Spin the wheel for an instant discount voucher",
                        welcome_title=welcome_title or f"Welcome to {new_shop.name}!",
                        welcome_subtitle=welcome_subtitle or "Spin the wheel to unlock your exclusive instant reward",
                        spin_button_text=branding.spin_button_text or "SPIN NOW",
                        start_date=timezone.now() - timedelta(hours=1),
                        end_date=timezone.now() + timedelta(days=365),
                        status='live',
                        is_active=True,
                        spin_cooldown_hours=spin_cooldown_hours,
                        theme=theme
                    )

                    # 6. Create Prizes (parse from prizes_json or default set)
                    prizes_data = []
                    if prizes_json:
                        try:
                            prizes_data = json.loads(prizes_json)
                        except Exception:
                            prizes_data = []

                    if not prizes_data:
                        prizes_data = [
                            {'name': '10% OFF Bill', 'prize_type': 'percentage', 'discount_percentage': Decimal('10.00'), 'fixed_discount_amount': Decimal('0.00'), 'coupon_text': '10% off your purchase', 'probability': 40.0, 'remaining_quantity': 200, 'display_color': branding.primary_color},
                            {'name': f'Flat {currency_symbol}100 OFF', 'prize_type': 'fixed', 'discount_percentage': Decimal('0.00'), 'fixed_discount_amount': Decimal('100.00'), 'coupon_text': f'{currency_symbol}100 discount on your bill', 'probability': 25.0, 'remaining_quantity': 100, 'display_color': branding.accent_color},
                            {'name': 'Complimentary Gift', 'prize_type': 'freebie', 'discount_percentage': Decimal('0.00'), 'fixed_discount_amount': Decimal('0.00'), 'coupon_text': 'Free surprise gift with order', 'probability': 15.0, 'remaining_quantity': 50, 'display_color': branding.secondary_color},
                            {'name': 'Better Luck Next Time', 'prize_type': 'no_win', 'discount_percentage': Decimal('0.00'), 'fixed_discount_amount': Decimal('0.00'), 'coupon_text': 'Thank you for playing', 'probability': 20.0, 'remaining_quantity': 500, 'display_color': '#64748b'},
                        ]

                    for p in prizes_data:
                        Prize.objects.create(
                            campaign=camp,
                            name=str(p.get('name', 'Special Reward')).strip(),
                            prize_type=p.get('prize_type', 'percentage'),
                            discount_percentage=parse_decimal_safe(p.get('discount_percentage'), default='0.00', min_val=Decimal('0.00'), max_val=Decimal('100.00')),
                            fixed_discount_amount=parse_decimal_safe(p.get('fixed_discount_amount'), default='0.00', min_val=Decimal('0.00'), max_val=Decimal('99999999.99')),
                            coupon_text=str(p.get('coupon_text', '') or f"Reward: {p.get('name')}").strip(),
                            probability=parse_float_safe(p.get('probability'), default=25.0, min_val=0.0, max_val=100.0),
                            remaining_quantity=parse_int_safe(p.get('remaining_quantity'), default=200, min_val=0),
                            max_wins=parse_int_safe(p.get('max_wins', p.get('remaining_quantity', 200)), default=200, min_val=0),
                            display_color=str(p.get('display_color', branding.primary_color)).strip()
                        )

                    # 7. Generate Permanent High-DPI QR Code
                    qr_obj = generate_shop_qr(new_shop)

                    # 8. Log Activity
                    actor_user = request.user if request.user.is_authenticated else new_user
                    ActivityLog.objects.create(
                        shop=new_shop,
                        actor=actor_user,
                        action="Business Created via Setup Wizard",
                        details=f"Created store '{new_shop.name}' with owner '{new_user.username}', plan '{selected_plan.name if selected_plan else 'Starter'}'"
                    )

                # Auto login if unauthenticated merchant
                if not request.user.is_authenticated:
                    login(request, new_user)

                qr_url = qr_obj.qr_image.url if (qr_obj and qr_obj.qr_image) else ''
                store_url = qr_obj.target_url if qr_obj else f"/s/{new_shop.public_token}/"
                dashboard_url = f"/dashboard/shop/?shop_id={new_shop.id}" if (request.user.is_authenticated and request.user.is_superadmin()) else "/dashboard/shop/"

                return JsonResponse({
                    'status': 'success',
                    'message': f"Business '{new_shop.name}' created successfully!",
                    'shop_id': new_shop.id,
                    'shop_name': new_shop.name,
                    'public_token': new_shop.public_token,
                    'qr_url': qr_url,
                    'store_url': store_url,
                    'username': new_user.username,
                    'password': owner_password,
                    'dashboard_url': dashboard_url
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f"Failed to create business: {str(e)}"}, status=500)

        # -------------------------------------------------------------
        # 2. ACTION: SAVE CREDENTIALS / UPDATE PASSWORD (Existing Owner)
        # -------------------------------------------------------------
        elif action == 'save_credentials':
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            new_email = request.POST.get('email', '').strip()
            new_phone = request.POST.get('phone', '').strip()

            target_user = request.user
            if shop and shop.owner and request.user.is_superadmin():
                target_user = shop.owner

            if new_password:
                if len(new_password) < 8:
                    return JsonResponse({'status': 'error', 'message': 'Password must be at least 8 characters long.'}, status=400)
                if new_password != confirm_password:
                    return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'}, status=400)
                target_user.set_password(new_password)

            if new_email:
                target_user.email = new_email
            if new_phone:
                target_user.phone = new_phone
            target_user.save()

            if target_user == request.user and new_password:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, target_user)

            if shop:
                ActivityLog.objects.create(
                    shop=shop,
                    actor=request.user,
                    action="Onboarding: Security Credentials Updated",
                    details=f"Updated credentials for user '{target_user.username}'"
                )

            return JsonResponse({'status': 'success', 'message': 'Security credentials updated successfully!'})

        # -------------------------------------------------------------
        # 3. ACTION: SAVE SHOP DETAILS (Backward Compatible)
        # -------------------------------------------------------------
        elif action == 'save_shop':
            if not shop:
                shop = request.user.shop or (Shop.objects.first() if request.user.is_superadmin() else None)
            if not shop:
                return JsonResponse({'status': 'error', 'message': 'No shop selected.'}, status=400)

            shop.name = request.POST.get('name', request.POST.get('shop_name', shop.name))
            shop.category = request.POST.get('category', shop.category)
            shop.currency_symbol = request.POST.get('currency_symbol', shop.currency_symbol)
            if 'phone' in request.POST or 'shop_phone' in request.POST:
                shop.phone = request.POST.get('phone', request.POST.get('shop_phone', shop.phone))
            if 'email' in request.POST or 'shop_email' in request.POST:
                shop.email = request.POST.get('email', request.POST.get('shop_email', shop.email))
            if 'address' in request.POST:
                shop.address = request.POST.get('address', shop.address)
            if 'timezone' in request.POST:
                shop.timezone = request.POST.get('timezone', shop.timezone)
            if 'country' in request.POST:
                shop.country = request.POST.get('country', shop.country)
            if 'region' in request.POST:
                shop.region = request.POST.get('region', shop.region)
            shop.save()

            ActivityLog.objects.create(shop=shop, actor=request.user, action="Onboarding: Shop Details Saved", details=f"Updated details for {shop.name}")
            return JsonResponse({'status': 'success', 'message': 'Shop details saved!'})

        # -------------------------------------------------------------
        # 4. ACTION: SAVE BRANDING (Backward Compatible)
        # -------------------------------------------------------------
        elif action == 'save_branding':
            if not shop:
                shop = request.user.shop or (Shop.objects.first() if request.user.is_superadmin() else None)
            if not shop:
                return JsonResponse({'status': 'error', 'message': 'No shop selected.'}, status=400)

            branding, _ = ShopBranding.objects.get_or_create(shop=shop)
            theme_choice = request.POST.get('theme', branding.theme)
            branding.theme = theme_choice
            branding.font_family = request.POST.get('font_family', branding.font_family)
            branding.primary_color = request.POST.get('primary_color', branding.primary_color)
            if 'intensity' in request.POST:
                branding.intensity = request.POST.get('intensity', branding.intensity)
            if 'secondary_color' in request.POST:
                branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
            if 'accent_color' in request.POST:
                branding.accent_color = request.POST.get('accent_color', branding.accent_color)
            if 'background_color' in request.POST:
                branding.background_color = request.POST.get('background_color', branding.background_color)
            if 'spin_button_text' in request.POST:
                branding.spin_button_text = request.POST.get('spin_button_text', branding.spin_button_text)
            branding.save()

            shop.normal_theme = theme_choice
            shop.save(update_fields=['normal_theme'])

            ActivityLog.objects.create(shop=shop, actor=request.user, action="Onboarding: Branding Saved", details=f"Theme set to {branding.theme}")
            return JsonResponse({'status': 'success', 'message': 'Branding theme saved!'})

        # -------------------------------------------------------------
        # 5. ACTION: SAVE CAMPAIGN & PRIZES
        # -------------------------------------------------------------
        elif action == 'save_campaign':
            if not shop:
                shop = request.user.shop or (Shop.objects.first() if request.user.is_superadmin() else None)
            if not shop:
                return JsonResponse({'status': 'error', 'message': 'No shop selected.'}, status=400)

            campaign = shop.get_active_campaign()
            if not campaign:
                campaign = Campaign.objects.create(
                    shop=shop,
                    name=request.POST.get('campaign_name', f"{shop.name} Promotion"),
                    welcome_title=request.POST.get('welcome_title', f"Welcome to {shop.name}!"),
                    welcome_subtitle=request.POST.get('welcome_subtitle', "Spin to win"),
                    start_date=timezone.now() - timedelta(hours=1),
                    end_date=timezone.now() + timedelta(days=365),
                    status='live',
                    is_active=True
                )
            else:
                if 'campaign_name' in request.POST:
                    campaign.name = request.POST.get('campaign_name', campaign.name)
                if 'welcome_title' in request.POST:
                    campaign.welcome_title = request.POST.get('welcome_title', campaign.welcome_title)
                if 'welcome_subtitle' in request.POST:
                    campaign.welcome_subtitle = request.POST.get('welcome_subtitle', campaign.welcome_subtitle)
                if 'spin_cooldown_hours' in request.POST:
                    try:
                        campaign.spin_cooldown_hours = int(request.POST.get('spin_cooldown_hours', campaign.spin_cooldown_hours))
                    except (ValueError, TypeError):
                        pass
                campaign.save()

            ActivityLog.objects.create(shop=shop, actor=request.user, action="Onboarding: Campaign Saved", details=f"Updated offer: {campaign.name}")
            return JsonResponse({'status': 'success', 'message': 'Campaign offer saved!'})

        # -------------------------------------------------------------
        # 6. ACTION: COMPLETE ONBOARDING (Backward Compatible)
        # -------------------------------------------------------------
        elif action == 'complete':
            if not shop:
                shop = request.user.shop or (Shop.objects.first() if request.user.is_superadmin() else None)
            if shop:
                shop.onboarding_completed = True
                shop.save()
                generate_shop_qr(shop)
                ActivityLog.objects.create(shop=shop, actor=request.user, action="Onboarding Completed", details="Shop onboarding wizard launched successfully.")

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Onboarding complete!', 'redirect_url': '/dashboard/shop/'})
            return redirect('shop_dashboard')

    # GET Request: Prepare Context
    if not shop and not is_create_mode:
        if request.user.is_authenticated:
            shop = request.user.shop or (Shop.objects.first() if request.user.is_superadmin() else None)
            if not shop:
                is_create_mode = True
        else:
            is_create_mode = True

    branding = None
    campaign = None
    if shop:
        branding, _ = ShopBranding.objects.get_or_create(shop=shop)
        campaign = shop.get_active_campaign()

    plans = Plan.objects.filter(is_active=True).order_by('price_rupees')

    return render(request, 'dashboard/onboarding.html', {
        'shop': shop,
        'branding': branding,
        'campaign': campaign,
        'is_create_mode': is_create_mode,
        'plans': plans,
        'theme_choices': ShopBranding.THEME_CHOICES,
        'font_choices': ShopBranding.FONT_CHOICES,
        'intensity_choices': ShopBranding.INTENSITY_CHOICES,
    })


@shop_access_required
def billing_view(request):
    if request.user.is_superadmin():
        return redirect('admin_subscriptions')

    shop = request.user.shop
    if not shop:
        return redirect('admin_dashboard')

    sub = get_or_create_shop_subscription(shop)
    plan = sub.plan
    is_demo = (plan.code == 'demo') if plan else False

    # Compute actual SaaS usage metrics
    campaign_count = shop.campaigns.count()
    active_campaign_count = shop.campaigns.filter(is_active=True, status__in=['live', 'active']).count()
    spin_count = SpinResult.objects.filter(shop=shop).count()

    # User rule: "only show demo plan if activated else show other plans"
    all_plans_query = Plan.objects.filter(is_active=True).order_by('price_rupees')
    if is_demo:
        all_plans = all_plans_query
    else:
        all_plans = all_plans_query.exclude(code='demo')

    pending_plan_ids = set(shop.plan_requests.filter(status='pending').values_list('plan_id', flat=True))
    my_requests = shop.plan_requests.select_related('plan').order_by('-created_at')[:5]

    return render(request, 'dashboard/billing.html', {
        'shop': shop,
        'subscription': sub,
        'plan': plan,
        'is_demo': is_demo,
        'is_valid': sub.is_valid(),
        'days_left': sub.days_left(),
        'campaign_count': campaign_count,
        'active_campaign_count': active_campaign_count,
        'spin_count': spin_count,
        'all_plans': all_plans,
        'pending_plan_ids': pending_plan_ids,
        'my_requests': my_requests,
    })


@shop_access_required
def account_settings_view(request):
    user = request.user
    shop = user.shop
    message = None
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)
            user.save()
            message = "Profile details updated successfully."

        elif action == 'change_password':
            old_pass = request.POST.get('old_password', '')
            new_pass1 = request.POST.get('new_password1', '')
            new_pass2 = request.POST.get('new_password2', '')

            if not user.check_password(old_pass):
                error = "Incorrect current password."
            elif new_pass1 != new_pass2:
                error = "New passwords do not match."
            elif len(new_pass1) < 6:
                error = "Password must be at least 6 characters long."
            else:
                user.set_password(new_pass1)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                message = "Password changed successfully."

    return render(request, 'dashboard/account_settings.html', {
        'shop': shop,
        'message': message,
        'error': error
    })


@shop_access_required
def notifications_view(request):
    shop = request.user.shop
    notifications_qs = Notification.objects.filter(shop=shop).order_by('-created_at') if shop else Notification.objects.none()
    paginator = Paginator(notifications_qs, 20)
    page_number = request.GET.get('page', 1)
    try:
        notifications_page = paginator.page(page_number)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/notifications.html', {
        'shop': shop,
        'notifications': notifications_page,
        'notifications_page': notifications_page,
        'paginator': paginator,
        'total_notifications_count': notifications_qs.count()
    })


@require_POST
@shop_access_required
def mark_notification_read_view(request, notification_id):
    shop = request.user.shop
    notif = get_object_or_404(Notification, id=notification_id, shop=shop)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return JsonResponse({'status': 'success'})


@shop_access_required
def preview_campaign_view(request, campaign_id):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        shop = Shop.objects.first()

    camp = get_object_or_404(Campaign, id=campaign_id, shop=shop)
    branding, _ = ShopBranding.objects.get_or_create(shop=shop)
    prizes = list(camp.prizes.filter(is_active=True))
    if not prizes:
        prizes = [{
            'id': 0, 'name': 'Sample Reward', 'display_color': '#6366f1', 'prize_type': 'percentage'
        }]

    prizes_json = json.dumps([{
        'id': p.id if hasattr(p, 'id') else p.get('id', 0),
        'name': p.name if hasattr(p, 'name') else p.get('name', 'Sample Reward'),
        'display_color': p.display_color if hasattr(p, 'display_color') else p.get('display_color', '#6366f1'),
        'prize_type': p.prize_type if hasattr(p, 'prize_type') else p.get('prize_type', 'percentage'),
        'design_config': (p.design_config if hasattr(p, 'design_config') else p.get('design_config', {})) or {}
    } for p in prizes])

    from core.services.theme_resolver import get_active_shop_theme, ThemeResolution
    theme_param = request.GET.get('theme')
    if theme_param:
        active_theme = theme_param
        theme_resolution = ThemeResolution(theme=active_theme, reason=f"Live Preview Query: {active_theme}", normal_theme=active_theme)
    else:
        theme_resolution = get_active_shop_theme(shop, camp)
        active_theme = theme_resolution.theme

    center_hub_config = camp.get_center_hub_config()
    return render(request, 'customer/spin_landing.html', {
        'shop': shop,
        'campaign': camp,
        'branding': branding,
        'font_family': getattr(branding, 'font_family', 'inter') if branding else 'inter',
        'active_theme': active_theme,
        'theme_resolution': theme_resolution,
        'theme_intensity': getattr(branding, 'intensity', 'balanced') or 'balanced',
        'prizes': prizes,
        'prizes_json': prizes_json,
        'center_hub_config': center_hub_config,
        'center_hub_config_json': json.dumps(center_hub_config),
        'is_preview': True,
        'is_public_page': True
    })


@require_POST
@shop_access_required
def preview_spin_api(request, campaign_id):
    shop = request.user.shop
    if request.user.is_superadmin() and not shop:
        camp = get_object_or_404(Campaign, id=campaign_id)
        shop = camp.shop
    else:
        camp = get_object_or_404(Campaign, id=campaign_id, shop=shop)

    prizes = list(camp.prizes.filter(is_active=True))
    if not prizes:
        return JsonResponse({'status': 'error', 'message': 'No active prizes configured.'}, status=400)

    weights = [max(0.0, float(p.probability)) for p in prizes]
    total_w = sum(weights)
    if total_w <= 0:
        winning_prize = random.choice(prizes)
    else:
        winning_prize = random.choices(prizes, weights=weights, k=1)[0]
    winning_index = prizes.index(winning_prize)

    # Decrement remaining quantity if positive
    if winning_prize.remaining_quantity > 0:
        winning_prize.remaining_quantity = max(0, winning_prize.remaining_quantity - 1)
        winning_prize.save(update_fields=['remaining_quantity'])

    # Record real SpinResult for preview test
    spin_res = SpinResult.objects.create(
        shop=shop,
        campaign=camp,
        prize=winning_prize,
        session_key=f"preview_{request.session.session_key or 'test'}",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    # Generate real, unique, redeemable Coupon for winning prizes
    coupon_data = None
    if winning_prize.prize_type != 'no_win':
        code = Coupon.generate_code(shop)
        expires = timezone.now() + timedelta(days=30)
        coupon = Coupon.objects.create(
            code=code,
            spin_result=spin_res,
            shop=shop,
            campaign=camp,
            prize=winning_prize,
            status='active',
            expires_at=expires
        )
        coupon_data = {
            'code': coupon.code,
            'verify_token': coupon.verify_token,
            'prize_name': winning_prize.name,
            'coupon_text': winning_prize.coupon_text,
            'expires_at': coupon.expires_at.strftime('%d %b %Y')
        }

    return JsonResponse({
        'status': 'success',
        'is_preview': True,
        'winning_segment_index': winning_index,
        'prize': {
            'id': winning_prize.id,
            'name': winning_prize.name,
            'prize_type': winning_prize.prize_type,
            'coupon_text': winning_prize.coupon_text
        },
        'coupon': coupon_data
    })


# ---------------------------------------------------------
# PHASE 7: HEALTH CHECK & PRODUCTION ERROR HANDLERS
# ---------------------------------------------------------

def health_check_view(request):
    from django.db import connection
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected',
        'service': 'Spin & Win SaaS Platform'
    }, status=status_code)


def custom_400_view(request, exception=None):
    ctx = get_error_context(request, 400, default_msg="Bad Request")
    if ctx.get('is_ajax'):
        return JsonResponse({'status': 'error', 'code': 400, 'message': 'Bad Request: The server could not understand your request.'}, status=400)
    return render(request, 'errors/400.html', ctx, status=400)


def custom_403_view(request, exception=None):
    ctx = get_error_context(request, 403, default_msg="Access Denied")
    if ctx.get('is_ajax'):
        return JsonResponse({'status': 'error', 'code': 403, 'message': 'Access Denied: You do not have permission to access this resource.'}, status=403)
    return render(request, 'errors/403.html', ctx, status=403)


def custom_404_view(request, exception=None):
    ctx = get_error_context(request, 404, default_msg="Resource Not Found")
    if ctx.get('is_ajax'):
        return JsonResponse({'status': 'error', 'code': 404, 'message': 'Not Found: The requested resource does not exist.'}, status=404)
    return render(request, 'errors/404.html', ctx, status=404)


def custom_500_view(request):
    ctx = get_error_context(request, 500, default_msg="Internal Server Error")
    if ctx.get('is_ajax'):
        return JsonResponse({'status': 'error', 'code': 500, 'message': 'Internal Server Error: A temporary server error occurred. Please try again later.'}, status=500)
    return render(request, 'errors/500.html', ctx, status=500)