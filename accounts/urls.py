"""URL patterns for accounts app."""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration (US-01)
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-code/', views.resend_verification_view, name='resend_code'),

    # Login & Logout (US-02)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard redirect
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
]
