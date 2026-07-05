"""
Report/Ticket models and related entities.
Related User Stories: US-05, US-06, US-07, US-08
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Faculty(models.Model):
    """University faculty/college."""

    name = models.CharField('نام دانشکده', max_length=200)

    class Meta:
        verbose_name = 'دانشکده'
        verbose_name_plural = 'دانشکده‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Building(models.Model):
    """Buildings within a faculty."""

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField('نام ساختمان', max_length=200)

    class Meta:
        verbose_name = 'ساختمان'
        verbose_name_plural = 'ساختمان‌ها'
        ordering = ['faculty', 'name']

    def __str__(self):
        return f"{self.faculty.name} - {self.name}"


class Location(models.Model):
    """Specific location (floor + room) within a building."""

    LOCATION_TYPE_CHOICES = [
        ('faculty', 'دانشکده'),
        ('dormitory', 'خوابگاه'),
        ('cafeteria', 'سلف'),
        ('library', 'کتابخانه'),
        ('gym', 'ورزشگاه'),
        ('other', 'سایر'),
    ]

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='locations')
    floor = models.CharField('طبقه', max_length=50, blank=True)
    room = models.CharField('اتاق', max_length=50, blank=True)
    location_type = models.CharField('نوع مکان', max_length=20, choices=LOCATION_TYPE_CHOICES, default='faculty')

    class Meta:
        verbose_name = 'مکان'
        verbose_name_plural = 'مکان‌ها'
        ordering = ['building', 'floor', 'room']

    def __str__(self):
        parts = [str(self.building)]
        if self.floor:
            parts.append(f"طبقه {self.floor}")
        if self.room:
            parts.append(f"اتاق {self.room}")
        return ' - '.join(parts)


class Specialty(models.Model):
    """Technician specialties (electrical, plumbing, IT, etc.)."""

    name = models.CharField('نام تخصص', max_length=100)

    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'تخصص‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class FaultCategory(models.Model):
    """Categories of faults, linked to specialties for auto-assignment."""

    name = models.CharField('نام دسته‌بندی', max_length=100)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name = 'دسته‌بندی خرابی'
        verbose_name_plural = 'دسته‌بندی‌های خرابی'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.specialty.name})"


class Report(models.Model):
    """
    Main report/ticket model.
    Core entity of the system.
    """

    PRIORITY_CHOICES = [
        ('normal', 'عادی'),
        ('important', 'مهم'),
        ('urgent', 'اضطراری'),
    ]

    STATUS_CHOICES = [
        ('pending', 'در صف انتظار'),
        ('assigned', 'ارجاع شده'),
        ('in_progress', 'در حال تعمیر'),
        ('suspended', 'معلق'),
        ('resolved', 'حل شده'),
        ('closed', 'بسته شده'),
        ('cancelled', 'لغو شده'),
        ('archived', 'بایگانی'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='submitted_reports', verbose_name='گزارش‌دهنده'
    )
    technician = models.ForeignKey(
        'technicians.Technician', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_reports', verbose_name='تکنسین'
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='مکان')
    category = models.ForeignKey(FaultCategory, on_delete=models.CASCADE, verbose_name='دسته‌بندی')

    title = models.CharField('عنوان خرابی', max_length=200)
    description = models.TextField('توضیحات', blank=True)
    audio_file = models.FileField('فایل صوتی', upload_to='reports/audio/', blank=True, null=True)
    priority = models.CharField('اولویت', max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    eta_hours = models.FloatField('زمان تخمینی (ساعت)', null=True, blank=True)
    rating = models.PositiveSmallIntegerField('امتیاز رضایت', null=True, blank=True)
    objection_text = models.TextField('متن اعتراض', blank=True)
    suspension_reason = models.CharField('دلیل تعلیق', max_length=200, blank=True)
    cancellation_reason = models.TextField('دلیل لغو', blank=True)

    created_at = models.DateTimeField('تاریخ ثبت', default=timezone.now)
    assigned_at = models.DateTimeField('تاریخ ارجاع', null=True, blank=True)
    closed_at = models.DateTimeField('تاریخ بسته شدن', null=True, blank=True)

    class Meta:
        verbose_name = 'گزارش'
        verbose_name_plural = 'گزارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

    @property
    def is_open(self):
        return self.status not in ('closed', 'cancelled', 'archived')

    @property
    def duration_open(self):
        """Returns how long the ticket has been open."""
        end = self.closed_at or timezone.now()
        return end - self.created_at


class ReportMedia(models.Model):
    """Images and videos attached to a report."""

    FILE_TYPE_CHOICES = [
        ('image', 'تصویر'),
        ('video', 'ویدیو'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='media')
    file_path = models.FileField('فایل', upload_to='reports/images/')
    file_type = models.CharField('نوع فایل', max_length=10, choices=FILE_TYPE_CHOICES, default='image')
    is_after = models.BooleanField('عکس بعد از تعمیر', default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'رسانه گزارش'
        verbose_name_plural = 'رسانه‌های گزارش'

    def __str__(self):
        return f"Media for Report #{self.report.id}"


class RepairLog(models.Model):
    """Timeline/log entries for each report."""

    ACTION_CHOICES = [
        ('created', 'ثبت گزارش'),
        ('assigned', 'ارجاع به تکنسین'),
        ('heading', 'در حال رفتن به محل'),
        ('arrived', 'حضور در محل'),
        ('started', 'شروع تعمیر'),
        ('suspended', 'تعلیق'),
        ('resumed', 'ازسرگیری'),
        ('completed', 'اتمام تعمیر'),
        ('rated', 'امتیازدهی'),
        ('closed', 'بسته شدن'),
        ('cancelled', 'لغو'),
        ('reassigned', 'ارجاع مجدد'),
        ('priority_changed', 'تغییر اولویت'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='logs')
    technician = models.ForeignKey(
        'technicians.Technician', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='repair_logs'
    )
    action = models.CharField('عملیات', max_length=30, choices=ACTION_CHOICES)
    description = models.TextField('توضیحات', blank=True)
    created_at = models.DateTimeField('زمان', default=timezone.now)

    class Meta:
        verbose_name = 'لاگ تعمیر'
        verbose_name_plural = 'لاگ‌های تعمیر'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_action_display()} - Report #{self.report.id}"


class TicketMessage(models.Model):
    """Messages between reporter and technician within a ticket."""

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField('پیام')
    attachment = models.FileField('پیوست', upload_to='reports/messages/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام‌های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f"Message in Report #{self.report.id} by {self.sender}"


class PartRequest(models.Model):
    """Part/material requests from technicians."""

    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='part_requests')
    technician = models.ForeignKey(
        'technicians.Technician', on_delete=models.CASCADE, related_name='part_requests'
    )
    part_name = models.CharField('نام قطعه', max_length=200)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست قطعه'
        verbose_name_plural = 'درخواست‌های قطعه'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.part_name} for Report #{self.report.id}"
