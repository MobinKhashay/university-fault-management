"""URL patterns for technicians app."""

from django.urls import path
from . import views

app_name = 'technicians'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('toggle-status/', views.toggle_status_view, name='toggle_status'),
    path('task/<int:report_id>/', views.task_detail_view, name='task_detail'),
    path('task/<int:report_id>/start/', views.start_task_view, name='start_task'),
    path('task/<int:report_id>/heading/', views.heading_to_location_view, name='heading'),
    path('task/<int:report_id>/arrived/', views.confirm_arrival_view, name='confirm_arrival'),
    path('task/<int:report_id>/complete/', views.complete_task_view, name='complete_task'),
    path('task/<int:report_id>/suspend/', views.suspend_task_view, name='suspend_task'),
    path('task/<int:report_id>/request-part/', views.request_part_view, name='request_part'),
    path('history/', views.work_history_view, name='work_history'),
]
