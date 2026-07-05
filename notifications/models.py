"""
Notification model.
Related User Stories: US-09
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notifications for report status changes."""

    TYPE_CHOICES = [
        ('status_change', 'تغییر وضعیت'),
        ('technician_assigned', 'اتصال تکنسین'),
        ('new_message', 'پیام جدید'),
        ('resolved', 'حل شدن'),
        ('part_approved', 'تایید قطعه'),
        ('part_rejected', 'رد قطعه'),
        ('rating_reminder', 'یادآوری امتیاز'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='کاربر'
    )
    report = models.ForeignKey(
        'reports.Report', on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications', verbose_name='گزارش'
    )
    type = models.CharField('نوع', max_length=30, choices=TYPE_CHOICES)
    message = models.TextField('متن اعلان')
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} - {self.get_type_display()}"
