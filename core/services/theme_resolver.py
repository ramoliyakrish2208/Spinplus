import zoneinfo
import datetime
from django.utils import timezone
from core.models import CalendarEvent, ThemeAuditLog, ShopBranding

class ThemeResolution:
    def __init__(self, theme, reason, event=None, is_override=False, is_auto=False, expires_at=None, normal_theme='royal', is_pre_festival=False, pre_festival_days_left=0):
        self.theme = theme
        self.reason = reason
        self.event = event
        self.is_override = is_override
        self.is_auto = is_auto
        self.expires_at = expires_at
        self.normal_theme = normal_theme
        self.is_pre_festival = is_pre_festival
        self.pre_festival_days_left = pre_festival_days_left

    def to_dict(self):
        return {
            'theme': self.theme,
            'reason': self.reason,
            'event_name': self.event.name if self.event else None,
            'event_icon': self.event.icon if self.event else '🎨',
            'is_override': self.is_override,
            'is_auto': self.is_auto,
            'is_pre_festival': self.is_pre_festival,
            'pre_festival_days_left': self.pre_festival_days_left,
            'expires_at': self.expires_at.strftime('%d %b %Y, %I:%M %p') if (self.expires_at and hasattr(self.expires_at, 'strftime')) else str(self.expires_at or ''),
            'normal_theme': self.normal_theme
        }

def get_shop_local_datetime(shop, target_datetime=None):
    """
    Converts a UTC or naive datetime to the Shop's configured timezone.
    Default timezone is 'Asia/Kolkata'.
    """
    dt = target_datetime or timezone.now()
    tz_str = getattr(shop, 'timezone', 'Asia/Kolkata') or 'Asia/Kolkata'
    try:
        tz = zoneinfo.ZoneInfo(tz_str)
    except Exception:
        tz = zoneinfo.ZoneInfo('Asia/Kolkata')

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, datetime.timezone.utc)
    return dt.astimezone(tz)

def adapt_theme_to_category(base_theme: str, category: str) -> str:
    """
    Adapts festival or default themes to specific business categories if enabled.
    For example:
    - Janmashtami + Sweets -> janmashtami_sweets
    - Janmashtami + Jewellery -> janmashtami_jewellery
    - Janmashtami + Clothing -> janmashtami_clothing
    - Janmashtami + Kids -> janmashtami_kids
    - Royal/Generic + Coffee -> coffee
    - Royal/Generic + Food -> restaurant
    """
    if not category:
        return base_theme

    cat = category.lower()

    # Janmashtami category adaptations
    if base_theme.startswith('janmashtami'):
        if any(w in cat for w in ['jewel', 'gold', 'diamond']):
            return 'janmashtami_jewellery'
        elif any(w in cat for w in ['sweet', 'bakery', 'mithai', 'dairy', 'milk', 'dahi']):
            return 'janmashtami_sweets'
        elif any(w in cat for w in ['cloth', 'fashion', 'apparel', 'saree', 'textile', 'garment', 'wear']):
            return 'janmashtami_clothing'
        elif any(w in cat for w in ['kid', 'toy', 'baby', 'child', 'play']):
            return 'janmashtami_kids'
        return 'janmashtami'

    # Generic theme category adaptations
    if base_theme in ['royal', 'default', 'minimal', 'modern', 'festival']:
        if 'jewel' in cat:
            return 'royal_jewellery'
        elif 'coffee' in cat or 'cafe' in cat:
            return 'coffee'
        elif any(w in cat for w in ['rest', 'dine', 'food', 'bakery', 'sweet']):
            return 'restaurant'
        elif any(w in cat for w in ['gym', 'fitness', 'sport']):
            return 'sports'
        elif any(w in cat for w in ['salon', 'beauty']):
            return 'beauty'
        elif any(w in cat for w in ['tech', 'elec', 'mobile']):
            return 'electronics'

    return base_theme

def get_active_shop_theme(shop, campaign=None, target_datetime=None):
    """
    Strict Priority Resolution:
    1. Manual Override (if set & valid for current local time)
    2. Active Campaign Theme Override (if set in campaign)
    3. Automatic Calendar Festival Events (if auto_theme_enabled is True)
    4. Pre-Festival Mode (if within pre_festival_days before an upcoming festival)
    5. Normal Shop Theme / Branding Theme ('royal' default)
    """
    if not shop:
        return ThemeResolution(theme='royal', reason='Default System Theme', normal_theme='royal')

    local_dt = get_shop_local_datetime(shop, target_datetime)
    local_date = local_dt.date()
    normal_theme = getattr(shop, 'normal_theme', 'royal') or 'royal'

    # Check ShopBranding fallback if normal_theme not explicit
    branding = shop.get_branding()
    if branding and getattr(branding, 'theme', None):
        normal_theme = branding.theme

    # 1. Manual Override
    if shop.manual_theme_override:
        if shop.override_until:
            override_dt = shop.override_until
            if timezone.is_naive(override_dt):
                override_dt = timezone.make_aware(override_dt, datetime.timezone.utc)
            if local_dt <= override_dt:
                return ThemeResolution(
                    theme=shop.manual_theme_override,
                    reason='Manual Override Active',
                    is_override=True,
                    is_auto=False,
                    expires_at=override_dt,
                    normal_theme=normal_theme
                )
            else:
                # Expired -> Revert
                prev_override = shop.manual_theme_override
                shop.manual_theme_override = None
                shop.override_until = None
                shop.save(update_fields=['manual_theme_override', 'override_until'])
                ThemeAuditLog.objects.create(
                    shop=shop,
                    previous_theme=prev_override,
                    new_theme=normal_theme,
                    reason='Manual Override Expired — Auto Reverted'
                )
        else:
            # Permanent manual override
            return ThemeResolution(
                theme=shop.manual_theme_override,
                reason='Manual Override Active',
                is_override=True,
                is_auto=False,
                expires_at=None,
                normal_theme=normal_theme
            )

    # 2. Active Campaign Override
    active_camp = campaign or shop.get_active_campaign()
    if active_camp and getattr(active_camp, 'theme', None):
        camp_theme = active_camp.theme.strip()
        if camp_theme and camp_theme.lower() not in ['', 'default', 'none']:
            return ThemeResolution(
                theme=camp_theme,
                reason=f"Promotional Campaign: {active_camp.name}",
                is_override=False,
                is_auto=False,
                normal_theme=normal_theme
            )

    # 3. Automatic Calendar Events
    if getattr(shop, 'auto_theme_enabled', True):
        # Query active events for date & region
        events = CalendarEvent.objects.filter(
            is_active=True,
            start_date__lte=local_date,
            end_date__gte=local_date
        ).order_by('-priority', 'start_date')

        # Filter by region if specified
        shop_country = getattr(shop, 'country', 'IN') or 'IN'
        shop_region = getattr(shop, 'region', '') or ''

        matching_event = None
        for evt in events:
            if evt.country and evt.country.upper() != shop_country.upper():
                continue
            if evt.region and shop_region and evt.region.lower() not in shop_region.lower():
                continue
            matching_event = evt
            break

        if not matching_event and events.exists():
            matching_event = events.first()

        if matching_event:
            theme_to_use = matching_event.theme

            # Category adaptation if enabled
            if getattr(shop, 'auto_category_theme_adaptation', True) and getattr(shop, 'category', None):
                theme_to_use = adapt_theme_to_category(theme_to_use, shop.category)

            return ThemeResolution(
                theme=theme_to_use,
                reason=f"Calendar Event: {matching_event.name}",
                event=matching_event,
                is_override=False,
                is_auto=True,
                expires_at=matching_event.end_date,
                normal_theme=normal_theme
            )

        # 4. Pre-Festival Mode (e.g. 1-7 days before event)
        pre_days = getattr(shop, 'pre_festival_days', 3) or 3
        if pre_days > 0:
            window_end = local_date + datetime.timedelta(days=pre_days)
            upcoming_events = CalendarEvent.objects.filter(
                is_active=True,
                start_date__gt=local_date,
                start_date__lte=window_end
            ).order_by('-priority', 'start_date')

            for u_evt in upcoming_events:
                if u_evt.country and u_evt.country.upper() != shop_country.upper():
                    continue
                if u_evt.region and shop_region and u_evt.region.lower() not in shop_region.lower():
                    continue
                
                days_until = (u_evt.start_date - local_date).days
                theme_to_use = u_evt.theme
                if getattr(shop, 'auto_category_theme_adaptation', True) and getattr(shop, 'category', None):
                    theme_to_use = adapt_theme_to_category(theme_to_use, shop.category)

                return ThemeResolution(
                    theme=theme_to_use,
                    reason=f"Pre-Festival Mode: {u_evt.name} Coming Soon ({days_until}d)",
                    event=u_evt,
                    is_override=False,
                    is_auto=True,
                    is_pre_festival=True,
                    pre_festival_days_left=days_until,
                    expires_at=u_evt.end_date,
                    normal_theme=normal_theme
                )

    # 5. Fallback to Normal Theme
    theme_to_use = normal_theme
    if getattr(shop, 'auto_category_theme_adaptation', True) and getattr(shop, 'category', None):
        theme_to_use = adapt_theme_to_category(normal_theme, shop.category)

    return ThemeResolution(
        theme=theme_to_use,
        reason='Normal Shop Theme',
        is_override=False,
        is_auto=False,
        normal_theme=normal_theme
    )

