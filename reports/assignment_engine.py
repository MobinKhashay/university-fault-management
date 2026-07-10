"""
Smart Auto-Assignment Engine.
Automatically assigns reports to the best available technician.
Related User Stories: US-22

Logic:
1. Detect required specialty from fault category
2. Find technicians with matching specialty
3. Filter by: active account + available status + within shift hours
4. Select technician with least active workload
5. If no technician available, put report in queue (pending)
"""

from django.utils import timezone
from django.conf import settings
from technicians.models import Technician
from reports.models import Report, RepairLog
from notifications.models import Notification


class AssignmentEngine:
    """
    Smart assignment engine that finds the best technician
    based on specialty, shift, availability, and workload.
    """

    def __init__(self, report):
        self.report = report
        self.required_specialty = report.category.specialty

    def assign(self):
        """
        Main assignment method.
        Returns (success: bool, message: str)
        """
        # Step 1: Find matching technicians
        candidates = self._find_candidates()

        if not candidates:
            # No technician available — put in queue
            self._enqueue()
            return False, 'تکنسین مناسبی در دسترس نیست. گزارش در صف انتظار قرار گرفت.'

        # Step 2: Select best candidate (least workload)
        best = self._select_best(candidates)

        # Step 3: Assign
        self._do_assign(best)
        return True, f'گزارش به {best.user.full_name} ارجاع شد.'

    def _find_candidates(self):
        """
        Find all eligible technicians.
        Filters: matching specialty + active + available + within shift
        """
        now = timezone.now()
        current_time = now.time()

        candidates = Technician.objects.filter(
            specialty=self.required_specialty,
            is_active=True,
            status='available',
        )

        # Filter by shift hours
        eligible = []
        for tech in candidates:
            if self._is_in_shift(tech, current_time):
                if tech.can_accept_task:
                    eligible.append(tech)

        return eligible

    def _is_in_shift(self, technician, current_time):
        """Check if technician is within their shift hours."""
        start = technician.shift_start
        end = technician.shift_end

        if start <= end:
            # Normal shift (e.g., 07:00 to 15:00)
            return start <= current_time <= end
        else:
            # Overnight shift (e.g., 22:00 to 06:00)
            return current_time >= start or current_time <= end

    def _select_best(self, candidates):
        """
        Select the technician with the least active workload.
        If tied, select the one with higher average rating.
        """
        best = None
        min_tasks = float('inf')
        best_rating = 0

        for tech in candidates:
            active = tech.active_tasks_count
            rating = tech.average_rating

            if active < min_tasks:
                best = tech
                min_tasks = active
                best_rating = rating
            elif active == min_tasks and rating > best_rating:
                best = tech
                best_rating = rating

        return best

    def _do_assign(self, technician):
        """Assign the report to the selected technician."""
        self.report.technician = technician
        self.report.status = 'assigned'
        self.report.assigned_at = timezone.now()
        self.report.save()

        # Create log entry
        RepairLog.objects.create(
            report=self.report,
            technician=technician,
            action='assigned',
            description=f'ارجاع خودکار به {technician.user.full_name} ({technician.specialty.name})',
        )

        # Notify technician
        Notification.objects.create(
            user=technician.user,
            report=self.report,
            type='technician_assigned',
            message=f'گزارش جدید #{self.report.id} — {self.report.title} به شما ارجاع شد.',
        )

        # Notify reporter
        Notification.objects.create(
            user=self.report.reporter,
            report=self.report,
            type='technician_assigned',
            message=f'تکنسین {technician.user.full_name} برای گزارش #{self.report.id} تخصیص داده شد.',
        )

    def _enqueue(self):
        """Put report in pending queue when no technician is available."""
        self.report.status = 'pending'
        self.report.save()

        RepairLog.objects.create(
            report=self.report,
            action='created',
            description='تکنسین مناسبی در دسترس نیست. گزارش در صف انتظار قرار گرفت.',
        )


def process_pending_queue():
    """
    Process all pending reports in queue.
    Called periodically (e.g., every 5 minutes via management command or cron).
    """
    pending_reports = Report.objects.filter(status='pending').order_by('created_at')

    assigned_count = 0
    for report in pending_reports:
        engine = AssignmentEngine(report)
        success, message = engine.assign()
        if success:
            assigned_count += 1

    return assigned_count
