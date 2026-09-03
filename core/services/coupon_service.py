"""
Enterprise Coupon Verification & Redemption Service.
Guarantees atomic single-use redemption, strict multi-tenant ownership checks,
and race condition immunity.
"""

from django.db import transaction
from django.utils import timezone
from core.models import Coupon, CouponRedemption, ActivityLog, User, Shop

class CouponRedemptionError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def redeem_coupon_atomically(code: str, shop: Shop, actor: User, notes: str = "") -> Coupon:
    """
    Atomically verifies and marks a coupon as redeemed for a specific shop.
    Guarantees no double redemption under concurrent requests.
    """
    clean_code = (code or '').strip().upper()
    if not clean_code:
        raise CouponRedemptionError("Please enter a valid coupon code.", status_code=400)

    with transaction.atomic():
        try:
            coupon = Coupon.objects.select_for_update().get(code=clean_code, shop=shop)
        except Coupon.DoesNotExist:
            other_shop_coupon = Coupon.objects.filter(code=clean_code).select_related('shop').first()
            if other_shop_coupon:
                raise CouponRedemptionError(
                    f"SECURITY REJECTION: Coupon '{clean_code}' belongs to store '{other_shop_coupon.shop.name}' and CANNOT be redeemed at '{shop.name}'.",
                    status_code=403
                )
            raise CouponRedemptionError(f"Invalid coupon code '{clean_code}' for {shop.name}.", status_code=404)

        if coupon.status == 'redeemed':
            raise CouponRedemptionError(f"Coupon '{clean_code}' was ALREADY REDEEMED.", status_code=409)

        if coupon.status == 'expired' or (coupon.expires_at and coupon.expires_at < timezone.now()):
            raise CouponRedemptionError(f"Coupon '{clean_code}' HAS EXPIRED.", status_code=410)

        if coupon.status == 'cancelled':
            raise CouponRedemptionError(f"Coupon '{clean_code}' has been cancelled.", status_code=400)

        if coupon.status != 'active':
            raise CouponRedemptionError(f"Cannot redeem: coupon status is '{coupon.status}'.", status_code=400)

        # Mark redeemed
        coupon.status = 'redeemed'
        coupon.save(update_fields=['status'])

        CouponRedemption.objects.create(
            coupon=coupon,
            redeemed_by=actor if getattr(actor, 'is_authenticated', False) else None,
            notes=notes
        )

        ActivityLog.objects.create(
            shop=shop,
            actor=actor if getattr(actor, 'is_authenticated', False) else None,
            action="Coupon Redeemed",
            details=f"Code {coupon.code} ({coupon.prize.name}) redeemed"
        )

        return coupon
