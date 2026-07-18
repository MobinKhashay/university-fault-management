"""URL patterns for notifications app."""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='list'),
    path('mark-read/<int:notif_id>/', views.mark_read_view, name='mark_read'),
    path('mark-all-read/', views.mark_all_read_view, name='mark_all_read'),
    path('unread-count/', views.unread_count_view, name='unread_count'),
]
