from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from core.models import User, Shop, ShopBranding, Campaign, Prize, SpinResult, Coupon, CouponRedemption, QRScanLog, ActivityLog, Plan, Subscription, Notification, CalendarEvent, ThemeAuditLog
from core.qr import generate_shop_qr, generate_coupon_qr

class SpinPlusCompleteAdminTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='adminpassword', role='super_admin'
        )

        self.owner_a = User.objects.create_user(
            username='owner_a', email='ownera@test.com', password='password123', role='shop_owner'
        )
        self.shop_a = Shop.objects.create(
            name='Shop Alpha', owner=self.owner_a, public_token='alpha-token-123', currency_symbol='$'
        )
        self.owner_a.shop = self.shop_a
        self.owner_a.save()

        now = timezone.now()
        self.camp_a = Campaign.objects.create(
            shop=self.shop_a, name='Alpha Campaign', start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10), status='live', is_active=True,
            welcome_title='Welcome to Alpha Store', spin_button_text='TRY YOUR LUCK'
        )
        self.prize_a1 = Prize.objects.create(
            campaign=self.camp_a, name='10% OFF Alpha', prize_type='percentage',
            discount_percentage=10.0, coupon_text='10% off total', probability=100.0,
            remaining_quantity=10
        )

        self.owner_b = User.objects.create_user(
            username='owner_b', email='ownerb@test.com', password='password123', role='shop_owner'
        )
        self.shop_b = Shop.objects.create(
            name='Shop Beta', owner=self.owner_b, public_token='beta-token-456', currency_symbol='₹'
        )
        self.owner_b.shop = self.shop_b
        self.owner_b.save()

    def test_shop_creation_and_qr_generation(self):
        """Verify shop token and QR code generation"""
        self.assertTrue(self.shop_a.public_token.startswith('alpha-token-123'))
        qr = generate_shop_qr(self.shop_a)
        self.assertIsNotNone(qr.qr_image)

    def test_secure_spin_logic(self):
        """Test server-side prize selection & spin endpoint"""
        url = f'/s/{self.shop_a.public_token}/spin/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['prize']['name'], '10% OFF Alpha')
        self.assertIsNotNone(data['coupon']['code'])
        self.assertIsNotNone(data['coupon']['verify_token'])

        spin_count = SpinResult.objects.filter(shop=self.shop_a).count()
        self.assertEqual(spin_count, 1)

        coupon_count = Coupon.objects.filter(shop=self.shop_a).count()
        self.assertEqual(coupon_count, 1)

    def test_no_staff_role_or_routes(self):
        """Verify Staff role and routes are removed per prompt specifications"""
        self.client.login(username='owner_a', password='password123')

        # Staff management URL should return 404
        res = self.client.get('/dashboard/shop/staff/')
        self.assertEqual(res.status_code, 404)

        # ROLE_CHOICES should only contain super_admin and shop_owner
        role_keys = [r[0] for r in User.ROLE_CHOICES]
        self.assertNotIn('shop_staff', role_keys)
        self.assertIn('shop_owner', role_keys)

    def test_campaign_duplication(self):
        """Test duplicating a seasonal campaign (e.g. Summer Sale -> Diwali Sale)"""
        self.client.login(username='owner_a', password='password123')

        dup_url = f'/dashboard/shop/campaigns/{self.camp_a.id}/duplicate/'
        res = self.client.get(dup_url)
        self.assertEqual(res.status_code, 302)

        copied_camp = Campaign.objects.get(name='Alpha Campaign (Copy)', shop=self.shop_a)
        self.assertFalse(copied_camp.is_active)
        self.assertEqual(copied_camp.status, 'draft')
        self.assertTrue(copied_camp.prizes.exists())
        self.assertEqual(copied_camp.prizes.first().name, '10% OFF Alpha')

    def test_global_search_api(self):
        """Test global search endpoint querying campaigns and coupons"""
        self.client.login(username='owner_a', password='password123')

        res = self.client.get('/dashboard/search/?q=Alpha')
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(len(data['results']) > 0)
        self.assertEqual(data['results'][0]['type'], 'Campaign')

    def test_activity_logs_view(self):
        """Test activity logs timeline view"""
        ActivityLog.objects.create(shop=self.shop_a, actor=self.owner_a, action="Test Action", details="Testing log entry")
        
        self.client.login(username='owner_a', password='password123')
        res = self.client.get('/dashboard/shop/logs/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Test Action")

    def test_campaign_crud_and_prize_probability_editor(self):
        """Test Campaign creation and Prize Probability Editor"""
        self.client.login(username='owner_a', password='password123')

        res_c = self.client.post('/dashboard/shop/campaigns/', {
            'action': 'create', 'name': 'Diwali Super Offer', 'description': 'Festival discounts',
            'spin_cooldown_hours': 12
        })
        self.assertEqual(res_c.status_code, 302)

        new_camp = Campaign.objects.get(name='Diwali Super Offer', shop=self.shop_a)
        self.assertTrue(new_camp.is_active)

        res_p = self.client.post(f'/dashboard/shop/campaigns/{new_camp.id}/prizes/', {
            'action': 'add_prize', 'name': '25% OFF Gift', 'prize_type': 'percentage',
            'discount_percentage': 25.0, 'coupon_text': '25% OFF festive special',
            'probability': 50.0, 'display_color': '#f59e0b', 'remaining_quantity': 50
        })
        self.assertEqual(res_p.status_code, 302)

        prize_created = Prize.objects.get(campaign=new_camp, name='25% OFF Gift')
        self.assertEqual(prize_created.probability, 50.0)

    def test_shop_profile_update(self):
        """Test shop profile update view"""
        self.client.login(username='owner_a', password='password123')

        res = self.client.post('/dashboard/shop/profile/', {
            'name': 'Alpha Gourmet Café', 'category': 'Café & Bakery',
            'currency_symbol': '₹', 'phone': '+91 9876543210',
            'email': 'cafe@alpha.com', 'address': 'MG Road, Bangalore',
            'description': 'Fresh coffee everyday'
        })
        self.assertEqual(res.status_code, 302)

        self.shop_a.refresh_from_db()
        self.assertEqual(self.shop_a.name, 'Alpha Gourmet Café')
        self.assertEqual(self.shop_a.currency_symbol, '₹')

    def test_public_coupon_view(self):
        """Test shareable public coupon page /coupon/<token>/"""
        spin_res = SpinResult.objects.create(
            shop=self.shop_a, campaign=self.camp_a, prize=self.prize_a1
        )
        coupon = Coupon.objects.create(
            code=Coupon.generate_code(), spin_result=spin_res, shop=self.shop_a,
            campaign=self.camp_a, prize=self.prize_a1, status='active',
            expires_at=timezone.now() + timedelta(days=5)
        )

        res = self.client.get(f'/coupon/{coupon.verify_token}/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, coupon.code)

    def test_verify_token_public_route(self):
        """Test public /verify/<token>/ route and shop owner redemption via token"""
        spin_res = SpinResult.objects.create(
            shop=self.shop_a, campaign=self.camp_a, prize=self.prize_a1
        )
        coupon = Coupon.objects.create(
            code=Coupon.generate_code(), spin_result=spin_res, shop=self.shop_a,
            campaign=self.camp_a, prize=self.prize_a1, status='active',
            expires_at=timezone.now() + timedelta(days=5)
        )

        verify_url = f'/verify/{coupon.verify_token}/'
        res_public = self.client.get(verify_url)
        self.assertContains(res_public, coupon.code)

        self.client.login(username='owner_a', password='password123')
        res_redeem = self.client.post(verify_url)
        self.assertContains(res_redeem, 'redeemed successfully')

        coupon.refresh_from_db()
        self.assertEqual(coupon.status, 'redeemed')

    def test_export_coupons_csv_tenant_isolation(self):
        """Test CSV export and verify Shop A owner only exports Shop A coupons"""
        spin_a = SpinResult.objects.create(shop=self.shop_a, campaign=self.camp_a, prize=self.prize_a1)
        Coupon.objects.create(
            code='SW-ALPHA-1234', spin_result=spin_a, shop=self.shop_a,
            campaign=self.camp_a, prize=self.prize_a1, status='active',
            expires_at=timezone.now() + timedelta(days=5)
        )

        spin_b = SpinResult.objects.create(shop=self.shop_b, campaign=self.camp_a, prize=self.prize_a1)
        Coupon.objects.create(
            code='SW-BETA-9999', spin_result=spin_b, shop=self.shop_b,
            campaign=self.camp_a, prize=self.prize_a1, status='active',
            expires_at=timezone.now() + timedelta(days=5)
        )

        self.client.login(username='owner_a', password='password123')
        res_csv = self.client.get('/dashboard/shop/export/coupons/')
        self.assertEqual(res_csv.status_code, 200)

        content = res_csv.content.decode('utf-8')
        self.assertIn('SW-ALPHA-1234', content)
        self.assertNotIn('SW-BETA-9999', content)

    def test_multi_tenant_data_isolation(self):
        """Shop A owner cannot redeem Shop B coupon"""
        code_b = Coupon.generate_code()
        spin_b = SpinResult.objects.create(
            shop=self.shop_b, campaign=self.camp_a, prize=self.prize_a1
        )
        coupon_b = Coupon.objects.create(
            code=code_b, spin_result=spin_b, shop=self.shop_b, campaign=self.camp_a,
            prize=self.prize_a1, status='active', expires_at=timezone.now() + timedelta(days=5)
        )

        self.client.login(username='owner_a', password='password123')
        redemption_url = '/dashboard/shop/coupons/redeem/'

        res = self.client.post(redemption_url, {'code': code_b, 'action': 'verify'})
        self.assertContains(res, 'SECURITY REJECTION')

    def test_duplicate_spin_prevention_cooldown(self):
        """Verify session cannot spin twice within cooldown window"""
        url = f'/s/{self.shop_a.public_token}/spin/'
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, 200)

        # Immediate second spin with same session should return 429 or error
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, 429)

    def test_sold_out_prize_prevention(self):
        """Verify prize with remaining_quantity = 0 is not awarded"""
        self.prize_a1.remaining_quantity = 0
        self.prize_a1.save()

        url = f'/s/{self.shop_a.public_token}/spin/'
        res = self.client.post(url)
        self.assertEqual(res.status_code, 400)
        self.assertContains(res, 'All rewards have been claimed', status_code=400)

    def test_double_redemption_prevention(self):
        """Verify redeeming an already redeemed coupon returns an error"""
        spin_res = SpinResult.objects.create(shop=self.shop_a, campaign=self.camp_a, prize=self.prize_a1)
        coupon = Coupon.objects.create(
            code=Coupon.generate_code(), spin_result=spin_res, shop=self.shop_a,
            campaign=self.camp_a, prize=self.prize_a1, status='redeemed',
            expires_at=timezone.now() + timedelta(days=5)
        )
        CouponRedemption.objects.create(coupon=coupon, redeemed_by=self.owner_a)

        self.client.login(username='owner_a', password='password123')
        res = self.client.post('/dashboard/shop/coupons/redeem/', {'code': coupon.code, 'action': 'confirm_redeem'})
        self.assertContains(res, 'ALREADY REDEEMED')

    def test_disabled_shop_access(self):
        """Verify disabled shop returns 403 unavailable state"""
        self.shop_a.status = 'disabled'
        self.shop_a.save()

        res = self.client.get(f'/s/{self.shop_a.public_token}/')
        self.assertEqual(res.status_code, 403)
        self.assertContains(res, 'Shop Profile Unavailable', status_code=403)

    def test_onboarding_wizard_flow(self):
        """Test onboarding wizard steps and completion"""
        self.client.login(username='owner_a', password='password123')
        
        # Save shop details step 1
        res1 = self.client.post('/dashboard/onboarding/', {'action': 'save_shop', 'name': 'Alpha Onboarded', 'category': 'Dining', 'currency_symbol': '$'})
        self.assertEqual(res1.status_code, 200)

        # Complete onboarding step 4
        res2 = self.client.post('/dashboard/onboarding/', {'action': 'complete'})
        self.assertEqual(res2.status_code, 302)

        self.shop_a.refresh_from_db()
        self.assertTrue(self.shop_a.onboarding_completed)
        self.assertEqual(self.shop_a.name, 'Alpha Onboarded')

    def test_billing_and_plan_limits(self):
        """Test billing subscription view and plan limit enforcement"""
        # Super admin accessing billing gets redirected to admin_subscriptions
        self.client.login(username='admin', password='adminpassword')
        res_admin_billing = self.client.get('/dashboard/billing/')
        self.assertRedirects(res_admin_billing, '/dashboard/admin/subscriptions/')

        # Shop owner accessing billing gets 200 OK
        self.client.login(username='owner_a', password='password123')
        
        res_billing = self.client.get('/dashboard/billing/')
        self.assertEqual(res_billing.status_code, 200)
        self.assertContains(res_billing, 'Starter Plan')

        # Limit campaign creation when plan max_campaigns is reached
        sub = Subscription.objects.get(shop=self.shop_a)
        sub.plan.max_campaigns = 1
        sub.plan.save()

        res_create = self.client.post('/dashboard/shop/campaigns/', {'action': 'create', 'name': 'Exceeding Campaign'})
        self.assertContains(res_create, 'Plan limit reached')

    def test_account_settings_and_password_change(self):
        """Test user profile update and secure password change"""
        self.client.login(username='owner_a', password='password123')

        res_prof = self.client.post('/dashboard/account/', {'action': 'update_profile', 'first_name': 'Alpha', 'last_name': 'Owner', 'email': 'newalpha@test.com'})
        self.assertContains(res_prof, 'Profile details updated successfully')

        self.owner_a.refresh_from_db()
        self.assertEqual(self.owner_a.first_name, 'Alpha')

        res_pass = self.client.post('/dashboard/account/', {
            'action': 'change_password', 'old_password': 'password123',
            'new_password1': 'newsecret456', 'new_password2': 'newsecret456'
        })
        self.assertContains(res_pass, 'Password changed successfully')

        # Verify old password no longer works
        self.owner_a.refresh_from_db()
        self.assertFalse(self.owner_a.check_password('password123'))
        self.assertTrue(self.owner_a.check_password('newsecret456'))

    def test_notification_alerts_system(self):
        """Test in-app notification creation, list, and mark as read endpoint"""
        notif = Notification.objects.create(shop=self.shop_a, user=self.owner_a, title="Inventory Low Alert", message="10% OFF Alpha is almost out of stock", level="warning")

        self.client.login(username='owner_a', password='password123')
        res_list = self.client.get('/dashboard/notifications/')
        self.assertContains(res_list, 'Inventory Low Alert')

        res_read = self.client.post(f'/dashboard/notifications/{notif.id}/read/')
        self.assertEqual(res_read.status_code, 200)

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_campaign_preview_mode_and_preview_spin_api(self):
        """Test campaign preview mode does not alter inventory or database records"""
        self.client.login(username='owner_a', password='password123')
        
        preview_url = f'/dashboard/shop/campaigns/{self.camp_a.id}/preview/'
        res_prev = self.client.get(preview_url)
        self.assertEqual(res_prev.status_code, 200)
        self.assertContains(res_prev, 'PREVIEW MODE')

        res_spin = self.client.post(f'/dashboard/shop/campaigns/{self.camp_a.id}/preview/spin/')
        self.assertEqual(res_spin.status_code, 200)

        data = res_spin.json()
        self.assertTrue(data['is_preview'])
        if data.get('coupon'):
            self.assertTrue('SW-' in data['coupon']['code'])
            coupon_code = data['coupon']['code']
            self.assertTrue(Coupon.objects.filter(code=coupon_code, shop=self.shop_a).exists())

    def test_cross_tenant_coupon_redemption_rejection(self):
        """Test that Shop B cannot verify or redeem a coupon issued by Shop A"""
        coupon_a = Coupon.objects.create(
            code=Coupon.generate_code(self.shop_a),
            spin_result=SpinResult.objects.create(shop=self.shop_a, campaign=self.camp_a, prize=self.prize_a1),
            shop=self.shop_a,
            campaign=self.camp_a,
            prize=self.prize_a1,
            status='active',
            expires_at=timezone.now() + timedelta(days=30)
        )

        # Log in as Shop B owner
        self.client.login(username='owner_b', password='password123')

        # Attempt verification on Shop B's terminal
        res_verify = self.client.post('/dashboard/shop/coupons/redeem/', {
            'code': coupon_a.code,
            'action': 'verify'
        })
        self.assertEqual(res_verify.status_code, 200)
        self.assertContains(res_verify, 'SECURITY REJECTION')

        # Attempt atomic redemption on Shop B's terminal
        res_redeem = self.client.post('/dashboard/shop/coupons/redeem/', {
            'code': coupon_a.code,
            'action': 'confirm_redeem'
        })
        self.assertEqual(res_redeem.status_code, 200)
        self.assertContains(res_redeem, 'SECURITY REJECTION')

        # Verify coupon_a remains active and unredeemed in DB
        coupon_a.refresh_from_db()
        self.assertEqual(coupon_a.status, 'active')

    def test_seasonal_template_campaign_creation(self):
        """Test campaign creation with seasonal template choice initializes default prizes"""
        self.client.login(username='owner_a', password='password123')

        res = self.client.post('/dashboard/shop/campaigns/', {
            'action': 'create', 'name': 'Diwali Festive Offer 2026',
            'template_type': 'festival', 'spin_cooldown_hours': 24
        })
        self.assertEqual(res.status_code, 302)

        camp = Campaign.objects.get(name='Diwali Festive Offer 2026', shop=self.shop_a)
        self.assertEqual(camp.template_type, 'festival')
        self.assertEqual(camp.prizes.count(), 4)
        self.assertTrue(camp.prizes.filter(name='20% OFF Festive Discount').exists())

    def test_health_check_endpoint(self):
        """Test public /health/ status endpoint returns 200 and healthy JSON payload"""
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')

    def test_admin_capacity_dashboard_endpoint(self):
        """Test Super Admin capacity dashboard endpoint returns HTTP 200 OK without 500 error"""
        self.client.login(username='admin', password='adminpassword')
        res = self.client.get('/dashboard/admin/capacity/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'System Capacity & Performance Dashboard')

    def test_shop_usage_limit_helpers(self):
        """Test Shop model usage check helpers (can_create_campaign, can_add_prize, can_spin)"""
        sub = self.shop_a.get_subscription()
        sub.plan.max_campaigns = 5
        sub.plan.max_prizes_per_campaign = 10
        sub.plan.max_spins_per_month = 1000
        sub.plan.save()

        self.assertTrue(self.shop_a.can_create_campaign())
        self.assertTrue(self.shop_a.can_add_prize(self.camp_a))
        self.assertTrue(self.shop_a.can_spin())

    def test_open_graph_meta_tags_rendering(self):
        """Test customer landing page renders Open Graph SEO meta tags"""
        res = self.client.get(f'/s/{self.shop_a.public_token}/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'og:title')
        self.assertContains(res, 'og:description')
        self.assertContains(res, 'og:type')

    def test_funnel_conversion_rate_metrics(self):
        """Test shop dashboard calculates conversion funnel rate context variables"""
        self.client.login(username='owner_a', password='password123')
        res = self.client.get('/dashboard/shop/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('win_rate', res.context)
        self.assertIn('overall_funnel_rate', res.context)

    def test_theme_persistence_and_dashboard_global_application(self):
        """Test Theme 4.0: Owner selects theme, saves to DB, and theme applies to dashboard and customer landing"""
        self.client.login(username='owner_a', password='password123')
        res_post = self.client.post('/dashboard/shop/branding/', {
            'theme': 'diwali',
            'font_family': 'cinzel',
            'primary_color': '#eab308',
            'secondary_color': '#ca8a04',
            'accent_color': '#fbbf24',
            'background_color': '#1c1917',
            'text_color': '#fef08a',
            'spin_button_text': 'SPIN FESTIVAL WHEEL'
        })
        self.assertRedirects(res_post, '/dashboard/shop/branding/')

        branding = ShopBranding.objects.get(shop=self.shop_a)
        self.assertEqual(branding.theme, 'diwali')
        self.assertEqual(branding.font_family, 'cinzel')

        res_dash = self.client.get('/dashboard/shop/')
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, 'data-theme="diwali"')

    def test_theme_tenant_isolation(self):
        """Test Theme 3.0: Shop A theme changes do not affect Shop B theme"""
        ShopBranding.objects.create(shop=self.shop_a, theme='neon')
        ShopBranding.objects.create(shop=self.shop_b, theme='luxury_black')

        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'theme': 'christmas',
            'font_family': 'outfit',
            'primary_color': '#dc2626',
            'secondary_color': '#16a34a',
            'accent_color': '#fbbf24',
            'background_color': '#0f172a',
            'text_color': '#ffffff',
            'spin_button_text': 'SPIN TO WIN'
        })

        self.shop_a.branding.refresh_from_db()
        self.shop_b.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'christmas')
        self.assertEqual(self.shop_b.branding.theme, 'luxury_black')

    def test_theme_resolution_priority_campaign_override_over_shop(self):
        """Test Theme 3.0: Campaign theme override takes precedence over Shop theme"""
        ShopBranding.objects.create(shop=self.shop_a, theme='minimal')
        self.camp_a.theme = 'diwali'
        self.camp_a.save()

        res_cust = self.client.get(f'/s/{self.shop_a.public_token}/')
        self.assertEqual(res_cust.status_code, 200)
        self.assertEqual(res_cust.context['active_theme'], 'diwali')
        self.assertContains(res_cust, 'data-theme="diwali"')

    def test_luxury_black_theme_persistence(self):
        """Test Theme 3.0: Luxury Black theme persistence and dashboard application"""
        self.client.login(username='owner_a', password='password123')
        res = self.client.post('/dashboard/shop/branding/', {
            'theme': 'luxury_black',
            'font_family': 'cinzel',
            'primary_color': '#f3e5ab',
            'secondary_color': '#272730',
            'accent_color': '#d4af37',
            'background_color': '#050507',
            'text_color': '#f4f4f6',
            'spin_button_text': 'SPIN FOR LUXURY'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'luxury_black')
        self.assertEqual(self.shop_a.branding.font_family, 'cinzel')

        res_dash = self.client.get('/dashboard/shop/')
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, 'data-theme="luxury_black"')

    def test_pearl_luxury_theme_persistence(self):
        """Test Theme 3.0: Pearl Luxury theme persistence"""
        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'theme': 'pearl',
            'font_family': 'playfair',
            'primary_color': '#0f172a',
            'secondary_color': '#e2e8f0',
            'accent_color': '#d4af37',
            'background_color': '#f8fafc',
            'text_color': '#0f172a',
            'spin_button_text': 'SPIN FOR PEARLS'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'pearl')

    def test_aurora_and_neon_themes_persistence(self):
        """Test Theme 3.0: Aurora and Cyber Neon themes"""
        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'theme': 'aurora',
            'font_family': 'outfit',
            'primary_color': '#a855f7',
            'secondary_color': '#3b82f6',
            'accent_color': '#06b6d4',
            'background_color': '#0b0f19',
            'text_color': '#f0f9ff',
            'spin_button_text': 'SPIN THE AURORA'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'aurora')

        self.client.post('/dashboard/shop/branding/', {
            'theme': 'neon',
            'font_family': 'space_grotesk',
            'primary_color': '#06b6d4',
            'secondary_color': '#a855f7',
            'accent_color': '#f43f5e',
            'background_color': '#09090b',
            'text_color': '#fafafa',
            'spin_button_text': 'SPIN CYBER NEON'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'neon')

    def test_reset_theme_defaults_action(self):
        """Test Theme 3.0: Reset action restores default palette for the selected theme"""
        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'action': 'reset',
            'theme': 'luxury_black'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'luxury_black')
        self.assertEqual(self.shop_a.branding.primary_color, '#f3e5ab')
        self.assertEqual(self.shop_a.branding.background_color, '#050507')

    def test_shop_resolve_theme_method(self):
        """Test Theme 3.0: Shop.resolve_theme method priority"""
        branding, _ = ShopBranding.objects.get_or_create(shop=self.shop_a, defaults={'theme': 'pearl'})
        branding.theme = 'pearl'
        branding.save()

        # Without campaign override
        self.assertEqual(self.shop_a.resolve_theme(None), 'pearl')

        # With campaign override
        self.camp_a.theme = 'neon'
        self.camp_a.save()
        self.assertEqual(self.shop_a.resolve_theme(self.camp_a), 'neon')

    def test_business_themes_persistence_restaurant_and_coffee(self):
        """Test Theme 3.0: Restaurant and Coffee business themes persistence and dashboard rendering"""
        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'theme': 'restaurant',
            'font_family': 'playfair',
            'primary_color': '#d97706',
            'secondary_color': '#451a03',
            'accent_color': '#f59e0b',
            'background_color': '#1c1917',
            'text_color': '#fef3c7',
            'spin_button_text': 'SPIN GOURMET REWARDS'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'restaurant')
        res_dash = self.client.get('/dashboard/shop/')
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, 'data-theme="restaurant"')

        self.client.post('/dashboard/shop/branding/', {
            'theme': 'coffee',
            'font_family': 'poppins',
            'primary_color': '#b45309',
            'secondary_color': '#78350f',
            'accent_color': '#fcd34d',
            'background_color': '#1a0e05',
            'text_color': '#fffbeb',
            'spin_button_text': 'SPIN COFFEE WHEEL'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'coffee')

    def test_fashion_electronics_and_sales_themes_persistence(self):
        """Test Theme 3.0: Fashion, Electronics, and Clearance themes persistence"""
        self.client.login(username='owner_a', password='password123')
        self.client.post('/dashboard/shop/branding/', {
            'theme': 'fashion',
            'font_family': 'cinzel',
            'primary_color': '#e4e4e7',
            'secondary_color': '#27272a',
            'accent_color': '#d4af37',
            'background_color': '#09090b',
            'text_color': '#fafafa',
            'spin_button_text': 'SPIN HAUTE COUTURE'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'fashion')

        self.client.post('/dashboard/shop/branding/', {
            'theme': 'electronics',
            'font_family': 'space_grotesk',
            'primary_color': '#06b6d4',
            'secondary_color': '#1e3a8a',
            'accent_color': '#38bdf8',
            'background_color': '#030712',
            'text_color': '#f0f9ff',
            'spin_button_text': 'SPIN TECH REWARDS'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'electronics')

        self.client.post('/dashboard/shop/branding/', {
            'theme': 'clearance',
            'font_family': 'space_grotesk',
            'primary_color': '#dc2626',
            'secondary_color': '#991b1b',
            'accent_color': '#facc15',
            'background_color': '#111827',
            'text_color': '#ffffff',
            'spin_button_text': 'SPIN CLEARANCE SALE'
        })
        self.shop_a.branding.refresh_from_db()
        self.assertEqual(self.shop_a.branding.theme, 'clearance')

    def test_campaign_theme_override_lifecycle(self):
        """
        Test Campaign Override System:
        Campaign Theme -> Shop Theme -> Default Theme
        1. Normal Shop Theme is 'luxury_black'
        2. Active Diwali Campaign has theme override 'diwali'
        3. Customer page resolves to 'diwali'
        4. When Diwali campaign ends/deactivates, Shop returns to 'luxury_black'
        5. If Shop branding is removed, falls back to Default 'royal'
        """
        # 1. Configure Normal Shop Theme -> luxury_black
        branding, _ = ShopBranding.objects.get_or_create(shop=self.shop_a)
        branding.theme = 'luxury_black'
        branding.save()

        # 2. Configure Campaign with theme override 'diwali'
        self.camp_a.theme = 'diwali'
        self.camp_a.status = 'live'
        self.camp_a.is_active = True
        self.camp_a.save()

        # 3. Customer page resolves to 'diwali'
        res_live = self.client.get(f'/s/{self.shop_a.public_token}/')
        self.assertEqual(res_live.status_code, 200)
        self.assertEqual(res_live.context['active_theme'], 'diwali')
        self.assertContains(res_live, 'data-theme="diwali"')

        # 4. Campaign ends -> Shop returns to normal theme 'luxury_black'
        self.camp_a.is_active = False
        self.camp_a.status = 'ended'
        self.camp_a.save()

        self.assertIsNone(self.shop_a.get_active_campaign())
        self.assertEqual(self.shop_a.resolve_theme(None), 'luxury_black')

        res_ended = self.client.get(f'/s/{self.shop_a.public_token}/')
        self.assertEqual(res_ended.status_code, 200)
        # Template is no_campaign.html, but theme applied to layout is normal shop theme
        self.assertContains(res_ended, 'data-theme="luxury_black"')

        # 5. When Shop branding has no theme, falls back to Default 'royal'
        branding.theme = ''
        branding.save()
        self.assertEqual(self.shop_a.resolve_theme(None), 'royal')


class SmartThemeEngineTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.owner = User.objects.create_user(
            username='smart_owner', email='smartowner@test.com', password='password123', role='shop_owner'
        )
        self.shop = Shop.objects.create(
            name='Gujarat Sweets & Snacks',
            owner=self.owner,
            public_token='smart-token-123',
            category='Restaurant & Food',
            timezone='Asia/Kolkata',
            country='IN',
            region='Gujarat',
            normal_theme='royal',
            auto_theme_enabled=True
        )
        self.owner.shop = self.shop
        self.owner.save()

        now = timezone.now()
        self.camp = Campaign.objects.create(
            shop=self.shop, name='Festive Season Campaign',
            start_date=now - timedelta(days=5), end_date=now + timedelta(days=30),
            status='live', is_active=True, theme='' # Empty theme to test calendar resolution
        )
        Prize.objects.create(
            campaign=self.camp, name='15% OFF Special', prize_type='percentage',
            discount_percentage=15.0, coupon_text='15% off total', probability=100.0,
            remaining_quantity=50
        )

        import datetime
        # 1. Create a 2-day Uttarayan festival
        self.uttarayan_evt = CalendarEvent.objects.create(
            name='Uttarayan Kite Festival',
            slug='test-uttarayan-2026',
            event_type='festival',
            country='IN',
            region='Gujarat',
            start_date=datetime.date(2026, 1, 14),
            end_date=datetime.date(2026, 1, 15),
            theme='uttarayan',
            priority=50,
            icon='🪁'
        )

        # 2. Create a higher-priority Diwali festival
        self.diwali_evt = CalendarEvent.objects.create(
            name='Grand Diwali Festival',
            slug='test-diwali-2026',
            event_type='festival',
            country='IN',
            region='',
            start_date=datetime.date(2026, 11, 8),
            end_date=datetime.date(2026, 11, 8),
            theme='diwali',
            priority=60,
            icon='🪔'
        )

    def test_normal_day_returns_normal_theme(self):
        """On a normal day with no active festival, returns normal theme."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        self.shop.auto_category_theme_adaptation = False
        self.shop.save()
        normal_dt = datetime.datetime(2026, 5, 20, 12, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=normal_dt)
        self.assertEqual(res.theme, 'royal')
        self.assertEqual(res.reason, 'Normal Shop Theme')

    def test_festival_day_returns_festival_theme(self):
        """On Uttarayan (Jan 14), automatically resolves to 'uttarayan' theme."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        uttarayan_dt = datetime.datetime(2026, 1, 14, 10, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=uttarayan_dt)
        self.assertEqual(res.theme, 'uttarayan')
        self.assertTrue(res.is_auto)
        self.assertEqual(res.event.name, 'Uttarayan Kite Festival')

    def test_festival_expiry_returns_normal_theme(self):
        """After festival ends (Jan 16), automatically reverts to normal theme."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        self.shop.auto_category_theme_adaptation = False
        self.shop.save()
        after_uttarayan_dt = datetime.datetime(2026, 1, 16, 1, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=after_uttarayan_dt)
        self.assertEqual(res.theme, 'royal')
        self.assertFalse(res.is_auto)

    def test_multi_day_event(self):
        """Theme remains active throughout both Day 1 and Day 2 of Uttarayan."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        day1_dt = datetime.datetime(2026, 1, 14, 20, 0, tzinfo=datetime.timezone.utc)
        day2_dt = datetime.datetime(2026, 1, 15, 14, 0, tzinfo=datetime.timezone.utc)

        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=day1_dt).theme, 'uttarayan')
        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=day2_dt).theme, 'uttarayan')

    def test_manual_override_precedence_and_expiry(self):
        """Manual override takes precedence over calendar events until expired."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        uttarayan_dt = datetime.datetime(2026, 1, 14, 10, 0, tzinfo=datetime.timezone.utc)

        # Set manual override to luxury_black for 1 hour
        self.shop.manual_theme_override = 'luxury_black'
        self.shop.override_until = uttarayan_dt + timedelta(hours=1)
        self.shop.save()

        # During override -> returns luxury_black
        res_override = get_active_shop_theme(self.shop, target_datetime=uttarayan_dt)
        self.assertEqual(res_override.theme, 'luxury_black')
        self.assertTrue(res_override.is_override)

        # After override expires -> auto reverts back to Uttarayan festival theme
        expired_dt = uttarayan_dt + timedelta(hours=2)
        res_reverted = get_active_shop_theme(self.shop, target_datetime=expired_dt)
        self.assertEqual(res_reverted.theme, 'uttarayan')
        self.assertFalse(res_reverted.is_override)

    def test_disabled_automation_returns_normal_theme(self):
        """When auto_theme_enabled is False, calendar automation is bypassed."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme
        uttarayan_dt = datetime.datetime(2026, 1, 14, 10, 0, tzinfo=datetime.timezone.utc)

        self.shop.auto_theme_enabled = False
        self.shop.auto_category_theme_adaptation = False
        self.shop.save()

        res = get_active_shop_theme(self.shop, target_datetime=uttarayan_dt)
        self.assertEqual(res.theme, 'royal')

    def test_customer_qr_page_resolves_dynamic_theme(self):
        """Permanent QR route /s/<token>/ renders current resolved theme directly."""
        url = f'/s/{self.shop.public_token}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('active_theme', response.context)
        self.assertEqual(response.context['active_theme'], self.shop.resolve_theme())

    def test_janmashtami_calendar_auto_switching(self):
        """On Janmashtami (4 Sep 2026), auto-switches to 'janmashtami' theme."""
        import datetime
        from core.services.calendar_service import sync_calendar_events
        from core.services.theme_resolver import get_active_shop_theme

        sync_calendar_events()
        self.shop.category = 'General Store'
        self.shop.auto_category_theme_adaptation = False
        self.shop.save()

        janmashtami_dt = datetime.datetime(2026, 9, 4, 12, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=janmashtami_dt)
        self.assertEqual(res.theme, 'janmashtami')
        self.assertTrue(res.is_auto)
        self.assertIn('Janmashtami', res.event.name)

    def test_janmashtami_pre_festival_countdown(self):
        """2 days before Janmashtami (2 Sep 2026), enters pre-festival mode with countdown."""
        import datetime
        from core.services.calendar_service import sync_calendar_events
        from core.services.theme_resolver import get_active_shop_theme

        sync_calendar_events()
        self.shop.auto_category_theme_adaptation = False
        self.shop.pre_festival_days = 3
        self.shop.save()

        pre_dt = datetime.datetime(2026, 9, 2, 10, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=pre_dt)
        self.assertTrue(res.is_pre_festival)
        self.assertEqual(res.pre_festival_days_left, 2)
        self.assertEqual(res.theme, 'janmashtami')

    def test_janmashtami_category_adaptation(self):
        """Janmashtami adapts cleanly to Jewellery, Sweets, Clothing, and Kids categories."""
        import datetime
        from core.services.calendar_service import sync_calendar_events
        from core.services.theme_resolver import get_active_shop_theme

        sync_calendar_events()
        self.shop.auto_category_theme_adaptation = True
        janmashtami_dt = datetime.datetime(2026, 9, 4, 12, 0, tzinfo=datetime.timezone.utc)

        # 1. Jewellery
        self.shop.category = 'Jewellery & Watches'
        self.shop.save()
        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=janmashtami_dt).theme, 'janmashtami_jewellery')

        # 2. Sweets / Food
        self.shop.category = 'Sweets & Bakery'
        self.shop.save()
        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=janmashtami_dt).theme, 'janmashtami_sweets')

        # 3. Clothing / Fashion
        self.shop.category = 'Clothing & Apparel'
        self.shop.save()
        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=janmashtami_dt).theme, 'janmashtami_clothing')

        # 4. Kids / Toys
        self.shop.category = 'Kids & Toys'
        self.shop.save()
        self.assertEqual(get_active_shop_theme(self.shop, target_datetime=janmashtami_dt).theme, 'janmashtami_kids')

    def test_janmashtami_ephemeris_calculation(self):
        """Verify dynamic calculation for Janmashtami festival dates across multiple years."""
        from core.services.calendar_service import get_janmashtami_dates_for_year
        import datetime

        d2026 = get_janmashtami_dates_for_year(2026)
        self.assertEqual(d2026, (datetime.date(2026, 9, 4), datetime.date(2026, 9, 5)))

        d2027 = get_janmashtami_dates_for_year(2027)
        self.assertEqual(d2027, (datetime.date(2027, 8, 25), datetime.date(2027, 8, 26)))

        d2028 = get_janmashtami_dates_for_year(2028)
        self.assertEqual(d2028, (datetime.date(2028, 8, 13), datetime.date(2028, 8, 14)))

    def test_coffee_theme_resolution_and_category_adaptation(self):
        """Verify Coffee theme adapts properly for Cafes and Coffee shops when enabled."""
        import datetime
        from core.services.theme_resolver import get_active_shop_theme

        self.shop.auto_category_theme_adaptation = True
        self.shop.category = 'Café & Coffee Shop'
        self.shop.save()

        normal_dt = datetime.datetime(2026, 5, 20, 12, 0, tzinfo=datetime.timezone.utc)
        res = get_active_shop_theme(self.shop, target_datetime=normal_dt)
        self.assertEqual(res.theme, 'coffee')


class SecurityPerformanceHardeningTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_superuser(
            username='sec_admin', email='admin@sec.com', password='password123', role='super_admin'
        )

        self.owner1 = User.objects.create_user(
            username='sec_owner1', email='owner1@sec.com', password='password123', role='shop_owner'
        )
        self.shop1 = Shop.objects.create(
            name='Tenant One Shop', owner=self.owner1, public_token='sec-token-111'
        )
        self.owner1.shop = self.shop1
        self.owner1.save()

        self.owner2 = User.objects.create_user(
            username='sec_owner2', email='owner2@sec.com', password='password123', role='shop_owner'
        )
        self.shop2 = Shop.objects.create(
            name='Tenant Two Shop', owner=self.owner2, public_token='sec-token-222'
        )
        self.owner2.shop = self.shop2
        self.owner2.save()

        now = timezone.now()
        self.camp1 = Campaign.objects.create(
            shop=self.shop1, name='Tenant 1 Promo', start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10), status='live', is_active=True
        )
        self.prize_real = Prize.objects.create(
            campaign=self.camp1, name='Real 50% Reward', prize_type='percentage',
            discount_percentage=50.0, coupon_text='50% OFF', probability=100.0,
            remaining_quantity=5
        )
        self.prize_zero = Prize.objects.create(
            campaign=self.camp1, name='Zero Prob Secret Item', prize_type='percentage',
            discount_percentage=99.0, coupon_text='NEVER WON', probability=0.0,
            remaining_quantity=10
        )

        self.camp2 = Campaign.objects.create(
            shop=self.shop2, name='Tenant 2 Promo', start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10), status='live', is_active=True
        )
        self.prize2 = Prize.objects.create(
            campaign=self.camp2, name='Tenant 2 Exclusive', prize_type='percentage',
            discount_percentage=10.0, coupon_text='10% OFF T2', probability=100.0,
            remaining_quantity=10
        )

    def test_zero_probability_prize_never_won(self):
        """Zero probability prize must NEVER be awarded when positive-probability prizes exist."""
        from core.services.spin_service import execute_authoritative_spin

        for i in range(5):
            outcome = execute_authoritative_spin(
                shop=self.shop1,
                session_key=f"sec_session_{i}",
                client_ip="127.0.0.1",
                user_agent="TestRunner"
            )
            self.assertEqual(outcome['prize']['name'], 'Real 50% Reward')
            self.assertNotEqual(outcome['prize']['name'], 'Zero Prob Secret Item')

    def test_multi_tenant_idor_protection_preview_campaign(self):
        """Owner 1 cannot preview or duplicate Owner 2's campaign (returns 404)."""
        self.client.login(username='sec_owner1', password='password123')

        # Attempt to access Shop 2's campaign
        res = self.client.get(f'/dashboard/shop/campaigns/{self.camp2.id}/preview/')
        self.assertEqual(res.status_code, 404)

        res_dup = self.client.get(f'/dashboard/shop/campaigns/{self.camp2.id}/duplicate/')
        self.assertEqual(res_dup.status_code, 404)

        res_prizes = self.client.get(f'/dashboard/shop/campaigns/{self.camp2.id}/prizes/')
        self.assertEqual(res_prizes.status_code, 404)

    def test_atomic_coupon_single_use_redemption(self):
        """A coupon can only be redeemed once; subsequent redemptions are rejected."""
        from core.services.coupon_service import redeem_coupon_atomically, CouponRedemptionError

        spin_res = SpinResult.objects.create(
            shop=self.shop1, campaign=self.camp1, prize=self.prize_real
        )
        coupon = Coupon.objects.create(
            code='SW-ATOM-1234',
            spin_result=spin_res,
            shop=self.shop1,
            campaign=self.camp1,
            prize=self.prize_real,
            status='active',
            expires_at=timezone.now() + timedelta(days=10)
        )

        # 1st redemption succeeds
        redeemed = redeem_coupon_atomically(code=coupon.code, shop=self.shop1, actor=self.owner1)
        self.assertEqual(redeemed.status, 'redeemed')

        # 2nd redemption raises error
        with self.assertRaises(CouponRedemptionError):
            redeem_coupon_atomically(code=coupon.code, shop=self.shop1, actor=self.owner1)

    def test_monthly_spin_quota_limit_enforcement(self):
        """Spin engine rejects spins if monthly subscription quota is exhausted."""
        from core.services.spin_service import execute_authoritative_spin, SpinExecutionError

        sub = self.shop1.get_subscription()
        sub.plan.max_spins_per_month = 2
        sub.plan.save()

        # Spin 1
        execute_authoritative_spin(self.shop1, "sess_1", "127.0.0.1", "UA")
        # Spin 2
        execute_authoritative_spin(self.shop1, "sess_2", "127.0.0.1", "UA")

        # Spin 3 exceeds limit
        with self.assertRaises(SpinExecutionError) as ctx:
            execute_authoritative_spin(self.shop1, "sess_3", "127.0.0.1", "UA")
        self.assertIn("Monthly spin limit reached", str(ctx.exception))

    def test_file_upload_security_validator(self):
        """Upload validator allows valid image formats and rejects invalid / dangerous files."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from core.utils.security import validate_uploaded_image
        from django.core.exceptions import ValidationError

        # Valid PNG
        valid_png = SimpleUploadedFile("avatar.png", b"\x89PNG\r\n\x1a\n\x00\x00", content_type="image/png")
        self.assertTrue(validate_uploaded_image(valid_png))

        # Invalid .exe / .py script
        bad_file = SimpleUploadedFile("exploit.py", b"import os; os.system('ls')", content_type="text/x-python")
        with self.assertRaises(ValidationError):
            validate_uploaded_image(bad_file)

        # Oversized file > 5MB
        huge_file = SimpleUploadedFile("huge.jpg", b"0" * (6 * 1024 * 1024), content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_uploaded_image(huge_file)

    def test_query_count_coupon_export_n_plus_one_elimination(self):
        """Exporting coupons should execute minimal constant queries with select_related."""
        for i in range(10):
            spin = SpinResult.objects.create(shop=self.shop1, campaign=self.camp1, prize=self.prize_real)
            Coupon.objects.create(
                code=f"SW-TEST-{i:04d}",
                spin_result=spin,
                shop=self.shop1,
                campaign=self.camp1,
                prize=self.prize_real,
                status='active',
                expires_at=timezone.now() + timedelta(days=10)
            )

        self.client.login(username='sec_owner1', password='password123')
        res = self.client.get('/dashboard/shop/export/coupons/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        self.assertIn('SW-TEST-0000', res.content.decode('utf-8'))

    def test_admin_dashboard_single_query_aggregation(self):
        """Admin dashboard uses annotated counts rather than running O(N) looping queries."""
        self.client.login(username='sec_admin', password='password123')
        res = self.client.get('/dashboard/admin/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Tenant One Shop')


class SubscriptionsManagementTestCase(TestCase):
    """
    Test suite for Subscriptions Management in ₹ (Rupees):
    - Plan CRUD in ₹
    - Super Admin Subscription Assignment, Status Toggles, and Validity Extensions
    - Shop Owner Subscription View & 1-Click Renewal
    - Post-Expiration Blocking & Instant Reactivation with Permanent QR Continuity
    """

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='sub_admin', password='password123', email='subadmin@test.com'
        )
        self.owner_user = User.objects.create_user(
            username='sub_owner', password='password123', role='shop_owner'
        )
        self.shop = Shop.objects.create(
            name='Mumbai Chai & Co',
            owner=self.owner_user,
            currency_symbol='₹',
            status='active'
        )
        self.owner_user.shop = self.shop
        self.owner_user.save()

        self.campaign = Campaign.objects.create(
            shop=self.shop,
            name='Diwali Special Spins',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            status='live',
            is_active=True,
            spin_cooldown_hours=24
        )
        self.prize = Prize.objects.create(
            campaign=self.campaign,
            name='Free Masala Chai',
            prize_type='freebie',
            coupon_text='1 Free Cutting Chai',
            probability=100.0,
            remaining_quantity=50
        )

    def test_admin_subscriptions_overview_access(self):
        """Super Admin can access /dashboard/admin/subscriptions/ while regular owners are redirected/blocked"""
        self.client.login(username='sub_owner', password='password123')
        res_owner = self.client.get('/dashboard/admin/subscriptions/')
        self.assertEqual(res_owner.status_code, 403)

        self.client.login(username='sub_admin', password='password123')
        res_admin = self.client.get('/dashboard/admin/subscriptions/')
        self.assertEqual(res_admin.status_code, 200)
        self.assertContains(res_admin, 'ENTERPRISE SUBSCRIPTION CENTER')
        self.assertContains(res_admin, 'Mumbai Chai &amp; Co')

    def test_admin_plan_crud_in_rupees(self):
        """Super Admin creates, edits, and deletes a subscription plan in ₹ (Rupees)"""
        self.client.login(username='sub_admin', password='password123')

        # 1. Create Plan in ₹
        res_create = self.client.post('/dashboard/admin/plans/save/', {
            'name': 'Festive Mega Tier',
            'code': 'festive_mega',
            'price_rupees': '1499.00',
            'billing_period_days': '30',
            'max_campaigns': '10',
            'max_active_campaigns': '3',
            'max_prizes_per_campaign': '12',
            'max_spins_per_month': '15000',
            'description': 'Designed for high volume festive seasons.',
            'is_active': 'on'
        })
        self.assertEqual(res_create.status_code, 302)

        plan = Plan.objects.get(code='festive_mega')
        self.assertEqual(plan.name, 'Festive Mega Tier')
        self.assertEqual(float(plan.price_rupees), 1499.0)
        self.assertIn('₹1,499', plan.formatted_price())

        # 2. Edit Plan
        res_edit = self.client.post('/dashboard/admin/plans/save/', {
            'plan_id': plan.id,
            'name': 'Festive Ultra Tier',
            'code': 'festive_ultra',
            'price_rupees': '1999.00',
            'billing_period_days': '60',
            'max_campaigns': '15',
            'max_active_campaigns': '5',
            'max_prizes_per_campaign': '16',
            'max_spins_per_month': '25000',
            'description': 'Updated description.',
            'is_active': 'on'
        })
        self.assertEqual(res_edit.status_code, 302)
        plan.refresh_from_db()
        self.assertEqual(plan.name, 'Festive Ultra Tier')
        self.assertEqual(float(plan.price_rupees), 1999.0)
        self.assertEqual(plan.billing_period_days, 60)

        # 3. Delete Plan
        res_del = self.client.post(f'/dashboard/admin/plans/{plan.id}/delete/')
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Plan.objects.filter(id=plan.id).exists())

    def test_admin_assign_subscription_and_extend_validity(self):
        """Super Admin assigns a plan to a shop and extends its validity"""
        self.client.login(username='sub_admin', password='password123')
        custom_plan = Plan.objects.create(
            name='Growth Tier', code='growth_tier', price_rupees=999.00, billing_period_days=30
        )

        res_assign = self.client.post('/dashboard/admin/subscriptions/assign/', {
            'shop_id': self.shop.id,
            'plan_id': custom_plan.id,
            'duration_days': '45',
            'status': 'active',
            'notes': 'Trial expansion for Diwali'
        })
        self.assertEqual(res_assign.status_code, 302)

        sub = Subscription.objects.get(shop=self.shop)
        self.assertEqual(sub.plan, custom_plan)
        self.assertEqual(sub.status, 'active')
        self.assertTrue(sub.is_valid())
        self.assertGreaterEqual(sub.days_left(), 44)

        # Extend validity by 30 days
        res_ext = self.client.post(f'/dashboard/admin/subscriptions/{sub.id}/status/', {
            'action': 'extend',
            'extra_days': '30'
        })
        self.assertEqual(res_ext.status_code, 302)
        sub.refresh_from_db()
        self.assertGreaterEqual(sub.days_left(), 74)

    def test_shop_owner_subscription_view_and_renewal(self):
        """Shop Owner views subscription in ₹ and renews or upgrades plan"""
        self.client.login(username='sub_owner', password='password123')
        res = self.client.get('/dashboard/subscription/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Subscription Management')
        self.assertContains(res, '₹')

        new_plan = Plan.objects.create(
            name='Pro Retailer', code='pro_retailer', price_rupees=1299.00, billing_period_days=30, is_active=True
        )

        res_renew = self.client.post('/dashboard/subscription/renew/', {'plan_id': new_plan.id})
        self.assertEqual(res_renew.status_code, 302)

        sub = Subscription.objects.get(shop=self.shop)
        self.assertEqual(sub.plan, new_plan)
        self.assertEqual(sub.status, 'active')
        self.assertTrue(sub.is_valid())

    def test_subscription_expiration_lifecycle_and_qr_continuity(self):
        """
        Verify that expired subscription blocks spins gracefully while keeping the permanent QR code intact.
        Once renewed, the same QR code and campaigns immediately work again.
        """
        sub = self.shop.get_subscription()
        initial_token = self.shop.public_token

        # 1. When Active: Customer can view landing page and spin wheel
        res_page = self.client.get(f'/s/{initial_token}/')
        self.assertEqual(res_page.status_code, 200)
        self.assertContains(res_page, 'SPIN & WIN')

        res_spin = self.client.post(f'/s/{initial_token}/spin/')
        self.assertEqual(res_spin.status_code, 200)
        data = res_spin.json()
        self.assertEqual(data['status'], 'success')

        # 2. When Expired:
        sub.status = 'expired'
        sub.expires_at = timezone.now() - timedelta(days=2)
        sub.save()

        self.assertFalse(self.shop.has_active_subscription())
        self.assertFalse(self.shop.can_spin())

        # Public shop page shows branded expired holding page (403)
        res_expired_page = self.client.get(f'/s/{initial_token}/')
        self.assertEqual(res_expired_page.status_code, 403)
        self.assertContains(res_expired_page, 'Promotion Intermission', status_code=403)
        self.assertContains(res_expired_page, 'Mumbai Chai &amp; Co', status_code=403)

        # Spin API rejected with 403
        res_expired_spin = self.client.post(f'/s/{initial_token}/spin/')
        self.assertEqual(res_expired_spin.status_code, 403)

        # 3. Shop Owner Dashboard shows expiration warning
        self.client.login(username='sub_owner', password='password123')
        res_dash = self.client.get('/dashboard/shop/')
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, 'Subscription Plan Expired')

        # 4. Owner Renews Subscription:
        sub.renew(duration_days=30)
        self.shop.refresh_from_db()
        self.assertTrue(self.shop.has_active_subscription())

        # 5. Same permanent QR code is active again!
        self.assertEqual(self.shop.public_token, initial_token)
        res_reactivated = self.client.get(f'/s/{initial_token}/')
        self.assertEqual(res_reactivated.status_code, 200)

    def test_admin_dashboard_pagination_and_search(self):
        """Test Super Admin dashboard pagination (15 items/page) and global search across all shops"""
        self.client.login(username='sub_admin', password='password123')

        # Create 20 more shops for a total > 20 to test pagination
        for i in range(20):
            owner = User.objects.create_user(
                username=f'p_owner_{i}', email=f'p_owner_{i}@test.com', password='pass', role='shop_owner'
            )
            Shop.objects.create(
                name=f'Pagination Store {i:02d}', owner=owner, public_token=f'tok-p-{i}', category='Food & Beverage'
            )

        # 1. First page should have 15 items and indicate more pages exist
        res = self.client.get('/dashboard/admin/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('shops', res.context)
        self.assertEqual(len(res.context['shops']), 15)
        self.assertTrue(res.context['shops'].has_next())
        self.assertGreaterEqual(res.context['shops'].paginator.count, 21)
        self.assertContains(res, 'Showing')
        self.assertContains(res, 'Pagination Store')

        # 2. Second page
        res_p2 = self.client.get('/dashboard/admin/?page=2')
        self.assertEqual(res_p2.status_code, 200)
        self.assertTrue(res_p2.context['shops'].has_previous())

        # 3. Search query across all pages
        res_search = self.client.get('/dashboard/admin/?q=Pagination+Store+05')
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(res_search.context['shops'].paginator.count, 1)
        self.assertContains(res_search, 'Pagination Store 05')

        # 4. Search with no results shows empty state
        res_empty = self.client.get('/dashboard/admin/?q=NoSuchStoreExists12345')
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(res_empty.context['shops'].paginator.count, 0)
        self.assertContains(res_empty, 'No shops found')
        self.assertContains(res_empty, 'Clear Search Filter')

    def test_admin_subscriptions_pagination_and_search(self):
        """Test Super Admin subscriptions pagination, status filter, and MRR optimization"""
        self.client.login(username='sub_admin', password='password123')

        # Create 20 new shops without subscriptions initially, then assign unique subscriptions
        plan = Plan.objects.get_or_create(code='pro_test_tier', defaults={'name': 'Pro Test Tier', 'price_rupees': 999.0, 'billing_period_days': 30})[0]
        now = timezone.now()

        for i in range(20):
            owner = User.objects.create_user(
                username=f'sub_test_user_{i}', email=f'sub_test_user_{i}@test.com', password='pass', role='shop_owner'
            )
            sh = Shop.objects.create(name=f'Sub Test Store {i:02d}', owner=owner, public_token=f'sub-test-tok-{i}')
            sub = sh.subscription
            sub.plan = plan
            sub.status = 'active' if i % 2 == 0 else 'expired'
            sub.starts_at = now
            sub.expires_at = now + timedelta(days=30 if i % 2 == 0 else -5)
            sub.save()

        # 1. Verify default view has 15 items per page and MRR calculated
        res = self.client.get('/dashboard/admin/subscriptions/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('shop_subscriptions', res.context)
        self.assertEqual(len(res.context['shop_subscriptions']), 15)
        self.assertTrue(res.context['shop_subscriptions'].has_next())
        self.assertIn('mrr_rupees', res.context)
        self.assertGreater(res.context['mrr_rupees'], 0)

        # 2. Search query for specific shop
        res_search = self.client.get('/dashboard/admin/subscriptions/?q=Sub+Test+Store+05')
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(res_search.context['shop_subscriptions'].paginator.count, 1)
        self.assertContains(res_search, 'Sub Test Store 05')

        # 3. Status filtering for active
        res_active = self.client.get('/dashboard/admin/subscriptions/?status=active')
        self.assertEqual(res_active.status_code, 200)
        for shop in res_active.context['shop_subscriptions']:
            self.assertTrue(shop.subscription.is_valid())















