import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Shop, Campaign, Prize
from core.views import sanitize_segment_design_config


class SegmentDesignSanitizationTests(TestCase):
    def test_empty_and_invalid_inputs(self):
        self.assertEqual(sanitize_segment_design_config(None), {})
        self.assertEqual(sanitize_segment_design_config(""), {})
        self.assertEqual(sanitize_segment_design_config("invalid-json"), {})
        self.assertEqual(sanitize_segment_design_config([]), {})
        self.assertEqual(sanitize_segment_design_config(123), {})

    def test_font_family_validation(self):
        # Valid fonts
        res = sanitize_segment_design_config({'font_family': 'poppins'})
        self.assertEqual(res['font_family'], 'poppins')

        res = sanitize_segment_design_config({'font_family': 'Cinzel'})
        self.assertEqual(res['font_family'], 'cinzel')

        res = sanitize_segment_design_config({'font_family': 'Plus Jakarta Sans'})
        self.assertEqual(res['font_family'], 'plus_jakarta_sans')

        # Disallowed font should not be stored
        res = sanitize_segment_design_config({'font_family': 'comic_sans_ms'})
        self.assertNotIn('font_family', res)

    def test_typography_and_bounds(self):
        raw = {
            'font_weight': '800',
            'font_size': '24',
            'text_align': 'center',
            'text_transform': 'uppercase',
            'letter_spacing': '2.5',
            'font_style': 'italic',
            'line_height': '1.3'
        }
        res = sanitize_segment_design_config(raw)
        self.assertEqual(res['font_weight'], 800)
        self.assertEqual(res['font_size'], 24)
        self.assertEqual(res['text_align'], 'center')
        self.assertEqual(res['text_transform'], 'uppercase')
        self.assertEqual(res['letter_spacing'], 2.5)
        self.assertEqual(res['font_style'], 'italic')
        self.assertEqual(res['line_height'], 1.3)

        # Clamping out-of-range bounds
        raw_clamped = {
            'font_size': '999',
            'letter_spacing': '100.0',
            'line_height': '99.0'
        }
        res_clamped = sanitize_segment_design_config(raw_clamped)
        self.assertNotIn('font_size', res_clamped)  # > 36 is dropped
        self.assertEqual(res_clamped['letter_spacing'], 10.0)  # clamped to max 10.0
        self.assertEqual(res_clamped['line_height'], 2.5)  # clamped to max 2.5

    def test_text_appearance_and_shadow_stroke(self):
        raw = {
            'text_color': '#ff00aa',
            'text_opacity': '85',
            'text_shadow_enabled': True,
            'text_shadow_color': '#112233',
            'text_shadow_blur': '8',
            'text_shadow_x': '3',
            'text_shadow_y': '4',
            'text_stroke_enabled': True,
            'text_stroke_color': '#000000',
            'text_stroke_width': '3'
        }
        res = sanitize_segment_design_config(raw)
        self.assertEqual(res['text_color'], '#ff00aa')
        self.assertEqual(res['text_opacity'], 85)
        self.assertTrue(res['text_shadow_enabled'])
        self.assertEqual(res['text_shadow_color'], '#112233')
        self.assertEqual(res['text_shadow_blur'], 8)
        self.assertEqual(res['text_shadow_x'], 3)
        self.assertEqual(res['text_shadow_y'], 4)
        self.assertTrue(res['text_stroke_enabled'])
        self.assertEqual(res['text_stroke_color'], '#000000')
        self.assertEqual(res['text_stroke_width'], 3)

    def test_gradient_and_pattern_background(self):
        raw = {
            'bg_type': 'gradient',
            'bg_color_1': '#6366f1',
            'bg_color_2': '#a855f7',
            'bg_color_3': '#ec4899',
            'gradient_type': 'radial',
            'gradient_angle': '135',
            'bg_pattern': 'stars',
            'highlight_enabled': True
        }
        res = sanitize_segment_design_config(raw)
        self.assertEqual(res['bg_type'], 'gradient')
        self.assertEqual(res['bg_color_1'], '#6366f1')
        self.assertEqual(res['bg_color_2'], '#a855f7')
        self.assertEqual(res['bg_color_3'], '#ec4899')
        self.assertEqual(res['gradient_type'], 'radial')
        self.assertEqual(res['gradient_angle'], 135)
        self.assertEqual(res['bg_pattern'], 'stars')
        self.assertTrue(res['highlight_enabled'])

    def test_icon_and_decorations(self):
        raw = {
            'icon_type': 'preset',
            'icon_name': 'gift',
            'icon_position': 'above',
            'icon_size': '20',
            'icon_spacing': '8'
        }
        res = sanitize_segment_design_config(raw)
        self.assertEqual(res['icon_type'], 'preset')
        self.assertEqual(res['icon_name'], 'gift')
        self.assertEqual(res['icon_position'], 'above')
        self.assertEqual(res['icon_size'], 20)
        self.assertEqual(res['icon_spacing'], 8)

        # Invalid icon is ignored
        raw_bad = {'icon_type': 'preset', 'icon_name': 'unauthorized_symbol'}
        res_bad = sanitize_segment_design_config(raw_bad)
        self.assertNotIn('icon_name', res_bad)

    def test_border_and_glow(self):
        raw = {
            'border_enabled': True,
            'border_color': '#ffd700',
            'border_width': '4',
            'border_style': 'dashed',
            'glow_enabled': True,
            'glow_color': '#f59e0b',
            'glow_intensity': '7'
        }
        res = sanitize_segment_design_config(raw)
        self.assertTrue(res['border_enabled'])
        self.assertEqual(res['border_color'], '#ffd700')
        self.assertEqual(res['border_width'], 4)
        self.assertEqual(res['border_style'], 'dashed')
        self.assertTrue(res['glow_enabled'])
        self.assertEqual(res['glow_color'], '#f59e0b')
        self.assertEqual(res['glow_intensity'], 7)


class SegmentDesignViewIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="design_shopowner",
            password="testpassword123",
            role="shop_owner"
        )
        self.shop = Shop.objects.create(
            name="Design Boutique",
            owner=self.user,
            public_token="design-token-abc"
        )
        self.user.shop = self.shop
        self.user.save()

        from django.utils import timezone
        sub = self.shop.get_subscription()
        sub.status = 'active'
        sub.expires_at = timezone.now() + timezone.timedelta(days=365)
        sub.save()

        self.campaign = Campaign.objects.create(
            shop=self.shop,
            name="Mega Diwali Wheel",
            status="live",
            is_active=True,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )

    def test_add_prize_with_segment_design_config(self):
        self.client.login(username="design_shopowner", password="testpassword123")
        design_payload = {
            'font_family': 'cinzel',
            'font_weight': 800,
            'font_size': 16,
            'bg_type': 'gradient',
            'bg_color_1': '#581c87',
            'bg_color_2': '#d4af37',
            'icon_type': 'preset',
            'icon_name': 'crown',
            'border_enabled': True,
            'border_color': '#ffd700'
        }

        response = self.client.post(
            reverse('prize_manager', kwargs={'campaign_id': self.campaign.id}),
            {
                'action': 'add_prize',
                'name': 'Golden Grand Prize',
                'prize_type': 'percentage',
                'discount_percentage': '30.0',
                'probability': '15.0',
                'display_color': '#581c87',
                'coupon_text': 'Valid on fine jewellery',
                'remaining_quantity': '100',
                'design_config': json.dumps(design_payload)
            }
        )
        self.assertEqual(response.status_code, 302)

        prize = Prize.objects.filter(campaign=self.campaign, name='Golden Grand Prize').first()
        self.assertIsNotNone(prize)
        self.assertEqual(prize.design_config.get('font_family'), 'cinzel')
        self.assertEqual(prize.design_config.get('font_weight'), 800)
        self.assertEqual(prize.design_config.get('icon_name'), 'crown')
        self.assertEqual(prize.design_config.get('border_color'), '#ffd700')

    def test_edit_prize_updates_segment_design(self):
        self.client.login(username="design_shopowner", password="testpassword123")
        prize = Prize.objects.create(
            campaign=self.campaign,
            name="Original Prize",
            prize_type="fixed",
            fixed_discount_amount=Decimal('100.00'),
            probability=20.0,
            display_color="#6366f1",
            remaining_quantity=50,
            design_config={'font_family': 'inter'}
        )

        updated_design = {
            'font_family': 'poppins',
            'font_weight': 900,
            'bg_type': 'pattern',
            'bg_pattern': 'chevrons',
            'glow_enabled': True,
            'glow_color': '#10b981'
        }

        response = self.client.post(
            reverse('prize_manager', kwargs={'campaign_id': self.campaign.id}),
            {
                'action': 'edit_prize',
                'prize_id': prize.id,
                'name': 'Updated Luxury Prize',
                'prize_type': 'fixed',
                'fixed_discount_amount': '150.00',
                'probability': '25.0',
                'display_color': '#10b981',
                'coupon_text': 'VIP coupon',
                'remaining_quantity': '75',
                'design_config': json.dumps(updated_design)
            }
        )
        self.assertEqual(response.status_code, 302)

        prize.refresh_from_db()
        self.assertEqual(prize.name, 'Updated Luxury Prize')
        self.assertEqual(prize.fixed_discount_amount, Decimal('150.00'))
        self.assertEqual(prize.design_config.get('font_family'), 'poppins')
        self.assertEqual(prize.design_config.get('bg_pattern'), 'chevrons')
        self.assertTrue(prize.design_config.get('glow_enabled'))

    def test_prize_manager_page_renders_design_config_in_json(self):
        Prize.objects.create(
            campaign=self.campaign,
            name="Diamond Prize",
            prize_type="percentage",
            discount_percentage=Decimal('50.00'),
            probability=10.0,
            display_color="#4f46e5",
            remaining_quantity=10,
            design_config={'font_family': 'outfit', 'icon_name': 'diamond'}
        )

        self.client.login(username="design_shopowner", password="testpassword123")
        response = self.client.get(reverse('prize_manager', kwargs={'campaign_id': self.campaign.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'outfit')
        self.assertContains(response, 'diamond')
        self.assertContains(response, 'LIVE CANVAS PREVIEW')

    def test_customer_spin_landing_receives_design_config(self):
        Prize.objects.create(
            campaign=self.campaign,
            name="Holiday Free Gift",
            prize_type="freebie",
            probability=50.0,
            display_color="#f59e0b",
            remaining_quantity=20,
            design_config={'font_family': 'bebas_neue', 'highlight_enabled': True}
        )

        response = self.client.get(reverse('public_shop', kwargs={'public_token': self.shop.public_token}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bebas_neue')
        self.assertContains(response, 'highlight_enabled')

    def test_edit_button_has_data_attributes_and_modal_trigger(self):
        prize = Prize.objects.create(
            campaign=self.campaign,
            name='Test "Special" Prize',
            prize_type='percentage',
            discount_percentage=Decimal('15.00'),
            probability=20.0,
            display_color='#d4af37',
            remaining_quantity=50
        )
        self.client.login(username="design_shopowner", password="testpassword123")
        response = self.client.get(reverse('prize_manager', kwargs={'campaign_id': self.campaign.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="btn-ghost edit-prize-btn"')
        self.assertContains(response, f'data-prize-id="{prize.id}"')
        self.assertContains(response, 'onclick="openEditPrizeModal(this)"')

    def test_update_wheel_center_customization(self):
        self.client.login(username="design_shopowner", password="testpassword123")
        response = self.client.post(
            reverse('prize_manager', kwargs={'campaign_id': self.campaign.id}),
            {
                'action': 'update_wheel_center',
                'hub_mode': 'icon',
                'hub_icon': 'diamond',
                'icon_color': '#38bdf8',
                'rim_color': '#ffd700',
                'bg_color': '#0f172a'
            }
        )
        self.assertEqual(response.status_code, 302)

        self.campaign.refresh_from_db()
        hub_cfg = self.campaign.get_center_hub_config()
        self.assertEqual(hub_cfg['mode'], 'icon')
        self.assertEqual(hub_cfg['icon'], 'diamond')
        self.assertEqual(hub_cfg['iconColor'], '#38bdf8')
        self.assertEqual(hub_cfg['rimColor'], '#ffd700')
        self.assertEqual(hub_cfg['bgColor'], '#0f172a')
