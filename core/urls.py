from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login_view, name='home'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('health/', views.health_check_view, name='health_check'),
    
    # Public QR Landing & Spin Engine
    path('s/<str:public_token>/', views.public_shop_view, name='public_shop'),
    path('s/<str:public_token>/spin/', views.spin_wheel_api, name='spin_wheel_api'),

    # Public Shareable Coupon Page & Verification Token
    path('coupon/<str:token>/', views.public_coupon_view, name='public_coupon'),
    path('verify/<str:token>/', views.verify_coupon_token_view, name='verify_coupon_token'),

    # Global Backend Search API
    path('dashboard/search/', views.global_search_api, name='global_search_api'),

    # Shop Owner Dashboard
    path('dashboard/shop/', views.shop_dashboard, name='shop_dashboard'),
    path('dashboard/shop/profile/', views.shop_profile_view, name='shop_profile'),
    path('dashboard/shop/branding/', views.update_branding, name='update_branding'),
    path('dashboard/shop/campaigns/', views.campaign_list_view, name='campaign_list'),
    path('dashboard/shop/campaigns/<int:campaign_id>/prizes/', views.prize_manager_view, name='prize_manager'),
    path('dashboard/shop/campaigns/<int:campaign_id>/duplicate/', views.duplicate_campaign_view, name='duplicate_campaign'),
    path('dashboard/shop/campaigns/<int:campaign_id>/preview/', views.preview_campaign_view, name='preview_campaign'),
    path('dashboard/shop/campaigns/<int:campaign_id>/preview/spin/', views.preview_spin_api, name='preview_spin_api'),
    path('dashboard/shop/logs/', views.activity_logs_view, name='activity_logs'),
    path('dashboard/shop/coupons/redeem/', views.redeem_coupon_view, name='redeem_coupon'),
    path('dashboard/shop/export/coupons/', views.export_coupons_csv, name='export_coupons_csv'),
    path('dashboard/shop/qr/download/', views.download_qr_view, name='download_qr'),
    path('dashboard/shop/qr/poster/', views.qr_poster_view, name='qr_poster'),

    # Subscriptions & Operations
    path('dashboard/onboarding/', views.onboarding_view, name='onboarding'),
    path('dashboard/subscription/', views.billing_view, name='subscription'),
    path('dashboard/subscription/renew/', views.subscription_renew_view, name='subscription_renew'),
    path('dashboard/subscription/request/', views.request_plan_view, name='request_plan'),
    path('dashboard/billing/', views.billing_view, name='billing'),
    path('dashboard/account/', views.account_settings_view, name='account_settings'),
    path('dashboard/notifications/', views.notifications_view, name='notifications'),
    path('dashboard/notifications/<int:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),

    # Super Admin Dashboard & Subscriptions Management Center
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/capacity/', views.admin_capacity_dashboard_view, name='admin_capacity_dashboard'),
    path('dashboard/admin/subscriptions/', views.admin_subscriptions_view, name='admin_subscriptions'),
    path('dashboard/admin/plan-requests/', views.admin_plan_requests_view, name='admin_plan_requests'),
    path('dashboard/admin/plan-requests/<int:request_id>/action/', views.admin_plan_request_action_view, name='admin_plan_request_action'),
    path('dashboard/admin/plans/save/', views.admin_plan_save_view, name='admin_plan_save'),
    path('dashboard/admin/plans/<int:plan_id>/delete/', views.admin_plan_delete_view, name='admin_plan_delete'),
    path('dashboard/admin/subscriptions/assign/', views.admin_subscription_assign_view, name='admin_subscription_assign'),
    path('dashboard/admin/subscriptions/<int:sub_id>/status/', views.admin_subscription_status_view, name='admin_subscription_status'),

    # Error Preview Routes (For Live Verification in Development & Production)
    path('errors/404/', views.custom_404_view, name='error_404_preview'),
    path('errors/500/', views.custom_500_view, name='error_500_preview'),
    path('errors/403/', views.custom_403_view, name='error_403_preview'),
    path('errors/400/', views.custom_400_view, name='error_400_preview'),
]