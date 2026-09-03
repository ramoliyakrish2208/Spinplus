"""
SpinPlus Demo Shop & Subscription Plans Seeder
==============================================
Creates or updates:
  1. Standard SaaS subscription plans in Indian Rupees (₹):
     - Free Demo Plan (₹0 / 14 days)
     - Starter Monthly (₹499 / 30 days)
     - Growth Monthly (₹999 / 30 days — more benefits)
     - Quarterly Pro (₹2,499 / 90 days — 3 months)
     - Semi-Annual Elite (₹4,499 / 180 days — 6 months)
     - Annual Business (₹7,999 / 365 days — 1 year)
     - Enterprise VIP (₹14,999 / 365 days — maximum benefits)
  2. Demo merchant user:
     - Username: demoshop
     - Password: Demo@12345
     - Shop: SpinPlus Demo Lounge & Cafe
     - Active subscription, branding, live campaign, prizes & QR code
"""
import os
import sys
from decimal import Decimal
from datetime import timedelta

import django

# Ensure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Setup Django environment if run as standalone script
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spinplus.settings')
django.setup()

from django.utils import timezone
from core.models import User, Shop, Plan, Subscription, ShopBranding, Campaign, Prize, QRCode
from core.qr import generate_shop_qr


def seed_plans():
    print("\n[1/3] Seeding / updating SaaS subscription plans in ₹...")

    plans_data = [
        {
            'code': 'free_demo',
            'name': 'Free Demo Plan',
            'price_rupees': Decimal('0.00'),
            'price_display': '₹0 / 14 Days',
            'billing_cycle': 'custom',
            'billing_period_days': 14,
            'trial_days': 14,
            'description': 'Full feature demo access for evaluation. Test wheel spinning, QR scanning, and coupon validation.',
            'max_campaigns': 1,
            'max_active_campaigns': 1,
            'max_prizes_per_campaign': 4,
            'max_spins_per_month': 100,
            'is_default': False,
            'is_active': True,
        },
        {
            'code': 'starter_monthly',
            'name': 'Starter Monthly',
            'price_rupees': Decimal('499.00'),
            'price_display': '₹499 / month',
            'billing_cycle': 'monthly',
            'billing_period_days': 30,
            'trial_days': 0,
            'description': 'Essential toolkit for local retail stores, bakeries, and boutiques starting customer engagement.',
            'max_campaigns': 3,
            'max_active_campaigns': 1,
            'max_prizes_per_campaign': 6,
            'max_spins_per_month': 1000,
            'is_default': True,
            'is_active': True,
        },
        {
            'code': 'growth_monthly',
            'name': 'Growth Monthly (More Benefits)',
            'price_rupees': Decimal('999.00'),
            'price_display': '₹999 / month',
            'billing_cycle': 'monthly',
            'billing_period_days': 30,
            'trial_days': 0,
            'description': 'Advanced promotional features with multiple simultaneous campaigns and higher monthly spin quotas.',
            'max_campaigns': 8,
            'max_active_campaigns': 2,
            'max_prizes_per_campaign': 10,
            'max_spins_per_month': 3500,
            'is_default': False,
            'is_active': True,
        },
        {
            'code': 'quarterly_pro',
            'name': 'Quarterly Pro (3 Months)',
            'price_rupees': Decimal('2499.00'),
            'price_display': '₹2,499 / 3 months',
            'billing_cycle': 'custom',
            'billing_period_days': 90,
            'trial_days': 0,
            'description': 'Save ~17% with a 3-month seasonal pass. Perfect for festival campaigns and quarterly footfall surges.',
            'max_campaigns': 15,
            'max_active_campaigns': 3,
            'max_prizes_per_campaign': 12,
            'max_spins_per_month': 5000,
            'is_default': False,
            'is_active': True,
        },
        {
            'code': 'semiannual_elite',
            'name': 'Semi-Annual Elite (6 Months)',
            'price_rupees': Decimal('4499.00'),
            'price_display': '₹4,499 / 6 months',
            'billing_cycle': 'custom',
            'billing_period_days': 180,
            'trial_days': 0,
            'description': 'Save ~25% with 6-month continuous coverage. High spin volume for busy restaurants and salons.',
            'max_campaigns': 25,
            'max_active_campaigns': 5,
            'max_prizes_per_campaign': 16,
            'max_spins_per_month': 10000,
            'is_default': False,
            'is_active': True,
        },
        {
            'code': 'annual_business',
            'name': 'Annual Business (1 Year)',
            'price_rupees': Decimal('7999.00'),
            'price_display': '₹7,999 / year',
            'billing_cycle': 'yearly',
            'billing_period_days': 365,
            'trial_days': 0,
            'description': 'Save ~33% with full year access. 10 simultaneous live campaigns and 25,000 spins/month capacity.',
            'max_campaigns': 50,
            'max_active_campaigns': 10,
            'max_prizes_per_campaign': 20,
            'max_spins_per_month': 25000,
            'is_default': False,
            'is_active': True,
        },
        {
            'code': 'enterprise_annual',
            'name': 'Enterprise VIP (Maximum Benefits)',
            'price_rupees': Decimal('14999.00'),
            'price_display': '₹14,999 / year',
            'billing_cycle': 'yearly',
            'billing_period_days': 365,
            'trial_days': 0,
            'description': 'Unlimited enterprise tier for supermarket chains, multi-counter stores, and mega events.',
            'max_campaigns': 100,
            'max_active_campaigns': 20,
            'max_prizes_per_campaign': 24,
            'max_spins_per_month': 100000,
            'is_default': False,
            'is_active': True,
        },
    ]

    seeded_plans = []
    for data in plans_data:
        code = data.pop('code')
        plan, created = Plan.objects.update_or_create(code=code, defaults=data)
        action = "Created" if created else "Updated"
        print(f"      ✅ {action} Plan: {plan.name} — {plan.price_display}")
        seeded_plans.append(plan)

    return seeded_plans


def seed_demo_shop():
    print("\n[2/3] Seeding demo merchant account...")

    # 1. Create or update user: demoshop / Demo@12345
    user, user_created = User.objects.get_or_create(
        username='demoshop',
        defaults={
            'email': 'demoshop@spinplus.in',
            'role': 'shop_owner',
            'first_name': 'Demo',
            'last_name': 'Merchant',
        }
    )
    user.role = 'shop_owner'
    user.set_password('Demo@12345')
    user.save()
    user_action = "Created" if user_created else "Updated password/role for"
    print(f"      ✅ {user_action} user: demoshop / Demo@12345")

    # 2. Create or update demo shop
    shop, shop_created = Shop.objects.get_or_create(
        owner=user,
        defaults={
            'name': 'SpinPlus Demo Cafe & Lounge',
            'category': 'Cafe & Gourmet Dining',
            'currency_symbol': '₹',
            'phone': '+91 98765 43210',
            'email': 'demoshop@spinplus.in',
            'address': 'Ground Floor, Galleria Boulevard, Ahmedabad, Gujarat 380015',
            'description': 'Experience the interactive Spin & Win promotional wheel at our artisan cafe.',
            'status': 'active',
            'timezone': 'Asia/Kolkata',
            'country': 'IN',
            'region': 'Gujarat',
            'normal_theme': 'royal',
            'onboarding_completed': True,
        }
    )
    # Link user.shop if not already set
    if user.shop != shop:
        user.shop = shop
        user.save(update_fields=['shop'])

    shop_action = "Created" if shop_created else "Found existing"
    print(f"      ✅ {shop_action} shop: {shop.name} (Token: {shop.public_token})")

    # 3. Assign active Subscription (Free Demo Plan, 30 days)
    free_demo_plan = Plan.objects.filter(code='free_demo').first() or Plan.objects.first()
    sub, sub_created = Subscription.objects.update_or_create(
        shop=shop,
        defaults={
            'plan': free_demo_plan,
            'status': 'active',
            'is_active': True,
            'starts_at': timezone.now(),
            'expires_at': timezone.now() + timedelta(days=30),
            'notes': 'Official SpinPlus Demo Account with Free Trial Plan',
        }
    )
    print(f"      ✅ Assigned Subscription: {sub.plan.name} (Expires: {sub.expires_at.strftime('%Y-%m-%d')})")

    # 4. Branding
    branding, _ = ShopBranding.objects.update_or_create(
        shop=shop,
        defaults={
            'theme': 'royal',
            'font_family': 'outfit',
            'primary_color': '#6366f1',
            'secondary_color': '#8b5cf6',
            'accent_color': '#f59e0b',
            'background_color': '#0f172a',
            'text_color': '#ffffff',
            'spin_button_text': 'SPIN & WIN DEALS',
            'intensity': 'balanced',
        }
    )
    print("      ✅ Configured custom branding (Royal theme, Outfit typography)")

    # 5. Live Promotional Campaign
    campaign, camp_created = Campaign.objects.update_or_create(
        shop=shop,
        name='Welcome Mega Spin & Win',
        defaults={
            'description': 'Spin our celebratory wheel to unlock instant discounts, vouchers, and free artisan items!',
            'welcome_title': 'Welcome to SpinPlus Demo Cafe!',
            'welcome_subtitle': 'Scan our table QR, spin the wheel, and show your lucky coupon to your server!',
            'spin_button_text': 'SPIN FOR LUCK',
            'winning_title': 'CONGRATULATIONS, YOU WON!',
            'winning_message': 'Your exclusive voucher is ready. Present the coupon code to our staff at billing.',
            'losing_message': 'Thanks for visiting! Spin again tomorrow for more deals.',
            'terms_conditions': 'Valid on minimum bill of ₹200. One coupon per table. Not combinable with other offers.',
            'start_date': timezone.now() - timedelta(days=1),
            'end_date': timezone.now() + timedelta(days=90),
            'status': 'live',
            'is_active': True,
            'max_spins_per_user': 3,
            'spin_cooldown_hours': 12,
        }
    )
    print(f"      ✅ {'Created' if camp_created else 'Updated'} active campaign: {campaign.name}")

    # 6. Configure realistic balanced prizes
    prizes_data = [
        {
            'name': '15% Off Total Bill',
            'prize_type': 'percentage',
            'discount_percentage': Decimal('15.00'),
            'fixed_discount_amount': Decimal('0.00'),
            'coupon_text': 'Save 15% on your food & beverage bill',
            'probability': 25.0,
            'display_color': '#6366f1',
            'remaining_quantity': 500,
            'max_wins': 500,
            'is_active': True,
        },
        {
            'name': 'Free Cold Brew Coffee',
            'prize_type': 'freebie',
            'discount_percentage': Decimal('0.00'),
            'fixed_discount_amount': Decimal('0.00'),
            'coupon_text': 'Complimentary Cold Brew on order above ₹250',
            'probability': 15.0,
            'display_color': '#10b981',
            'remaining_quantity': 250,
            'max_wins': 250,
            'is_active': True,
        },
        {
            'name': '₹50 Flat Instant Discount',
            'prize_type': 'fixed',
            'discount_percentage': Decimal('0.00'),
            'fixed_discount_amount': Decimal('50.00'),
            'coupon_text': '₹50 flat discount on billing',
            'probability': 20.0,
            'display_color': '#f59e0b',
            'remaining_quantity': 400,
            'max_wins': 400,
            'is_active': True,
        },
        {
            'name': 'Free Artisan Dessert',
            'prize_type': 'freebie',
            'discount_percentage': Decimal('0.00'),
            'fixed_discount_amount': Decimal('0.00'),
            'coupon_text': 'Complimentary Chef choice dessert',
            'probability': 15.0,
            'display_color': '#ec4899',
            'remaining_quantity': 200,
            'max_wins': 200,
            'is_active': True,
        },
        {
            'name': '25% Mega VIP Discount',
            'prize_type': 'percentage',
            'discount_percentage': Decimal('25.00'),
            'fixed_discount_amount': Decimal('0.00'),
            'coupon_text': 'Save a huge 25% on your bill',
            'probability': 10.0,
            'display_color': '#8b5cf6',
            'remaining_quantity': 100,
            'max_wins': 100,
            'is_active': True,
        },
        {
            'name': 'Try Again Tomorrow',
            'prize_type': 'no_win',
            'discount_percentage': Decimal('0.00'),
            'fixed_discount_amount': Decimal('0.00'),
            'coupon_text': 'Better luck next time!',
            'probability': 15.0,
            'display_color': '#64748b',
            'remaining_quantity': 9999,
            'max_wins': 9999,
            'is_active': True,
        },
    ]

    for pdata in prizes_data:
        pname = pdata.pop('name')
        prize, _ = Prize.objects.update_or_create(
            campaign=campaign,
            name=pname,
            defaults=pdata
        )
        print(f"         • Prize: {prize.name} ({prize.probability}% weight)")

    # 7. QR Code
    site_base = "https://spinplus.pythonanywhere.com"
    qr_code, _ = QRCode.objects.get_or_create(
        shop=shop,
        defaults={'target_url': f"{site_base}/s/{shop.public_token}/"}
    )
    if not qr_code.qr_image:
        generate_shop_qr(shop, site_base)
    print(f"      ✅ QR Code ready: {site_base}/s/{shop.public_token}/")

    return shop


def main():
    print("=" * 60)
    print("  SpinPlus — Demo Shop & Multi-Tier Subscription Plans Seeder")
    print("=" * 60)
    seed_plans()
    shop = seed_demo_shop()
    print("\n[3/3] Seeding Summary:")
    print(f"      • Demo Username: demoshop")
    print(f"      • Demo Password: Demo@12345")
    print(f"      • Merchant Panel: /dashboard/shop/")
    print(f"      • Customer Wheel: /s/{shop.public_token}/")
    print("=" * 60)
    print("  ✅ All plans and demo shop seeded successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
