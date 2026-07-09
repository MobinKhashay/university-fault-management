"""URL patterns for accounts app."""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-code/', views.resend_verification_view, name='resend_code'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
]
