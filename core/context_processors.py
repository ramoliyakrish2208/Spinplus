from core.models import Shop, ShopBranding, PlanRequest
from core.services.theme_resolver import get_active_shop_theme

def shop_theme_processor(request):
    """
    Global Shop Theme context processor for Spin & Win SaaS Platform.
    Dynamically calculates active theme via Smart Theme Engine across all pages (Dashboard, Studio, Staff, CRM, Analytics, Errors, etc.).
    """
    res = {
        'active_theme': 'royal',
        'font_family': 'inter',
        'theme_intensity': 'balanced',
        'current_shop': None,
        'branding': None,
        'theme_resolution': None,
        'theme_defaults': ShopBranding.get_theme_defaults('royal')
    }

    shop = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        if getattr(request.user, 'shop', None):
            shop = request.user.shop
        elif request.user.is_superadmin():
            shop_id = request.GET.get('shop_id')
            if shop_id:
                shop = Shop.objects.filter(id=shop_id).first()
            if not shop:
                shop = Shop.objects.first()
    elif hasattr(request, 'shop') and request.shop:
        shop = request.shop

    if shop:
        res['current_shop'] = shop
        branding = shop.get_branding()
        if branding:
            res['branding'] = branding
            res['font_family'] = branding.font_family or 'inter'
            res['theme_intensity'] = getattr(branding, 'intensity', 'balanced') or 'balanced'

        active_camp = shop.get_active_campaign()
        resolution = get_active_shop_theme(shop, campaign=active_camp)

        res['active_theme'] = resolution.theme
        res['theme_resolution'] = resolution.to_dict()
        res['theme_defaults'] = ShopBranding.get_theme_defaults(resolution.theme)

    # Provide pending plan requests count for superadmin notification badge
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superadmin():
        res['pending_plan_requests_count'] = PlanRequest.objects.filter(status='pending').count()

    return res
