import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import User, Shop, Campaign, Prize, Coupon, SpinResult, Notification, ActivityLog
from core.views import parse_decimal_safe, parse_float_safe, parse_int_safe, get_error_context
from core.services.spin_service import execute_authoritative_spin, SpinExecutionError
from core.services.coupon_service import redeem_coupon_atomically, CouponRedemptionError

class HardeningAndReliabilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="shopowner_test",
            password="testpassword123",
            role="shop_owner"
        )
        self.shop = Shop.objects.create(
            name="Test Hardened Boutique",
            owner=self.owner,
            public_token="test-boutique-token",
            status="active"
        )
        self.owner.shop = self.shop
        self.owner.save(update_fields=['shop'])

        # Ensure subscription is active for shop
        sub = self.shop.get_subscription()
        sub.status = 'active'
        sub.expires_at = timezone.now() + timezone.timedelta(days=365)
        sub.save()

        self.campaign = Campaign.objects.create(
            shop=self.shop,
            name="Hardened Campaign",
            status="live",
            is_active=True,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            spin_cooldown_hours=0
        )

        self.prize_win = Prize.objects.create(
            campaign=self.campaign,
            name="15% Off",
            prize_type="percentage",
            discount_percentage=Decimal("15.00"),
            probability=50.0,
            remaining_quantity=1,
            max_wins=1
        )
        self.prize_nowin = Prize.objects.create(
            campaign=self.campaign,
            name="Try Again",
            prize_type="no_win",
            probability=50.0,
            remaining_quantity=999,
            max_wins=999
        )

    def test_decimal_safe_parsers(self):
        """Verify parse_decimal_safe prevents InvalidOperation and handles corrupted input gracefully."""
        self.assertEqual(parse_decimal_safe("12.345"), Decimal("12.35"))
        self.assertEqual(parse_decimal_safe(None, default="0.00"), Decimal("0.00"))
        self.assertEqual(parse_decimal_safe("not_a_number", default="0.00"), Decimal("0.00"))
        self.assertEqual(parse_decimal_safe("", default="5.00"), Decimal("5.00"))
        self.assertEqual(parse_decimal_safe("-10.00", min_val=Decimal("0.00")), Decimal("0.00"))
        self.assertEqual(parse_decimal_safe("150.00", max_val=Decimal("100.00")), Decimal("100.00"))

    def test_numeric_safe_parsers(self):
        """Verify parse_int_safe and parse_float_safe."""
        self.assertEqual(parse_int_safe("42"), 42)
        self.assertEqual(parse_int_safe("invalid", default=10), 10)
        self.assertEqual(parse_int_safe("-5", min_val=0), 0)
        self.assertEqual(parse_float_safe("25.5"), 25.5)
        self.assertEqual(parse_float_safe("invalid", default=10.0), 10.0)

    def test_prize_probability_sum_no_invalid_operation(self):
        """Verify calculating total probability sum handles Decimal and float conversions without crash."""
        prizes = self.campaign.prizes.all()
        total_prob = sum(parse_float_safe(getattr(p, 'probability', 0.0), default=0.0) for p in prizes)
        self.assertEqual(total_prob, 100.0)

    def test_error_isolation_customer_404(self):
        """A customer visiting an invalid public token route receives a customer-isolated error page, never a business panel."""
        response = self.client.get("/s/nonexistent-token-404/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")
        # Ensure business dashboard links or controls are not exposed in context
        self.assertTrue(response.context.get("is_public_page"))
        self.assertTrue(response.context.get("is_customer_error"))
        self.assertFalse(response.context.get("is_shop_owner_error"))
        self.assertFalse(response.context.get("is_admin_error"))

    def test_error_isolation_ajax_returns_json(self):
        """AJAX request encountering 404 or error returns clean JSON, never HTML business panel."""
        response = self.client.post(
            "/s/nonexistent-token-404/spin/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("code"), 404)

    def test_unauthenticated_dashboard_access_blocked(self):
        """Unauthenticated user accessing /dashboard/shop/ must be redirected to login with no data leak."""
        response = self.client.get("/dashboard/shop/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login/"))

    def test_atomic_stock_decrement_concurrency(self):
        """When a prize has 1 remaining item, subsequent spins must not allow negative stock."""
        # 1st spin
        res1 = execute_authoritative_spin(
            shop=self.shop,
            session_key="sess_1",
            client_ip="127.0.0.1",
            user_agent="test_agent"
        )
        self.assertIn("prize", res1)

        # 2nd spin with new session
        res2 = execute_authoritative_spin(
            shop=self.shop,
            session_key="sess_2",
            client_ip="127.0.0.1",
            user_agent="test_agent"
        )
        self.assertIn("prize", res2)

        self.prize_win.refresh_from_db()
        self.assertGreaterEqual(self.prize_win.remaining_quantity, 0)

    def test_atomic_coupon_redemption_duplicate_prevention(self):
        """Redeeming a coupon twice must succeed once and raise error/conflict on second attempt."""
        spin_res = SpinResult.objects.create(
            shop=self.shop,
            campaign=self.campaign,
            prize=self.prize_win,
            session_key="test_session"
        )
        coupon = Coupon.objects.create(
            code=Coupon.generate_code(self.shop),
            spin_result=spin_res,
            shop=self.shop,
            campaign=self.campaign,
            prize=self.prize_win,
            status="active",
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        # First redemption succeeds
        redeemed = redeem_coupon_atomically(
            code=coupon.code,
            shop=self.shop,
            actor=self.owner,
            notes="First attempt"
        )
        self.assertEqual(redeemed.status, "redeemed")

        # Second redemption attempt must raise CouponRedemptionError
        with self.assertRaises(CouponRedemptionError):
            redeem_coupon_atomically(
                code=coupon.code,
                shop=self.shop,
                actor=self.owner,
                notes="Second duplicate attempt"
            )

    def test_pagination_activity_logs(self):
        """Verify activity logs are paginated properly."""
        for i in range(30):
            ActivityLog.objects.create(
                shop=self.shop,
                actor=self.owner,
                action=f"Action {i}",
                details=f"Details {i}"
            )
        self.client.login(username="shopowner_test", password="testpassword123")
        response = self.client.get(reverse("activity_logs"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("logs_page", response.context)
        self.assertEqual(len(response.context["logs_page"]), 25)
        self.assertEqual(response.context["paginator"].num_pages, 2)

    def test_redeem_barcode_scanner_page_rendered(self):
        """Verify redeem page renders the 1D barcode camera scanner container, reticle, and ZXing scripts."""
        self.client.login(username="shopowner_test", password="testpassword123")
        response = self.client.get(reverse("redeem_coupon"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="cameraStreamContainer"')
        self.assertContains(response, 'id="videoElement"')
        self.assertContains(response, 'id="torchBtn"')
        self.assertContains(response, 'scanner-laser')
        self.assertContains(response, 'scanner-box')
        self.assertContains(response, 'zxing.min.js')

    def test_redeem_barcode_leading_zeros_preserved(self):
        """Verify barcode scanner inputs preserve leading zeros and verify correctly."""
        spin_res = SpinResult.objects.create(
            shop=self.shop,
            campaign=self.campaign,
            prize=self.prize_win,
            session_key="test_session_leading_zeros"
        )
        # Create coupon with leading zero (e.g. 0123456789)
        barcode_code = "0123456789"
        Coupon.objects.create(
            code=barcode_code,
            spin_result=spin_res,
            shop=self.shop,
            campaign=self.campaign,
            prize=self.prize_win,
            status="active",
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        self.client.login(username="shopowner_test", password="testpassword123")

        # Verify through barcode scanner POST submission
        response = self.client.post(reverse("redeem_coupon"), {
            "action": "verify",
            "code": barcode_code
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, barcode_code)
        self.assertContains(response, "VALID COUPON READY")

    def test_prize_decimal_bounds_and_clean(self):
        """Verify Prize model clean() and save() enforce valid decimal bounds and rounding."""
        # 1. Percentage > 100 clamped to 100.00
        p1 = Prize.objects.create(
            campaign=self.campaign,
            name="150% Huge Promo",
            prize_type="percentage",
            discount_percentage=Decimal("150.00"),
            probability=10.0
        )
        self.assertEqual(p1.discount_percentage, Decimal("100.00"))

        # 2. Negative percentage clamped to 0.00
        p2 = Prize.objects.create(
            campaign=self.campaign,
            name="Negative Promo",
            prize_type="percentage",
            discount_percentage=Decimal("-25.00"),
            probability=10.0
        )
        self.assertEqual(p2.discount_percentage, Decimal("0.00"))

        # 3. Fixed discount typed into discount_percentage is safely transferred
        p3 = Prize.objects.create(
            campaign=self.campaign,
            name="₹500 Cash Voucher",
            prize_type="fixed",
            discount_percentage=Decimal("500.00"),
            fixed_discount_amount=Decimal("0.00"),
            probability=10.0
        )
        self.assertEqual(p3.discount_percentage, Decimal("0.00"))
        self.assertEqual(p3.fixed_discount_amount, Decimal("500.00"))

    def test_plan_decimal_bounds_and_clean(self):
        """Verify Plan model clean() and save() enforce valid price bounds."""
        from core.models import Plan
        pl = Plan.objects.create(
            code="test_unbounded_plan",
            name="Test Plan",
            price_rupees=Decimal("-50.00")
        )
        self.assertEqual(pl.price_rupees, Decimal("0.00"))

    def test_shop_dashboard_isolates_corrupt_decimal(self):
        """Verify /dashboard/shop/ does not crash with HTTP 500 when SQLite contains an incompatible Decimal record."""
        from django.db import connection
        # Insert a raw incompatible value (e.g. 1000 in a max_digits=5 column) directly via SQL
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO core_prize (campaign_id, name, prize_type, discount_percentage, fixed_discount_amount, coupon_text, probability, display_color, is_active, max_wins, remaining_quantity, design_config) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.campaign.id, "Corrupt Decimal Prize", "percentage", 1000, 0, "Test", 10.0, "#ff0000", True, 100, 100, '{}')
            )

        self.client.login(username="shopowner_test", password="testpassword123")
        response = self.client.get(reverse("shop_dashboard"))
        # Must return HTTP 200, not 500!
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Corrupt Decimal Prize")

    def test_safe_stream_handler_os_error(self):
        """Verify SafeStreamHandler swallows OSError (write error / broken pipe) cleanly."""
        import logging
        from spinplus.settings import SafeStreamHandler

        class BrokenStream:
            def write(self, msg):
                raise OSError("write error: Broken pipe")
            def flush(self):
                raise OSError("write error: Broken pipe")

        handler = SafeStreamHandler(BrokenStream())
        record = logging.LogRecord("test", logging.INFO, "path", 1, "test message", (), None)
        # Should not raise exception
        handler.emit(record)
        handler.flush()

