from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import User, Shop, ShopBranding, Campaign, Prize

class Command(BaseCommand):
    help = 'Seeds initial multi-tenant demo data for Spin & Win platform'

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # 1. Super Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@spinwin.local',
                'role': 'super_admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS("Super Admin 'admin' created (password: admin123)"))

        # 2. Shop 1: ABC Cafe
        cafe_owner, created = User.objects.get_or_create(
            username='cafe_owner',
            defaults={'email': 'owner@abccafe.com', 'role': 'shop_owner'}
        )
        if created:
            cafe_owner.set_password('owner123')
            cafe_owner.save()

        shop1, created = Shop.objects.get_or_create(
            public_token='abc-cafe-8XK29',
            defaults={
                'name': 'ABC Café',
                'owner': cafe_owner,
                'category': 'Café & Bakery',
                'phone': '+1 555-0192',
                'email': 'contact@abccafe.com',
                'address': '123 Gourmet Street, Foodville',
                'description': 'Artisanal coffee, fresh pastries, and daily delightful surprises.',
                'status': 'active'
            }
        )
        cafe_owner.shop = shop1
        cafe_owner.save()

        ShopBranding.objects.get_or_create(
            shop=shop1,
            defaults={
                'theme': 'modern',
                'primary_color': '#6366f1',
                'secondary_color': '#4f46e5',
                'accent_color': '#f59e0b',
                'background_color': '#0f172a',
                'text_color': '#f8fafc',
                'button_color': '#6366f1',
                'header_color': '#1e293b',
                'spin_button_text': 'SPIN TO WIN',
                'spin_button_color': '#ec4899'
            }
        )

        now = timezone.now()
        camp1, created = Campaign.objects.get_or_create(
            shop=shop1,
            name='Summer Spin & Win',
            defaults={
                'description': 'Spin the wheel on every visit and unlock instant discounts!',
                'start_date': now - timedelta(days=1),
                'end_date': now + timedelta(days=60),
                'status': 'active',
                'is_active': True,
                'max_spins_per_user': 1,
                'spin_cooldown_hours': 24
            }
        )

        prizes1 = [
            ('5% OFF Coffee', 'percentage', 5.0, 0, '5% OFF your next coffee', 30.0, '#3b82f6'),
            ('10% OFF Total Bill', 'percentage', 10.0, 0, '10% OFF total bill', 25.0, '#10b981'),
            ('15% OFF Pastries', 'percentage', 15.0, 0, '15% OFF fresh pastries', 20.0, '#8b5cf6'),
            ('20% OFF Special', 'percentage', 20.0, 0, '20% OFF any order', 10.0, '#f59e0b'),
            ('$5 OFF Coupon', 'fixed', 0, 5.0, '$5 OFF purchase over $15', 5.0, '#ec4899'),
            ('Free Cookie', 'freebie', 0, 0, 'Free Freshly Baked Cookie', 5.0, '#06b6d4'),
            ('Better Luck Next Time', 'no_win', 0, 0, 'Thank you for playing!', 5.0, '#64748b'),
        ]

        for p_name, p_type, disc_pct, fixed_amt, text, prob, color in prizes1:
            Prize.objects.get_or_create(
                campaign=camp1,
                name=p_name,
                defaults={
                    'prize_type': p_type,
                    'discount_percentage': disc_pct,
                    'fixed_discount_amount': fixed_amt,
                    'coupon_text': text,
                    'probability': prob,
                    'display_color': color,
                    'max_wins': 500,
                    'remaining_quantity': 500,
                    'is_active': True
                }
            )

        # 3. Shop 2: Velvet Luxury
        luxury_owner, created = User.objects.get_or_create(
            username='luxury_owner',
            defaults={'email': 'owner@velvetluxury.com', 'role': 'shop_owner'}
        )
        if created:
            luxury_owner.set_password('owner123')
            luxury_owner.save()

        shop2, created = Shop.objects.get_or_create(
            public_token='velvet-luxury-99X',
            defaults={
                'name': 'Velvet & Co. Luxury',
                'owner': luxury_owner,
                'category': 'High-End Fashion',
                'phone': '+1 555-8821',
                'email': 'vip@velvetluxury.com',
                'address': '742 Fifth Avenue, Luxury District',
                'description': 'Exclusive haute couture and premium jewelry.',
                'status': 'active'
            }
        )
        luxury_owner.shop = shop2
        luxury_owner.save()

        ShopBranding.objects.get_or_create(
            shop=shop2,
            defaults={
                'theme': 'luxury',
                'primary_color': '#d97706',
                'secondary_color': '#b45309',
                'accent_color': '#fef3c7',
                'background_color': '#09090b',
                'text_color': '#fef3c7',
                'button_color': '#d97706',
                'header_color': '#18181b',
                'spin_button_text': 'SPIN THE LUXURY WHEEL',
                'spin_button_color': '#d97706'
            }
        )

        camp2, created = Campaign.objects.get_or_create(
            shop=shop2,
            name='Exclusive VIP Rewards',
            defaults={
                'description': 'Unlock privileged luxury vouchers.',
                'start_date': now - timedelta(days=1),
                'end_date': now + timedelta(days=90),
                'status': 'active',
                'is_active': True
            }
        )

        prizes2 = [
            ('10% VIP Pass', 'percentage', 10.0, 0, '10% OFF luxury apparel', 40.0, '#d97706'),
            ('15% VIP Pass', 'percentage', 15.0, 0, '15% OFF luxury apparel', 30.0, '#b45309'),
            ('$50 Boutique Gift', 'fixed', 0, 50.0, '$50 OFF purchase', 20.0, '#f59e0b'),
            ('Better Luck Next Time', 'no_win', 0, 0, 'Thank you for visiting Velvet & Co.', 10.0, '#3f3f46'),
        ]

        for p_name, p_type, disc_pct, fixed_amt, text, prob, color in prizes2:
            Prize.objects.get_or_create(
                campaign=camp2,
                name=p_name,
                defaults={
                    'prize_type': p_type,
                    'discount_percentage': disc_pct,
                    'fixed_discount_amount': fixed_amt,
                    'coupon_text': text,
                    'probability': prob,
                    'display_color': color,
                    'max_wins': 200,
                    'remaining_quantity': 200,
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded!"))
