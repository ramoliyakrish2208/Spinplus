import uuid
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('shop_owner', 'Shop Owner'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='shop_owner')
    shop = models.ForeignKey('Shop', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone = models.CharField(max_length=20, blank=True)

    def is_superadmin(self):
        return self.role == 'super_admin' or self.is_superuser

    def is_owner(self):
        return self.role == 'shop_owner'



class Shop(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    )
    name = models.CharField(max_length=150)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_shops')
    public_token = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    currency_symbol = models.CharField(max_length=10, default='₹')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='shop_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    auto_theme_enabled = models.BooleanField(default=True)
    normal_theme = models.CharField(max_length=50, default='royal')
    manual_theme_override = models.CharField(max_length=50, blank=True, null=True)
    override_until = models.DateTimeField(null=True, blank=True)
    auto_category_theme_adaptation = models.BooleanField(default=True)
    country = models.CharField(max_length=50, default='IN')
    region = models.CharField(max_length=100, default='Gujarat')
    pre_festival_days = models.IntegerField(default=3)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            token = secrets.token_hex(6)
            while Shop.objects.filter(public_token=token).exists():
                token = secrets.token_hex(6)
            self.public_token = token
        super().save(*args, **kwargs)

    def get_subscription(self):
        from django.utils import timezone as tz
        from datetime import timedelta
        sub, _ = Subscription.objects.get_or_create(shop=self)
        if not sub.plan:
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
            sub.plan = default_plan
            if not sub.expires_at:
                sub.expires_at = tz.now() + timedelta(days=30)
            sub.status = 'active'
            sub.save()
        return sub

    def has_active_subscription(self):
        sub = self.get_subscription()
        return sub.is_valid()

    def can_create_campaign(self):
        if not self.has_active_subscription():
            return False
        sub = self.get_subscription()
        return self.campaigns.count() < sub.plan.max_campaigns

    def can_add_prize(self, campaign):
        if not self.has_active_subscription():
            return False
        sub = self.get_subscription()
        return campaign.prizes.count() < sub.plan.max_prizes_per_campaign

    def can_spin(self):
        if not self.has_active_subscription():
            return False
        sub = self.get_subscription()
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spins = SpinResult.objects.filter(shop=self, created_at__gte=start_of_month).count()
        return monthly_spins < sub.plan.max_spins_per_month

    def get_active_campaign(self):
        now = timezone.now()
        active = self.campaigns.filter(
            status__in=['active', 'live'],
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()
        if not active:
            active = self.campaigns.filter(status__in=['active', 'live'], is_active=True).first()
        return active

    def get_branding(self):
        try:
            return getattr(self, 'branding', None)
        except Exception:
            return None

    def resolve_theme(self, campaign=None):
        """
        Theme Resolution Priority:
        1. Manual Override (if set & valid)
        2. Active Campaign Theme Override
        3. Automatic Calendar Festival Events (if auto_theme_enabled is True)
        4. Normal Shop Theme / Branding Theme ('royal' default)
        """
        try:
            from core.services.theme_resolver import get_active_shop_theme
            res = get_active_shop_theme(self, campaign=campaign)
            return res.theme
        except Exception:
            if campaign and getattr(campaign, 'theme', None) and campaign.theme.strip() and campaign.theme.strip() not in ['', 'default', 'none']:
                return campaign.theme.strip()
            branding = self.get_branding()
            if branding and getattr(branding, 'theme', None):
                return branding.theme
            return self.normal_theme or 'royal'

    def __str__(self):
        return self.name


class ShopBranding(models.Model):
    THEME_CHOICES = (
        ('royal', 'Royal Gold'),
        ('royal_jewellery', 'Royal Jewellery (Gold & Ruby)'),
        ('luxury_black', 'Luxury Black'),
        ('minimal_luxury', 'Minimal Luxury'),
        ('pearl', 'Pearl Luxury (Beauty & Salon)'),
        ('aurora', 'Aurora Luminous'),
        ('glass', 'Glassmorphism Frosted'),
        ('neon', 'Cyber Neon (Gaming)'),
        ('emerald', 'Emerald Green'),
        ('burgundy', 'Burgundy Fashion'),
        ('fashion', 'Haute Couture Fashion'),
        ('modern_blue', 'Modern Blue Tech'),
        ('festival', 'Festival Celebration'),
        ('diwali', 'Diwali Lights & Dhanteras'),
        ('navratri', 'Navratri Garba'),
        ('holi', 'Holi Color Splash'),
        ('christmas', 'Christmas Holiday'),
        ('new_year', 'New Year Sparkle'),
        ('eid', 'Eid Celebration'),
        ('valentines', 'Valentine Romance'),
        ('halloween', 'Spooky Halloween'),
        ('uttarayan', 'Uttarayan Kite Festival'),
        ('summer_sale', 'Summer Tropical Sale'),
        ('winter_sale', 'Winter Frost Sale'),
        ('monsoon_sale', 'Monsoon Splash Sale'),
        ('flash_sale', 'Flash Sale Lightning'),
        ('clearance', 'Clearance Sale'),
        ('restaurant', 'Restaurant & Gourmet Dining'),
        ('coffee', 'Coffee Café & Bakery'),
        ('beauty', 'Cosmetics & Beauty Glow'),
        ('sports', 'Sports & Gym Energy'),
        ('automotive', 'Automotive Speed & Carbon'),
        ('playful', 'Playful Kids'),
        ('kids', 'Kids & Toys Playful'),
        ('candy', 'Candy Sweet'),
        ('minimal', 'Minimal Clean'),
        ('sunset', 'Sunset Warmth'),
        ('ocean', 'Ocean Wave'),
        ('floral', 'Floral Blossom'),
        ('premium_white', 'Premium White'),
        ('janmashtami', 'Krishna Janmashtami'),
        ('janmashtami_jewellery', 'Janmashtami Royal Jewellery'),
        ('janmashtami_sweets', 'Janmashtami Sweets & Butter Pot'),
        ('janmashtami_clothing', 'Janmashtami Festive Apparel'),
        ('janmashtami_kids', 'Janmashtami Bal Gopal Kids'),
        ('custom', 'Custom Theme'),
    )
    FONT_CHOICES = (
        ('inter', 'Inter (Modern)'),
        ('poppins', 'Poppins (Friendly)'),
        ('outfit', 'Outfit (Tech)'),
        ('playfair', 'Playfair Display (Luxury)'),
        ('space_grotesk', 'Space Grotesk (Futuristic)'),
        ('cinzel', 'Cinzel (Elegant)'),
    )
    INTENSITY_CHOICES = (
        ('subtle', 'Subtle (Low Animation)'),
        ('balanced', 'Balanced (Standard Premium Effects)'),
        ('dynamic', 'Dynamic (Maximum Promotional Effects)'),
    )
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='branding')
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='royal')
    font_family = models.CharField(max_length=30, choices=FONT_CHOICES, default='inter')
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='balanced', null=True, blank=True)
    primary_color = models.CharField(max_length=20, default='#6366f1')
    secondary_color = models.CharField(max_length=20, default='#4f46e5')
    accent_color = models.CharField(max_length=20, default='#f59e0b')
    background_color = models.CharField(max_length=20, default='#0f172a')
    text_color = models.CharField(max_length=20, default='#f8fafc')
    button_color = models.CharField(max_length=20, default='#6366f1')
    header_color = models.CharField(max_length=20, default='#1e293b')
    wheel_center_logo = models.ImageField(upload_to='wheel_logos/', blank=True, null=True)
    pointer_style = models.CharField(max_length=20, default='classic')
    spin_button_text = models.CharField(max_length=50, default='SPIN NOW')
    spin_button_color = models.CharField(max_length=20, default='#ec4899')
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_theme_defaults(cls, theme_code):
        defaults = {
            'royal': {
                'primary_color': '#d4af37',
                'secondary_color': '#4a152d',
                'accent_color': '#ffd700',
                'background_color': '#0a060d',
                'text_color': '#fdfbf7',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN & WIN GOLD'
            },
            'luxury_black': {
                'primary_color': '#f3e5ab',
                'secondary_color': '#272730',
                'accent_color': '#d4af37',
                'background_color': '#050507',
                'text_color': '#f4f4f6',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN FOR LUXURY'
            },
            'pearl': {
                'primary_color': '#0f172a',
                'secondary_color': '#e2e8f0',
                'accent_color': '#d4af37',
                'background_color': '#f8fafc',
                'text_color': '#0f172a',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN FOR PEARLS'
            },
            'aurora': {
                'primary_color': '#a855f7',
                'secondary_color': '#3b82f6',
                'accent_color': '#06b6d4',
                'background_color': '#0b0f19',
                'text_color': '#f0f9ff',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN THE AURORA'
            },
            'glass': {
                'primary_color': '#6366f1',
                'secondary_color': '#8b5cf6',
                'accent_color': '#38bdf8',
                'background_color': '#0f172a',
                'text_color': '#ffffff',
                'font_family': 'inter',
                'spin_button_text': 'SPIN GLASS WHEEL'
            },
            'neon': {
                'primary_color': '#06b6d4',
                'secondary_color': '#a855f7',
                'accent_color': '#f43f5e',
                'background_color': '#09090b',
                'text_color': '#fafafa',
                'font_family': 'space_grotesk',
                'spin_button_text': 'SPIN CYBER NEON'
            },
            'diwali': {
                'primary_color': '#d4af37',
                'secondary_color': '#6d28d9',
                'accent_color': '#f59e0b',
                'background_color': '#0d0614',
                'text_color': '#fef08a',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN DIWALI DHAMAKA'
            },
            'navratri': {
                'primary_color': '#ec4899',
                'secondary_color': '#8b5cf6',
                'accent_color': '#f59e0b',
                'background_color': '#180828',
                'text_color': '#fff1f2',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN GARBA WHEEL'
            },
            'holi': {
                'primary_color': '#f43f5e',
                'secondary_color': '#06b6d4',
                'accent_color': '#eab308',
                'background_color': '#111827',
                'text_color': '#ffffff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN HOLI COLORS'
            },
            'christmas': {
                'primary_color': '#dc2626',
                'secondary_color': '#16a34a',
                'accent_color': '#fef08a',
                'background_color': '#051b11',
                'text_color': '#ffffff',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN XMAS REWARD'
            },
            'new_year': {
                'primary_color': '#d4af37',
                'secondary_color': '#3b82f6',
                'accent_color': '#ffffff',
                'background_color': '#030712',
                'text_color': '#f8fafc',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN NEW YEAR LUCK'
            },
            'eid': {
                'primary_color': '#10b981',
                'secondary_color': '#065f46',
                'accent_color': '#d4af37',
                'background_color': '#022c22',
                'text_color': '#ecfdf5',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN EID BLESSINGS'
            },
            'valentines': {
                'primary_color': '#f43f5e',
                'secondary_color': '#831843',
                'accent_color': '#fda4af',
                'background_color': '#1a050f',
                'text_color': '#fff1f2',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN LOVE REWARD'
            },
            'summer_sale': {
                'primary_color': '#f59e0b',
                'secondary_color': '#0284c7',
                'accent_color': '#10b981',
                'background_color': '#0c4a6e',
                'text_color': '#f0f9ff',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN SUMMER SALE'
            },
            'winter_sale': {
                'primary_color': '#38bdf8',
                'secondary_color': '#1e3a8a',
                'accent_color': '#ffffff',
                'background_color': '#030712',
                'text_color': '#f0f9ff',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN WINTER FROST'
            },
            'monsoon_sale': {
                'primary_color': '#0ea5e9',
                'secondary_color': '#0369a1',
                'accent_color': '#38bdf8',
                'background_color': '#082f49',
                'text_color': '#e0f2fe',
                'font_family': 'inter',
                'spin_button_text': 'SPIN MONSOON REWARD'
            },
            'flash_sale': {
                'primary_color': '#ef4444',
                'secondary_color': '#f59e0b',
                'accent_color': '#fbbf24',
                'background_color': '#18181b',
                'text_color': '#ffffff',
                'font_family': 'space_grotesk',
                'spin_button_text': 'SPIN FLASH SALE'
            },
            'clearance': {
                'primary_color': '#dc2626',
                'secondary_color': '#991b1b',
                'accent_color': '#facc15',
                'background_color': '#111827',
                'text_color': '#ffffff',
                'font_family': 'space_grotesk',
                'spin_button_text': 'SPIN CLEARANCE SALE'
            },
            'restaurant': {
                'primary_color': '#d97706',
                'secondary_color': '#451a03',
                'accent_color': '#f59e0b',
                'background_color': '#1c1917',
                'text_color': '#fef3c7',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN GOURMET REWARDS'
            },
            'coffee': {
                'primary_color': '#b45309',
                'secondary_color': '#78350f',
                'accent_color': '#fcd34d',
                'background_color': '#1a0e05',
                'text_color': '#fffbeb',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN COFFEE WHEEL'
            },
            'fashion': {
                'primary_color': '#e4e4e7',
                'secondary_color': '#27272a',
                'accent_color': '#d4af37',
                'background_color': '#09090b',
                'text_color': '#fafafa',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN HAUTE COUTURE'
            },
            'electronics': {
                'primary_color': '#06b6d4',
                'secondary_color': '#1e3a8a',
                'accent_color': '#38bdf8',
                'background_color': '#030712',
                'text_color': '#f0f9ff',
                'font_family': 'space_grotesk',
                'spin_button_text': 'SPIN TECH REWARDS'
            },
            'janmashtami': {
                'primary_color': '#00e5ff',
                'secondary_color': '#3b185f',
                'accent_color': '#ffd700',
                'background_color': '#060b1e',
                'text_color': '#f0f9ff',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN KRISHNA\'S WHEEL'
            },
            'janmashtami_jewellery': {
                'primary_color': '#d4af37',
                'secondary_color': '#1e1b4b',
                'accent_color': '#ffd700',
                'background_color': '#040714',
                'text_color': '#fef08a',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN ROYAL JEWELS'
            },
            'janmashtami_sweets': {
                'primary_color': '#f59e0b',
                'secondary_color': '#4c1d95',
                'accent_color': '#fef08a',
                'background_color': '#0a0d24',
                'text_color': '#fffbeb',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN MAKHAN HANDI'
            },
            'janmashtami_clothing': {
                'primary_color': '#00c49f',
                'secondary_color': '#581c87',
                'accent_color': '#ffd700',
                'background_color': '#070c20',
                'text_color': '#fdf2f8',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN FESTIVE ATTIRE'
            },
            'janmashtami_kids': {
                'primary_color': '#00f2fe',
                'secondary_color': '#8b5cf6',
                'accent_color': '#fbbf24',
                'background_color': '#080e28',
                'text_color': '#ffffff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN BAL GOPAL'
            },
            'royal_jewellery': {
                'primary_color': '#ffd700',
                'secondary_color': '#4a152d',
                'accent_color': '#ffd700',
                'background_color': '#0a060d',
                'text_color': '#fdfbf7',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN ROYAL JEWELS'
            },
            'minimal_luxury': {
                'primary_color': '#f3e5ab',
                'secondary_color': '#272730',
                'accent_color': '#d4af37',
                'background_color': '#050507',
                'text_color': '#f4f4f6',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN FOR LUXURY'
            },
            'halloween': {
                'primary_color': '#ff6b00',
                'secondary_color': '#4a0e4e',
                'accent_color': '#a855f7',
                'background_color': '#0d0214',
                'text_color': '#ffebd9',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN OR TRICK'
            },
            'sports': {
                'primary_color': '#ef4444',
                'secondary_color': '#1e293b',
                'accent_color': '#f59e0b',
                'background_color': '#0b0f19',
                'text_color': '#f8fafc',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN FOR ENERGY'
            },
            'automotive': {
                'primary_color': '#f59e0b',
                'secondary_color': '#18181b',
                'accent_color': '#ef4444',
                'background_color': '#09090b',
                'text_color': '#f4f4f5',
                'font_family': 'space_grotesk',
                'spin_button_text': 'SPIN & ACCELERATE'
            },
            'beauty': {
                'primary_color': '#ec4899',
                'secondary_color': '#831843',
                'accent_color': '#fbcfe8',
                'background_color': '#180814',
                'text_color': '#fdf2f8',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN FOR GLOW'
            },
            'playful': {
                'primary_color': '#06b6d4',
                'secondary_color': '#8b5cf6',
                'accent_color': '#fbbf24',
                'background_color': '#0a0e27',
                'text_color': '#ffffff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN PLAYFUL TOYS'
            },
            'kids': {
                'primary_color': '#06b6d4',
                'secondary_color': '#8b5cf6',
                'accent_color': '#fbbf24',
                'background_color': '#0a0e27',
                'text_color': '#ffffff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN KIDS TOYS'
            },
            'candy': {
                'primary_color': '#f472b6',
                'secondary_color': '#8b5cf6',
                'accent_color': '#fde047',
                'background_color': '#1a0a20',
                'text_color': '#fdf4ff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN SWEET CANDY'
            },
            'uttarayan': {
                'primary_color': '#f59e0b',
                'secondary_color': '#0284c7',
                'accent_color': '#10b981',
                'background_color': '#082032',
                'text_color': '#f0f9ff',
                'font_family': 'poppins',
                'spin_button_text': 'SPIN KAI PO CHE'
            },
            'festival': {
                'primary_color': '#d4af37',
                'secondary_color': '#8b5cf6',
                'accent_color': '#ec4899',
                'background_color': '#14061a',
                'text_color': '#fef08a',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN FESTIVAL WHEEL'
            },
            'emerald': {
                'primary_color': '#10b981',
                'secondary_color': '#065f46',
                'accent_color': '#fef08a',
                'background_color': '#022c22',
                'text_color': '#ecfdf5',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN EMERALD WHEEL'
            },
            'burgundy': {
                'primary_color': '#f472b6',
                'secondary_color': '#831843',
                'accent_color': '#fbbf24',
                'background_color': '#1c0a14',
                'text_color': '#fdf2f8',
                'font_family': 'cinzel',
                'spin_button_text': 'SPIN BURGUNDY'
            },
            'minimal': {
                'primary_color': '#6366f1',
                'secondary_color': '#1e293b',
                'accent_color': '#f59e0b',
                'background_color': '#0f172a',
                'text_color': '#f8fafc',
                'font_family': 'inter',
                'spin_button_text': 'SPIN MINIMAL'
            },
            'sunset': {
                'primary_color': '#f97316',
                'secondary_color': '#db2777',
                'accent_color': '#fbbf24',
                'background_color': '#180b1e',
                'text_color': '#fff7ed',
                'font_family': 'outfit',
                'spin_button_text': 'SPIN SUNSET GOLD'
            },
            'ocean': {
                'primary_color': '#06b6d4',
                'secondary_color': '#0284c7',
                'accent_color': '#38bdf8',
                'background_color': '#021b2b',
                'text_color': '#f0f9ff',
                'font_family': 'inter',
                'spin_button_text': 'SPIN OCEAN WAVE'
            },
            'floral': {
                'primary_color': '#a855f7',
                'secondary_color': '#ec4899',
                'accent_color': '#fbcfe8',
                'background_color': '#130820',
                'text_color': '#faf5ff',
                'font_family': 'playfair',
                'spin_button_text': 'SPIN BLOSSOM'
            },
            'modern_blue': {
                'primary_color': '#3b82f6',
                'secondary_color': '#1d4ed8',
                'accent_color': '#60a5fa',
                'background_color': '#0f172a',
                'text_color': '#f8fafc',
                'font_family': 'inter',
                'spin_button_text': 'SPIN MODERN BLUE'
            },
            'premium_white': {
                'primary_color': '#0f172a',
                'secondary_color': '#f1f5f9',
                'accent_color': '#6366f1',
                'background_color': '#ffffff',
                'text_color': '#0f172a',
                'font_family': 'inter',
                'spin_button_text': 'SPIN REWARDS'
            },
        }
        return defaults.get(theme_code, {
            'primary_color': '#6366f1',
            'secondary_color': '#4f46e5',
            'accent_color': '#f59e0b',
            'background_color': '#0f172a',
            'text_color': '#f8fafc',
            'font_family': 'inter',
            'spin_button_text': 'SPIN NOW'
        })

    def __str__(self):
        return f"Branding for {self.shop.name}"


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('live', 'Live / Active'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('disabled', 'Disabled'),
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    welcome_title = models.CharField(max_length=200, blank=True)
    welcome_subtitle = models.CharField(max_length=255, blank=True)
    spin_button_text = models.CharField(max_length=50, default='SPIN NOW')
    winning_title = models.CharField(max_length=150, default='CONGRATULATIONS!')
    winning_message = models.CharField(max_length=255, blank=True)
    losing_message = models.CharField(max_length=255, default='Better luck next time!')
    terms_conditions = models.TextField(blank=True, default='Valid for single spin per visit. Show coupon code to staff at checkout.')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='live')
    max_spins_per_user = models.IntegerField(default=1)
    spin_cooldown_hours = models.IntegerField(default=24)
    hero_image = models.ImageField(upload_to='campaign_heroes/', blank=True, null=True)
    template_type = models.CharField(max_length=50, blank=True)
    theme = models.CharField(max_length=50, default='', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_welcome_title(self):
        return self.welcome_title if self.welcome_title else f"Welcome to {self.shop.name}"

    def get_welcome_subtitle(self):
        return self.welcome_subtitle if self.welcome_subtitle else self.description

    def __str__(self):
        return f"{self.name} ({self.shop.name})"


class Prize(models.Model):
    TYPE_CHOICES = (
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Discount'),
        ('freebie', 'Free Item'),
        ('no_win', 'Try Again / Better Luck'),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='prizes')
    name = models.CharField(max_length=100)
    prize_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='percentage')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    fixed_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    coupon_text = models.CharField(max_length=255, blank=True)
    probability = models.FloatField(default=15.0, help_text='Weight percentage (e.g. 25.0)')
    display_color = models.CharField(max_length=20, default='#6366f1')
    is_active = models.BooleanField(default=True)
    max_wins = models.IntegerField(default=500)
    remaining_quantity = models.IntegerField(default=500)

    def __str__(self):
        return f"{self.name} - {self.campaign.name}"


class QRCode(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='qr_code')
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    target_url = models.URLField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QR for {self.shop.name}"


class SpinResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='spin_results')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='spin_results')
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, related_name='spin_results')
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'created_at']),
            models.Index(fields=['shop', 'campaign', 'created_at']),
            models.Index(fields=['session_key', 'created_at']),
        ]

    def __str__(self):
        return f"Spin {self.id} - {self.prize.name}"


class Coupon(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    code = models.CharField(max_length=30, unique=True, db_index=True)
    verify_token = models.CharField(max_length=64, unique=True, db_index=True, blank=True, null=True)
    spin_result = models.OneToOneField(SpinResult, on_delete=models.CASCADE, related_name='coupon')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='coupons')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='coupons')
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, related_name='coupons')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'status']),
            models.Index(fields=['shop', 'created_at']),
            models.Index(fields=['campaign', 'status']),
        ]

    @classmethod
    def generate_code(cls, shop=None):
        if shop:
            shop_prefix = f"S{shop.id:03d}"
            prefix = f"{shop_prefix}-SW"
        else:
            prefix = "SW"
        part1 = secrets.token_hex(2).upper()
        part2 = secrets.token_hex(2).upper()
        code = f"{prefix}-{part1}-{part2}"
        while cls.objects.filter(code=code).exists():
            part1 = secrets.token_hex(2).upper()
            part2 = secrets.token_hex(2).upper()
            code = f"{prefix}-{part1}-{part2}"
        return code

    def save(self, *args, **kwargs):
        if not self.verify_token:
            token = f"v_{secrets.token_urlsafe(16)}"
            while Coupon.objects.filter(verify_token=token).exists():
                token = f"v_{secrets.token_urlsafe(16)}"
            self.verify_token = token
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({self.prize.name})"


class CouponRedemption(models.Model):
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name='redemption')
    redeemed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-redeemed_at']
        indexes = [
            models.Index(fields=['redeemed_at']),
        ]

    def __str__(self):
        return f"Redeemed {self.coupon.code} at {self.redeemed_at}"


class ActivityLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['shop', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"


class QRScanLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='qr_scans')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['shop', 'scanned_at']),
        ]

    def __str__(self):
        return f"Scan for {self.shop.name} at {self.scanned_at}"


class Plan(models.Model):
    CYCLE_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom Days'),
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, default='starter')
    price_rupees = models.DecimalField(max_digits=10, decimal_places=2, default=499.00)
    price_display = models.CharField(max_length=50, default='₹499 / month')
    billing_cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES, default='monthly')
    billing_period_days = models.IntegerField(default=30)
    trial_days = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    max_campaigns = models.IntegerField(default=5)
    max_active_campaigns = models.IntegerField(default=1)
    max_prizes_per_campaign = models.IntegerField(default=8)
    max_spins_per_month = models.IntegerField(default=1000)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def formatted_price(self):
        val_str = f"₹{int(self.price_rupees):,}" if self.price_rupees % 1 == 0 else f"₹{self.price_rupees:,.2f}"
        if self.billing_cycle == 'yearly' or self.billing_period_days == 365:
            return f"{val_str} / yr"
        elif self.billing_cycle == 'monthly' or self.billing_period_days == 30:
            return f"{val_str} / mo"
        return f"{val_str} / {self.billing_period_days}d"

    def __str__(self):
        return f"{self.name} ({self.formatted_price()})"


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
    )
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        if self.status not in ['active', 'trial']:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def days_left(self):
        if not self.expires_at:
            return None
        now = timezone.now()
        if self.expires_at <= now:
            return 0
        diff = self.expires_at - now
        return diff.days + (1 if diff.seconds > 0 else 0)

    def renew(self, plan=None, duration_days=None):
        if plan:
            self.plan = plan
        days = duration_days or (self.plan.billing_period_days if self.plan else 30)
        now = timezone.now()
        base_date = self.expires_at if (self.expires_at and self.expires_at > now) else now
        self.expires_at = base_date + timezone.timedelta(days=days)
        self.status = 'active'
        self.is_active = True
        self.save()
        return self

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"{self.shop.name} — {plan_name} ({self.status})"


class Notification(models.Model):
    LEVEL_CHOICES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.level.upper()}] {self.title}"


class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ('festival', 'Festival'),
        ('special_day', 'Special Occasion / Day'),
        ('seasonal', 'Seasonal Event'),
        ('weekday', 'Weekday Theme'),
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, default='festival')
    country = models.CharField(max_length=50, blank=True, default='IN')
    region = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    theme = models.CharField(max_length=50, choices=ShopBranding.THEME_CHOICES, default='festival')
    priority = models.IntegerField(default=10)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🎉')
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=50, default='system')
    source_event_id = models.CharField(max_length=100, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', 'start_date']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name} ({self.start_date} to {self.end_date})"


class ThemeAuditLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='theme_audit_logs')
    previous_theme = models.CharField(max_length=50)
    new_theme = models.CharField(max_length=50)
    reason = models.CharField(max_length=200)
    event = models.ForeignKey(CalendarEvent, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Shop #{self.shop_id}: {self.previous_theme} -> {self.new_theme} ({self.reason})"


class PlanRequest(models.Model):
    """Tenant shop owners submit plan upgrade requests for admin approval."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='plan_requests')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_plan_requests')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.shop.name} → {self.plan.name} ({self.status})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Shop)
def auto_create_shop_subscription(sender, instance, created, **kwargs):
    if created:
        default_plan = Plan.objects.filter(is_default=True, is_active=True).first()
        if not default_plan:
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
        Subscription.objects.get_or_create(
            shop=instance,
            defaults={
                'plan': default_plan,
                'status': 'active',
                'starts_at': timezone.now(),
                'expires_at': timezone.now() + timezone.timedelta(days=default_plan.billing_period_days),
                'is_active': True
            }
        )



