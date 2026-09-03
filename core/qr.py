import os
import io
import qrcode
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from core.models import QRCode

def generate_shop_qr(shop, base_url=None):
    """
    Generates a permanent high-resolution QR code for the shop pointing to /s/<public_token>/
    """
    if not base_url:
        base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    target_url = f"{base_url.rstrip('/')}/s/{shop.public_token}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    if shop.logo and os.path.exists(shop.logo.path):
        try:
            logo = Image.open(shop.logo.path).convert('RGBA')
            qr_w, qr_h = qr_img.size
            logo_max_size = int(qr_w * 0.22)
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
            
            logo_w, logo_h = logo.size
            pos_x = (qr_w - logo_w) // 2
            pos_y = (qr_h - logo_h) // 2

            box = Image.new('RGBA', (logo_w + 8, logo_h + 8), (255, 255, 255, 255))
            qr_img.paste(box, (pos_x - 4, pos_y - 4), box)
            qr_img.paste(logo, (pos_x, pos_y), logo)
        except Exception:
            pass

    buffer = io.BytesIO()
    qr_img.convert('RGB').save(buffer, format='PNG')
    file_name = f"qr_{shop.public_token}.png"

    qr_obj, created = QRCode.objects.get_or_create(
        shop=shop,
        defaults={'target_url': target_url}
    )
    qr_obj.target_url = target_url
    qr_obj.qr_image.save(file_name, ContentFile(buffer.getvalue()), save=True)
    return qr_obj

def generate_coupon_qr(coupon, base_url=None):
    """
    Generates a secure verification QR code for a coupon pointing to /verify/<verify_token>/
    """
    if not base_url:
        base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

    if not coupon.verify_token:
        coupon.save() # triggers token generation

    target_url = f"{base_url.rstrip('/')}/verify/{coupon.verify_token}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())
