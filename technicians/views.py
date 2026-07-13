"""
Technician panel views: Dashboard, Tasks, Report Details.
Related User Stories: US-11, US-12, US-13, US-14, US-15
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.conf import settings
from .models import Technician
from reports.models import Report, RepairLog, ReportMedia, PartRequest
from notifications.models import Notification


def technician_required(view_func):
    """Decorator to restrict access to technician users only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_technician:
            messages.error(request, 'شما دسترسی به پنل تکنسین ندارید.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@technician_required
def dashboard_view(request):
    """
    Technician dashboard with profile card, status toggle, stats, and task tabs.
    US-11: داشبورد تکنسین با کارت پروفایل، وضعیت حضور، آمار
    """
    tech = request.user.technician_profile
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Task counts
    new_tasks = Report.objects.filter(technician=tech, status='assigned').count()
    in_progress_tasks = Report.objects.filter(technician=tech, status='in_progress').count()
    suspended_tasks = Report.objects.filter(technician=tech, status='suspended').count()

    # Today stats
    today_completed = Report.objects.filter(
        technician=tech, closed_at__gte=today_start
    ).count()

    # Overall stats
    total_completed = tech.total_completed
    avg_rating = round(tech.average_rating, 1)

    # Task lists for tabs
    new_task_list = Report.objects.filter(
        technician=tech, status='assigned'
    ).select_related('location__building__faculty', 'category').order_by('-created_at')

    in_progress_list = Report.objects.filter(
        technician=tech, status='in_progress'
    ).select_related('location__building__faculty', 'category').order_by('-created_at')

    suspended_list = Report.objects.filter(
        technician=tech, status='suspended'
    ).select_related('location__building__faculty', 'category').order_by('-created_at')

    # Unread notifications
    unread_notifs = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'tech': tech,
        'new_tasks': new_tasks,
        'in_progress_tasks': in_progress_tasks,
        'suspended_tasks': suspended_tasks,
        'today_completed': today_completed,
        'total_completed': total_completed,
        'avg_rating': avg_rating,
        'new_task_list': new_task_list,
        'in_progress_list': in_progress_list,
        'suspended_list': suspended_list,
        'unread_notifs': unread_notifs,
    }
    return render(request, 'technicians/dashboard.html', context)


@technician_required
def toggle_status_view(request):
    """
    Toggle technician availability status via AJAX.
    US-11: سوییچ وضعیت حضور (آماده/مشغول/پایان شیفت)
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        new_status = request.POST.get('status', '')

        if new_status in ['available', 'busy', 'off_shift']:
            tech.status = new_status
            tech.save()

            status_labels = dict(Technician.STATUS_CHOICES)
            return JsonResponse({
                'success': True,
                'status': new_status,
                'label': status_labels.get(new_status, ''),
            })

    return JsonResponse({'success': False})


@technician_required
def task_detail_view(request, report_id):
    """
    Task detail view for technician with action buttons.
    US-13: جزئیات گزارش خرابی + ثبت تعمیر
    """
    tech = request.user.technician_profile
    report = get_object_or_404(Report, id=report_id, technician=tech)

    logs = report.logs.all().order_by('created_at')
    media = report.media.filter(is_after=False)
    after_media = report.media.filter(is_after=True)
    ticket_messages = report.messages.all().order_by('created_at')
    part_requests = report.part_requests.all()

    context = {
        'report': report,
        'logs': logs,
        'media': media,
        'after_media': after_media,
        'messages_list': ticket_messages,
        'part_requests': part_requests,
    }
    return render(request, 'technicians/task_detail.html', context)


@technician_required
def start_task_view(request, report_id):
    """
    Technician starts working on a task — select ETA.
    US-13: دکمه شروع کار + انتخاب ETA
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        # Check max active tasks
        if tech.active_tasks_count >= settings.MAX_ACTIVE_TASKS_PER_TECHNICIAN:
            messages.error(request, f'شما حداکثر {settings.MAX_ACTIVE_TASKS_PER_TECHNICIAN} تسک فعال همزمان می‌توانید داشته باشید.')
            return redirect('technicians:task_detail', report_id=report_id)

        eta = request.POST.get('eta', '')
        try:
            report.eta_hours = float(eta)
        except (ValueError, TypeError):
            report.eta_hours = 2.0

        report.status = 'in_progress'
        report.save()

        RepairLog.objects.create(
            report=report, technician=tech,
            action='started',
            description=f'شروع کار توسط {tech.user.full_name} — ETA: {report.eta_hours} ساعت',
        )

        # Notify reporter
        Notification.objects.create(
            user=report.reporter, report=report,
            type='status_change',
            message=f'تکنسین {tech.user.full_name} کار روی گزارش #{report.id} را شروع کرد.',
        )

        messages.success(request, 'کار شروع شد.')
    return redirect('technicians:task_detail', report_id=report_id)


@technician_required
def heading_to_location_view(request, report_id):
    """
    Technician heading to location.
    US-13: دکمه «در حال رفتن به محل»
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        RepairLog.objects.create(
            report=report, technician=tech,
            action='heading',
            description=f'{tech.user.full_name} در حال رفتن به محل',
        )
        messages.success(request, 'وضعیت ثبت شد: در حال رفتن به محل')
    return redirect('technicians:task_detail', report_id=report_id)


@technician_required
def confirm_arrival_view(request, report_id):
    """
    Technician confirms physical arrival.
    US-13: تایید حضور فیزیکی در محل
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        RepairLog.objects.create(
            report=report, technician=tech,
            action='arrived',
            description=f'{tech.user.full_name} در محل حاضر شد',
        )
        messages.success(request, 'حضور در محل تایید شد.')
    return redirect('technicians:task_detail', report_id=report_id)


@technician_required
def complete_task_view(request, report_id):
    """
    Technician completes a task (requires description + optional photo).
    US-13: اتمام کار مشروط به عکس یا توضیح
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        description = request.POST.get('description', '')
        if not description:
            messages.error(request, 'لطفاً توضیح تعمیر را وارد کنید.')
            return redirect('technicians:task_detail', report_id=report_id)

        # Handle after-repair photo
        photo = request.FILES.get('after_photo')
        if photo:
            ReportMedia.objects.create(
                report=report, file_path=photo,
                file_type='image', is_after=True,
            )

        report.status = 'resolved'
        report.closed_at = timezone.now()
        report.save()

        RepairLog.objects.create(
            report=report, technician=tech,
            action='completed',
            description=f'تعمیر انجام شد: {description}',
        )

        # Notify reporter
        Notification.objects.create(
            user=report.reporter, report=report,
            type='resolved',
            message=f'گزارش #{report.id} توسط {tech.user.full_name} تعمیر شد. لطفاً امتیاز رضایت خود را ثبت کنید.',
        )

        messages.success(request, 'تعمیر با موفقیت ثبت شد.')
    return redirect('technicians:dashboard')


@technician_required
def suspend_task_view(request, report_id):
    """
    Technician suspends a task with reason.
    US-13: تعلیق با ذکر دلیل
    """
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        reason = request.POST.get('reason', '')
        if not reason:
            messages.error(request, 'لطفاً دلیل تعلیق را وارد کنید.')
            return redirect('technicians:task_detail', report_id=report_id)

        report.status = 'suspended'
        report.suspension_reason = reason
        report.save()

        RepairLog.objects.create(
            report=report, technician=tech,
            action='suspended',
            description=f'تعلیق: {reason}',
        )

        Notification.objects.create(
            user=report.reporter, report=report,
            type='status_change',
            message=f'گزارش #{report.id} به حالت تعلیق درآمد. دلیل: {reason}',
        )

        messages.success(request, 'تسک معلق شد.')
    return redirect('technicians:dashboard')


@technician_required
def request_part_view(request, report_id):
    """Technician requests a part/material for repair."""
    if request.method == 'POST':
        tech = request.user.technician_profile
        report = get_object_or_404(Report, id=report_id, technician=tech)

        part_name = request.POST.get('part_name', '')
        if part_name:
            PartRequest.objects.create(
                report=report, technician=tech, part_name=part_name,
            )
            RepairLog.objects.create(
                report=report, technician=tech,
                action='suspended',
                description=f'درخواست قطعه: {part_name}',
            )
            messages.success(request, f'درخواست قطعه «{part_name}» ثبت شد.')

    return redirect('technicians:task_detail', report_id=report_id)


@technician_required
def work_history_view(request):
    """
    Technician work history with filters.
    US-15: تاریخچه کارها با فیلتر
    """
    tech = request.user.technician_profile

    reports = Report.objects.filter(
        technician=tech,
        status__in=['resolved', 'closed', 'archived'],
    ).select_related('location__building__faculty', 'category').order_by('-closed_at')

    # Rating filter
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        reports = reports.filter(rating=int(rating_filter))

    context = {
        'reports': reports,
        'current_rating': rating_filter,
    }
    return render(request, 'technicians/work_history.html', context)
