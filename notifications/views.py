"""
Notification views.
Related User Stories: US-09
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import Notification


@login_required
def notifications_view(request):
    """
    Notifications page with read/unread filter tabs.
    US-09: اعلان‌ها با فیلتر خوانده/نخوانده
    """
    tab = request.GET.get('tab', 'all')
    notifications = Notification.objects.filter(user=request.user)

    if tab == 'unread':
        notifications = notifications.filter(is_read=False)
    elif tab == 'read':
        notifications = notifications.filter(is_read=True)

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'notifications': notifications[:50],
        'current_tab': tab,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required
def mark_read_view(request, notif_id):
    """Mark a single notification as read (AJAX)."""
    if request.method == 'POST':
        try:
            notif = Notification.objects.get(id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})


@login_required
def mark_all_read_view(request):
    """Mark all notifications as read (AJAX)."""
    if request.method == 'POST':
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return JsonResponse({'success': True, 'count': count})
    return JsonResponse({'success': False})


@login_required
def unread_count_view(request):
    """Return unread notification count (AJAX — for navbar badge)."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
