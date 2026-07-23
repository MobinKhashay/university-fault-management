"""
Management command to delete old read notifications.
Run: python manage.py cleanup_notifications
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Delete read notifications older than 30 days'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(
            days=getattr(settings, 'NOTIFICATION_AUTO_DELETE_DAYS', 30)
        )
        deleted, _ = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff,
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(f'{deleted} old notification(s) deleted.')
        )