# Generated manually for DecimalField SQLite repair & production hardening
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.db import migrations
import logging

logger = logging.getLogger('core')

def repair_decimal_fields(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()

    # 1. Audit & Repair core_prize table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_prize'")
    if cursor.fetchone():
        cursor.execute("SELECT id, name, prize_type, discount_percentage, fixed_discount_amount FROM core_prize")
        prizes = cursor.fetchall()
        for p_id, p_name, p_type, raw_disc, raw_fixed in prizes:
            needs_update = False
            
            # --- Sanitize discount_percentage ---
            try:
                if raw_disc is None or str(raw_disc).strip() == '':
                    dec_disc = Decimal('0.00')
                    needs_update = True
                else:
                    dec_disc = Decimal(str(raw_disc).strip())
                    if dec_disc.is_nan() or dec_disc.is_infinite():
                        dec_disc = Decimal('0.00')
                        needs_update = True
            except (InvalidOperation, TypeError, ValueError):
                dec_disc = Decimal('0.00')
                needs_update = True

            # --- Sanitize fixed_discount_amount ---
            try:
                if raw_fixed is None or str(raw_fixed).strip() == '':
                    dec_fixed = Decimal('0.00')
                    needs_update = True
                else:
                    dec_fixed = Decimal(str(raw_fixed).strip())
                    if dec_fixed.is_nan() or dec_fixed.is_infinite():
                        dec_fixed = Decimal('0.00')
                        needs_update = True
            except (InvalidOperation, TypeError, ValueError):
                dec_fixed = Decimal('0.00')
                needs_update = True

            # --- Semantic Business Logic Repairs ---
            # If prize_type is fixed and merchant entered amount into discount_percentage (e.g. 500, 1000)
            if p_type == 'fixed' and dec_fixed <= Decimal('0.00') and dec_disc > Decimal('0.00'):
                dec_fixed = min(dec_disc, Decimal('99999999.99'))
                dec_disc = Decimal('0.00')
                needs_update = True
                print(f"[Migration 0025] Repaired Prize ID={p_id} ('{p_name}'): transferred discount_percentage {raw_disc} -> fixed_discount_amount={dec_fixed}")

            # Clamp discount_percentage to [0.00, 100.00]
            if dec_disc < Decimal('0.00'):
                dec_disc = Decimal('0.00')
                needs_update = True
            elif dec_disc > Decimal('100.00'):
                print(f"[Migration 0025] Repaired Prize ID={p_id} ('{p_name}'): clamped discount_percentage from {dec_disc} to 100.00")
                dec_disc = Decimal('100.00')
                needs_update = True

            # Clamp fixed_discount_amount to [0.00, 99999999.99]
            if dec_fixed < Decimal('0.00'):
                dec_fixed = Decimal('0.00')
                needs_update = True
            elif dec_fixed > Decimal('99999999.99'):
                dec_fixed = Decimal('99999999.99')
                needs_update = True

            final_disc = dec_disc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            final_fixed = dec_fixed.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Store sanitized strings so SQLite DecimalField converter parses cleanly
            cursor.execute(
                "UPDATE core_prize SET discount_percentage = ?, fixed_discount_amount = ? WHERE id = ?",
                (str(final_disc), str(final_fixed), p_id)
            )

    # 2. Audit & Repair core_plan table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_plan'")
    if cursor.fetchone():
        cursor.execute("SELECT id, name, price_rupees FROM core_plan")
        plans = cursor.fetchall()
        for pl_id, pl_name, raw_price in plans:
            try:
                if raw_price is None or str(raw_price).strip() == '':
                    dec_price = Decimal('0.00')
                else:
                    dec_price = Decimal(str(raw_price).strip())
                    if dec_price.is_nan() or dec_price.is_infinite():
                        dec_price = Decimal('0.00')
            except (InvalidOperation, TypeError, ValueError):
                dec_price = Decimal('0.00')

            if dec_price < Decimal('0.00'):
                dec_price = Decimal('0.00')
            elif dec_price > Decimal('99999999.99'):
                dec_price = Decimal('99999999.99')

            final_price = dec_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            cursor.execute(
                "UPDATE core_plan SET price_rupees = ? WHERE id = ?",
                (str(final_price), pl_id)
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_alter_calendarevent_theme_alter_shopbranding_theme'),
    ]

    operations = [
        migrations.RunPython(repair_decimal_fields, reverse_code=migrations.RunPython.noop),
    ]
