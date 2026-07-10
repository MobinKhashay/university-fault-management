"""
Management command to process pending report queue.
Run periodically: python manage.py process_queue

Related User Stories: US-22
"""

from django.core.management.base import BaseCommand
from reports.assignment_engine import process_pending_queue


class Command(BaseCommand):
    help = 'Process pending reports queue and auto-assign to available technicians'

    def handle(self, *args, **options):
        count = process_pending_queue()
        self.stdout.write(
            self.style.SUCCESS(f'{count} report(s) assigned from queue.')
        )
