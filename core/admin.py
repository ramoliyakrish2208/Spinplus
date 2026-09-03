from django.contrib import admin
from core.models import User, Shop, ShopBranding, Campaign, Prize, SpinResult, Coupon, CouponRedemption, Plan, Subscription, ActivityLog, Notification, CalendarEvent, ThemeAuditLog

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'event_type', 'theme', 'priority', 'start_date', 'end_date', 'country', 'region', 'is_active')
    list_filter = ('event_type', 'is_active', 'country', 'theme')
    search_fields = ('name', 'description', 'theme', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-priority', 'start_date')


@admin.register(ThemeAuditLog)
class ThemeAuditLogAdmin(admin.ModelAdmin):
    list_display = ('shop', 'previous_theme', 'new_theme', 'reason', 'timestamp')
    list_filter = ('shop', 'timestamp')
    search_fields = ('shop__name', 'reason', 'previous_theme', 'new_theme')


admin.site.register(User)
admin.site.register(Shop)
admin.site.register(ShopBranding)
admin.site.register(Campaign)
admin.site.register(Prize)
admin.site.register(SpinResult)
admin.site.register(Coupon)
admin.site.register(CouponRedemption)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(ActivityLog)
admin.site.register(Notification)
