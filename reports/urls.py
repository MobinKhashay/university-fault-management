"""URL patterns for reports app."""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('submit/', views.submit_report_view, name='submit_report'),
    path('my-reports/', views.my_reports_view, name='my_reports'),

    # AJAX endpoints
    path('ajax/buildings/', views.ajax_get_buildings, name='ajax_buildings'),
    path('ajax/locations/', views.ajax_get_locations, name='ajax_locations'),
    path('ajax/check-duplicate/', views.ajax_check_duplicate, name='ajax_check_duplicate'),
]
