"""URL patterns for accounts app."""

from django.urls import path
from . import views
from .profile_views import profile_view

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-code/', views.resend_verification_view, name='resend_code'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify_view, name='password_reset_verify'),
    path('password-reset/resend/', views.password_reset_resend_view, name='password_reset_resend'),
    path('password-reset/new/', views.password_reset_new_view, name='password_reset_new'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard'),
]