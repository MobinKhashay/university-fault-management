"""
Auto-close resolved tickets after 72 hours with no response.
Run: python manage.py auto_close_tickets
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from reports.models import Report, RepairLog
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Auto-close resolved tickets after 72 hours and assign 5-star rating'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(
            hours=getattr(settings, 'AUTO_CLOSE_TICKET_HOURS', 72)
        )

        # Find resolved tickets older than 72 hours with no rating
        stale_tickets = Report.objects.filter(
            status='resolved',
            rating__isnull=True,
            closed_at__lt=cutoff,
        )

        closed_count = 0
        for report in stale_tickets:
            report.status = 'closed'
            report.rating = 5
            report.save()

            RepairLog.objects.create(
                report=report,
                action='auto_closed',
                description='بسته شدن خودکار پس از ۷۲ ساعت بدون واکنش گزارش‌دهنده — امتیاز ۵ ستاره ثبت شد',
            )

            Notification.objects.create(
                user=report.reporter,
                report=report,
                type='status_change',
                message=f'گزارش #{report.id} به دلیل عدم واکنش پس از ۷۲ ساعت بسته شد و امتیاز ۵ ستاره ثبت شد.',
            )

            if report.technician:
                Notification.objects.create(
                    user=report.technician.user,
                    report=report,
                    type='status_change',
                    message=f'گزارش #{report.id} خودکار بسته شد — امتیاز ۵ ستاره دریافت کردید. ✅',
                )

            closed_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'{closed_count} ticket(s) auto-closed with 5-star rating.')
        )