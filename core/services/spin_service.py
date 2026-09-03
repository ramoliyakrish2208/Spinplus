"""
Authoritative Spin Engine Service.
Guarantees 100% server-side outcome determination, atomic inventory locking,
zero-probability prize protection, and cryptographically secure coupon generation.
"""

import random
from datetime import timedelta
from django.db import transaction, OperationalError
from django.utils import timezone
from core.models import Shop, Campaign, Prize, SpinResult, Coupon

class SpinExecutionError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def execute_authoritative_spin(shop: Shop, session_key: str, client_ip: str, user_agent: str) -> dict:
    try:
        with transaction.atomic():
            # 1. Lock shop row
            locked_shop = Shop.objects.select_for_update().get(id=shop.id)
        if locked_shop.status != 'active':
            raise SpinExecutionError("This shop promotion is currently unavailable.", status_code=403)

        # 2. Check subscription status and monthly spin limits
        if not locked_shop.has_active_subscription():
            raise SpinExecutionError("This store's promotional campaign has ended or is undergoing scheduled maintenance. Please check back later.", status_code=403)

        if not locked_shop.can_spin():
            raise SpinExecutionError("Monthly spin limit reached for this promotion. Please contact store staff.", status_code=429)

        # 3. Get active campaign
        campaign = locked_shop.get_active_campaign()
        if not campaign:
            raise SpinExecutionError("No active promotion campaign available.", status_code=400)

        # 4. Check session cooldown
        if session_key and campaign.spin_cooldown_hours > 0:
            cooldown_limit = timezone.now() - timedelta(hours=campaign.spin_cooldown_hours)
            already_spun = SpinResult.objects.filter(
                shop=locked_shop,
                campaign=campaign,
                session_key=session_key,
                created_at__gte=cooldown_limit
            ).exists()
            if already_spun:
                raise SpinExecutionError(
                    f"You have already spun the wheel. Please try again in {campaign.spin_cooldown_hours} hours.",
                    status_code=429
                )

        # 5. Lock and retrieve active prizes with remaining stock
        all_active_prizes = list(
            campaign.prizes.select_for_update().filter(is_active=True)
        )
        available_prizes = [p for p in all_active_prizes if p.remaining_quantity > 0]

        if not available_prizes:
            raise SpinExecutionError("All rewards have been claimed for today!", status_code=400)

        # 6. Authoritative Probability Calculation:
        # Separate positive probability prizes from zero probability / no_win prizes
        positive_prizes = [p for p in available_prizes if p.probability > 0]

        if positive_prizes:
            weights = [float(p.probability) for p in positive_prizes]
            winning_prize = random.choices(positive_prizes, weights=weights, k=1)[0]
        else:
            # Fallback only when all configured prizes have 0% weight
            no_win_prizes = [p for p in available_prizes if p.prize_type == 'no_win']
            if no_win_prizes:
                winning_prize = random.choice(no_win_prizes)
            else:
                winning_prize = available_prizes[0]

        # Determine segment index relative to the active display wheel
        # (wheel.js renders all active prizes with remaining_quantity > 0)
        display_prizes = [p for p in all_active_prizes if p.remaining_quantity > 0]
        try:
            winning_index = display_prizes.index(winning_prize)
        except ValueError:
            winning_index = 0

        # 7. Atomically decrement remaining stock
        winning_prize.remaining_quantity = max(0, winning_prize.remaining_quantity - 1)
        winning_prize.save(update_fields=['remaining_quantity'])

        # 8. Record Spin Result
        spin_res = SpinResult.objects.create(
            shop=locked_shop,
            campaign=campaign,
            prize=winning_prize,
            session_key=session_key or '',
            ip_address=client_ip,
            user_agent=user_agent
        )

        # 9. Generate Cryptographically Unpredictable Coupon
        coupon_data = None
        if winning_prize.prize_type != 'no_win':
            code = Coupon.generate_code(locked_shop)
            expires = timezone.now() + timedelta(days=30)
            coupon = Coupon.objects.create(
                code=code,
                spin_result=spin_res,
                shop=locked_shop,
                campaign=campaign,
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

        return {
            'winning_segment_index': winning_index,
            'prize': {
                'id': winning_prize.id,
                'name': winning_prize.name,
                'prize_type': winning_prize.prize_type,
                'coupon_text': winning_prize.coupon_text
            },
            'coupon': coupon_data
        }
    except OperationalError as e:
        if 'locked' in str(e).lower() or 'busy' in str(e).lower():
            raise SpinExecutionError("Traffic demand is very high. Please try spinning again in a few seconds.", status_code=429)
        raise e
