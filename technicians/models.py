"""
Technician model.
Related User Stories: US-11, US-12, US-13, US-14, US-15
"""

from django.db import models
from django.conf import settings


class Technician(models.Model):
    """Technician profile linked to a User account."""

    STATUS_CHOICES = [
        ('available', 'آماده به کار'),
        ('busy', 'مشغول'),
        ('off_shift', 'پایان شیفت'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='technician_profile', verbose_name='کاربر'
    )
    specialty = models.ForeignKey(
        'reports.Specialty', on_delete=models.CASCADE,
        related_name='technicians', verbose_name='تخصص'
    )
    personnel_code = models.CharField('کد پرسنلی', max_length=20, unique=True)
    shift_start = models.TimeField('شروع شیفت')
    shift_end = models.TimeField('پایان شیفت')
    status = models.CharField('وضعیت حضور', max_length=20, choices=STATUS_CHOICES, default='off_shift')
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'تکنسین'
        verbose_name_plural = 'تکنسین‌ها'
        ordering = ['user__last_name']

    def __str__(self):
        return f"{self.user.full_name} ({self.specialty.name})"

    @property
    def active_tasks_count(self):
        """Returns number of currently active tasks."""
        return self.assigned_reports.filter(
            status__in=['assigned', 'in_progress']
        ).count()

    @property
    def can_accept_task(self):
        """Check if technician can accept new tasks (max 3)."""
        return (
            self.is_active
            and self.status == 'available'
            and self.active_tasks_count < settings.MAX_ACTIVE_TASKS_PER_TECHNICIAN
        )

    @property
    def total_completed(self):
        """Total completed tasks."""
        return self.assigned_reports.filter(status__in=['closed', 'archived']).count()

    @property
    def average_rating(self):
        """Average satisfaction rating from reporters."""
        from django.db.models import Avg
        result = self.assigned_reports.filter(
            rating__isnull=False
        ).aggregate(avg=Avg('rating'))
        return result['avg'] or 0
