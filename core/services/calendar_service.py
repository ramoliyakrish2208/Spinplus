import datetime
from django.utils import timezone
from core.models import CalendarEvent

DEFAULT_CALENDAR_EVENTS = [
    # ── 2026 REAL CALENDAR FESTIVALS & SPECIAL EVENTS ──
    {
        'name': 'Uttarayan / Makar Sankranti',
        'slug': 'uttarayan-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 1, 14),
        'end_date': datetime.date(2026, 1, 15),
        'theme': 'uttarayan',
        'priority': 50,
        'icon': '🪁',
        'description': 'Makar Sankranti Kite Flying Festival.'
    },
    {
        'name': 'Valentine\'s Day',
        'slug': 'valentines-day-2026',
        'event_type': 'special_day',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 2, 14),
        'end_date': datetime.date(2026, 2, 14),
        'theme': 'valentines',
        'priority': 40,
        'icon': '💖',
        'description': 'Valentine\'s Day Romance & Gifting Season.'
    },
    {
        'name': 'Holi Festival of Colors',
        'slug': 'holi-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 3, 3),
        'end_date': datetime.date(2026, 3, 4),
        'theme': 'holi',
        'priority': 50,
        'icon': '🎨',
        'description': 'Festival of Colors Holi.'
    },
    {
        'name': 'International Women\'s Day',
        'slug': 'womens-day-2026',
        'event_type': 'special_day',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 3, 8),
        'end_date': datetime.date(2026, 3, 8),
        'theme': 'beauty',
        'priority': 30,
        'icon': '💐',
        'description': 'International Women\'s Day Special Offers.'
    },
    {
        'name': 'Eid al-Fitr',
        'slug': 'eid-al-fitr-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 3, 20),
        'end_date': datetime.date(2026, 3, 21),
        'theme': 'eid',
        'priority': 50,
        'icon': '🌙',
        'description': 'Eid al-Fitr Moonlit Celebrations.'
    },
    {
        'name': 'Summer Grand Sale',
        'slug': 'summer-sale-2026',
        'event_type': 'seasonal',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 5, 1),
        'end_date': datetime.date(2026, 5, 10),
        'theme': 'summer_sale',
        'priority': 20,
        'icon': '☀️',
        'description': 'Tropical Summer Shopping Season.'
    },
    {
        'name': 'Monsoon Splash Festival',
        'slug': 'monsoon-sale-2026',
        'event_type': 'seasonal',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 7, 15),
        'end_date': datetime.date(2026, 7, 20),
        'theme': 'monsoon_sale',
        'priority': 20,
        'icon': '🌧️',
        'description': 'Rainy Season Offers & Monsoon Deals.'
    },
    {
        'name': 'Raksha Bandhan',
        'slug': 'raksha-bandhan-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 8, 28),
        'end_date': datetime.date(2026, 8, 28),
        'theme': 'royal',
        'priority': 45,
        'icon': '🎁',
        'description': 'Raksha Bandhan Sibling Love & Gifting Festival.'
    },
    {
        'name': 'Krishna Janmashtami',
        'slug': 'janmashtami-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 9, 4),
        'end_date': datetime.date(2026, 9, 5),
        'theme': 'janmashtami',
        'priority': 65,
        'icon': '🦚',
        'description': 'Magical Krishna Janmashtami Midnight Celebration.'
    },
    {
        'name': 'Ganesh Chaturthi',
        'slug': 'ganesh-chaturthi-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 9, 14),
        'end_date': datetime.date(2026, 9, 24),
        'theme': 'festival',
        'priority': 55,
        'icon': '🐘',
        'description': '10 Days Ganesh Mahotsav Celebration.'
    },
    {
        'name': 'Navratri Garba Celebration',
        'slug': 'navratri-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 10, 10),
        'end_date': datetime.date(2026, 10, 18),
        'theme': 'navratri',
        'priority': 60,
        'icon': '💃',
        'description': '9 Divine Nights of Navratri Garba & Dandiya.'
    },
    {
        'name': 'Dussehra / Vijayadashami',
        'slug': 'dussehra-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 10, 20),
        'end_date': datetime.date(2026, 10, 20),
        'theme': 'royal',
        'priority': 50,
        'icon': '🏹',
        'description': 'Victory of Good over Evil Dussehra Festival.'
    },
    {
        'name': 'Halloween Spooky Festival',
        'slug': 'halloween-2026',
        'event_type': 'special_day',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 10, 31),
        'end_date': datetime.date(2026, 10, 31),
        'theme': 'halloween',
        'priority': 40,
        'icon': '🎃',
        'description': 'Spooky Halloween Trick or Treat Discounts.'
    },
    {
        'name': 'Dhanteras & Diwali Lights',
        'slug': 'diwali-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 11, 6),
        'end_date': datetime.date(2026, 11, 10),
        'theme': 'diwali',
        'priority': 70,
        'icon': '🪔',
        'description': 'Grand Festival of Lights Diwali & Dhanteras.'
    },
    {
        'name': 'Black Friday & Cyber Sale',
        'slug': 'black-friday-2026',
        'event_type': 'seasonal',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 11, 27),
        'end_date': datetime.date(2026, 11, 30),
        'theme': 'flash_sale',
        'priority': 45,
        'icon': '⚡',
        'description': 'Mega Black Friday Flash Sale Lightning Deals.'
    },
    {
        'name': 'Christmas Holiday Magic',
        'slug': 'christmas-2026',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 12, 24),
        'end_date': datetime.date(2026, 12, 26),
        'theme': 'christmas',
        'priority': 55,
        'icon': '🎄',
        'description': 'Winter Christmas Village & Festive Joy.'
    },
    {
        'name': 'New Year Midnight Celebration',
        'slug': 'new-year-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2026, 12, 31),
        'end_date': datetime.date(2027, 1, 1),
        'theme': 'new_year',
        'priority': 60,
        'icon': '🎆',
        'description': 'Midnight New Year Golden Countdown.'
    },

    # ── 2027 REAL CALENDAR FESTIVALS ──
    {
        'name': 'Uttarayan / Makar Sankranti 2027',
        'slug': 'uttarayan-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 1, 14),
        'end_date': datetime.date(2027, 1, 15),
        'theme': 'uttarayan',
        'priority': 50,
        'icon': '🪁',
        'description': 'Makar Sankranti Kite Festival 2027.'
    },
    {
        'name': 'Valentine\'s Day 2027',
        'slug': 'valentines-2027',
        'event_type': 'special_day',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 2, 14),
        'end_date': datetime.date(2027, 2, 14),
        'theme': 'valentines',
        'priority': 40,
        'icon': '💖',
        'description': 'Valentine\'s Day Romance 2027.'
    },
    {
        'name': 'Maha Shivratri 2027',
        'slug': 'maha-shivratri-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 3, 6),
        'end_date': datetime.date(2027, 3, 6),
        'theme': 'royal',
        'priority': 50,
        'icon': '🔱',
        'description': 'Maha Shivratri Auspicious Night.'
    },
    {
        'name': 'Eid al-Fitr 2027',
        'slug': 'eid-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 3, 10),
        'end_date': datetime.date(2027, 3, 11),
        'theme': 'eid',
        'priority': 50,
        'icon': '🌙',
        'description': 'Eid al-Fitr Celebrations 2027.'
    },
    {
        'name': 'Holi Festival of Colors 2027',
        'slug': 'holi-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 3, 22),
        'end_date': datetime.date(2027, 3, 23),
        'theme': 'holi',
        'priority': 50,
        'icon': '🎨',
        'description': 'Holi Festival of Colors 2027.'
    },
    {
        'name': 'Krishna Janmashtami 2027',
        'slug': 'janmashtami-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 8, 25),
        'end_date': datetime.date(2027, 8, 26),
        'theme': 'janmashtami',
        'priority': 65,
        'icon': '🦚',
        'description': 'Krishna Janmashtami Celebration 2027.'
    },
    {
        'name': 'Navratri Garba Celebration 2027',
        'slug': 'navratri-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 9, 30),
        'end_date': datetime.date(2027, 10, 8),
        'theme': 'navratri',
        'priority': 60,
        'icon': '💃',
        'description': 'Navratri Garba Festival 2027.'
    },
    {
        'name': 'Dhanteras & Diwali Lights 2027',
        'slug': 'diwali-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 10, 27),
        'end_date': datetime.date(2027, 10, 31),
        'theme': 'diwali',
        'priority': 70,
        'icon': '🪔',
        'description': 'Diwali Lights Festival 2027.'
    },
    {
        'name': 'Christmas Festival 2027',
        'slug': 'christmas-2027',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 12, 24),
        'end_date': datetime.date(2027, 12, 26),
        'theme': 'christmas',
        'priority': 55,
        'icon': '🎄',
        'description': 'Christmas Holiday Magic 2027.'
    },
    {
        'name': 'New Year Midnight Party 2028',
        'slug': 'new-year-2028',
        'event_type': 'festival',
        'country': 'IN',
        'region': '',
        'start_date': datetime.date(2027, 12, 31),
        'end_date': datetime.date(2028, 1, 1),
        'theme': 'new_year',
        'priority': 60,
        'icon': '🎆',
        'description': 'New Year Celebration 2028.'
    }
]


def sync_calendar_events():
    """
    Populates and synchronizes system default calendar events in the database.
    """
    count = 0
    now = timezone.now()
    for item in DEFAULT_CALENDAR_EVENTS:
        evt, created = CalendarEvent.objects.update_or_create(
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'event_type': item['event_type'],
                'country': item.get('country', 'IN'),
                'region': item.get('region', ''),
                'start_date': item['start_date'],
                'end_date': item['end_date'],
                'theme': item['theme'],
                'priority': item['priority'],
                'icon': item['icon'],
                'description': item['description'],
                'is_active': True,
                'source': 'system',
                'last_synced': now
            }
        )
        if created:
            count += 1
    return len(DEFAULT_CALENDAR_EVENTS), count


def get_next_upcoming_festivals(shop=None, limit=5, target_date=None):
    """
    Automatically detects and returns the next N upcoming festivals from the real calendar.
    Orders chronologically from today forward.
    Attaches computed fields: days_until, is_active_now, is_today, formatted_range.
    """
    if shop:
        from core.services.theme_resolver import get_shop_local_datetime
        local_dt = get_shop_local_datetime(shop) if not target_date else target_date
        current_date = local_dt.date() if hasattr(local_dt, 'date') else local_dt
        shop_country = getattr(shop, 'country', 'IN') or 'IN'
        shop_region = getattr(shop, 'region', '') or ''
    else:
        current_date = target_date or timezone.now().date()
        shop_country = 'IN'
        shop_region = ''

    # Ensure DB is populated
    sync_calendar_events()

    events = CalendarEvent.objects.filter(
        is_active=True,
        end_date__gte=current_date
    ).order_by('start_date', '-priority')

    matched_events = []
    for evt in events:
        if evt.country and evt.country.upper() != shop_country.upper():
            continue
        if evt.region and shop_region and evt.region.lower() not in shop_region.lower():
            continue

        days_until = max(0, (evt.start_date - current_date).days)
        is_active_now = evt.start_date <= current_date <= evt.end_date
        is_today = evt.start_date == current_date

        evt.days_until = days_until
        evt.is_active_now = is_active_now
        evt.is_today = is_today
        if evt.start_date == evt.end_date:
            evt.formatted_range = evt.start_date.strftime('%d %b %Y')
        else:
            evt.formatted_range = f"{evt.start_date.strftime('%d %b')} – {evt.end_date.strftime('%d %b %Y')}"

        matched_events.append(evt)
        if len(matched_events) >= limit:
            break

    # If region filter yielded fewer than limit, top up with general events
    if len(matched_events) < limit:
        for evt in events:
            if evt in matched_events:
                continue
            days_until = max(0, (evt.start_date - current_date).days)
            is_active_now = evt.start_date <= current_date <= evt.end_date
            is_today = evt.start_date == current_date

            evt.days_until = days_until
            evt.is_active_now = is_active_now
            evt.is_today = is_today
            if evt.start_date == evt.end_date:
                evt.formatted_range = evt.start_date.strftime('%d %b %Y')
            else:
                evt.formatted_range = f"{evt.start_date.strftime('%d %b')} – {evt.end_date.strftime('%d %b %Y')}"

            matched_events.append(evt)
            if len(matched_events) >= limit:
                break

    return matched_events[:limit]


# Astronomical / Hindu Lunar Calendar Ephemeris for Janmashtami
# (Ashtami Tithi of Krishna Paksha in the month of Bhadrapada)
JANMASHTAMI_EPHEMERIS = {
    2024: (datetime.date(2024, 8, 26), datetime.date(2024, 8, 27)),
    2025: (datetime.date(2025, 8, 16), datetime.date(2025, 8, 17)),
    2026: (datetime.date(2026, 9, 4), datetime.date(2026, 9, 5)),
    2027: (datetime.date(2027, 8, 25), datetime.date(2027, 8, 26)),
    2028: (datetime.date(2028, 8, 13), datetime.date(2028, 8, 14)),
    2029: (datetime.date(2029, 9, 1), datetime.date(2029, 9, 2)),
    2030: (datetime.date(2030, 8, 21), datetime.date(2030, 8, 22)),
}


def get_janmashtami_dates_for_year(year: int):
    """
    Returns (start_date, end_date) for Krishna Janmashtami for any given year.
    Uses accurate panchang ephemeris table with dynamic fallback.
    """
    if year in JANMASHTAMI_EPHEMERIS:
        return JANMASHTAMI_EPHEMERIS[year]
    # General approximation for future unlisted years: late August
    approx_start = datetime.date(year, 8, 20)
    return approx_start, approx_start + datetime.timedelta(days=1)
