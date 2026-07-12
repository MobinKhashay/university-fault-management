"""
Admin panel views: Dashboard, Report Management.
Related User Stories: US-16, US-17
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from reports.models import Report, RepairLog, FaultCategory, Faculty
from technicians.models import Technician
from accounts.models import User


def admin_required(view_func):
    """Decorator to restrict access to admin users only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            messages.error(request, 'شما دسترسی به پنل مدیر ندارید.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard_view(request):
    """
    Admin dashboard with KPI cards, charts data, and technician monitoring.
    US-16: داشبورد مدیر با KPI زنده و نمودارها
    """
    # KPI Cards
    active_tickets = Report.objects.filter(
        status__in=['assigned', 'in_progress', 'suspended']
    ).count()

    queue_tickets = Report.objects.filter(status='pending').count()

    active_technicians = Technician.objects.filter(
        is_active=True, status='available'
    ).count()

    # Average satisfaction this month
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    avg_rating = Report.objects.filter(
        rating__isnull=False,
        closed_at__gte=month_start,
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    # Chart Data: Ticket status distribution (Pie Chart)
    status_data = Report.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    status_labels = []
    status_counts = []
    status_map = dict(Report.STATUS_CHOICES)
    for item in status_data:
        status_labels.append(status_map.get(item['status'], item['status']))
        status_counts.append(item['count'])

    # Chart Data: Tickets per faculty (Bar Chart)
    faculty_data = Report.objects.values(
        'location__building__faculty__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    faculty_labels = []
    faculty_counts = []
    for item in faculty_data:
        name = item['location__building__faculty__name'] or 'نامشخص'
        faculty_labels.append(name)
        faculty_counts.append(item['count'])

    # Approval required: Part requests pending
    from reports.models import PartRequest
    pending_parts = PartRequest.objects.filter(status='pending').select_related(
        'report', 'technician__user'
    )[:10]

    # Suspended tickets
    suspended_tickets = Report.objects.filter(
        status='suspended'
    ).select_related('technician__user')[:10]

    # Technician monitoring table
    technicians = Technician.objects.filter(is_active=True).select_related(
        'user', 'specialty'
    )

    tech_list = []
    for tech in technicians:
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_completed = tech.assigned_reports.filter(
            closed_at__gte=today_start
        ).count()

        tech_list.append({
            'name': tech.user.full_name,
            'specialty': tech.specialty.name,
            'status': tech.get_status_display(),
            'status_raw': tech.status,
            'active_tasks': tech.active_tasks_count,
            'today_completed': today_completed,
        })

    import json
    context = {
        'active_tickets': active_tickets,
        'queue_tickets': queue_tickets,
        'active_technicians': active_technicians,
        'avg_rating': round(avg_rating, 1),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'faculty_labels': json.dumps(faculty_labels),
        'faculty_counts': json.dumps(faculty_counts),
        'pending_parts': pending_parts,
        'suspended_tickets': suspended_tickets,
        'technicians': tech_list,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def manage_reports_view(request):
    """
    Report management with search, filters and admin actions.
    US-17: مدیریت گزارش‌ها با جستجو و فیلتر
    """
    reports = Report.objects.all().select_related(
        'reporter', 'technician__user', 'location__building__faculty', 'category'
    )

    # Search
    search = request.GET.get('q', '')
    if search:
        reports = reports.filter(
            Q(id__icontains=search) |
            Q(title__icontains=search) |
            Q(reporter__first_name__icontains=search) |
            Q(reporter__last_name__icontains=search) |
            Q(technician__user__first_name__icontains=search) |
            Q(technician__user__last_name__icontains=search)
        )

    # Filters
    status_filter = request.GET.get('status', '')
    faculty_filter = request.GET.get('faculty', '')
    category_filter = request.GET.get('category', '')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if faculty_filter:
        reports = reports.filter(location__building__faculty_id=faculty_filter)
    if category_filter:
        reports = reports.filter(category_id=category_filter)

    context = {
        'reports': reports[:100],
        'search': search,
        'current_status': status_filter,
        'current_faculty': faculty_filter,
        'current_category': category_filter,
        'faculties': Faculty.objects.all(),
        'categories': FaultCategory.objects.all(),
        'status_choices': Report.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/manage_reports.html', context)


@admin_required
def report_detail_modal(request, report_id):
    """Quick view modal data for a report (AJAX)."""
    report = get_object_or_404(Report, id=report_id)
    logs = report.logs.all()
    media = report.media.all()

    data = {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'status': report.get_status_display(),
        'priority': report.get_priority_display(),
        'reporter': report.reporter.full_name,
        'technician': report.technician.user.full_name if report.technician else 'ارجاع نشده',
        'location': str(report.location),
        'category': str(report.category),
        'created_at': report.created_at.strftime('%Y/%m/%d %H:%M'),
        'duration': str(report.duration_open).split('.')[0],
        'logs': [
            {'action': log.get_action_display(), 'time': log.created_at.strftime('%Y/%m/%d %H:%M'), 'desc': log.description}
            for log in logs
        ],
        'media': [
            {'url': m.file_path.url, 'type': m.file_type}
            for m in media
        ],
    }
    return JsonResponse(data)


@admin_required
def change_technician_view(request, report_id):
    """Admin manually changes assigned technician."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        tech_id = request.POST.get('technician_id')

        try:
            new_tech = Technician.objects.get(id=tech_id, is_active=True)
        except Technician.DoesNotExist:
            messages.error(request, 'تکنسین یافت نشد.')
            return redirect('admin_panel:manage_reports')

        old_tech = report.technician
        report.technician = new_tech
        report.status = 'assigned'
        report.save()

        RepairLog.objects.create(
            report=report,
            technician=new_tech,
            action='reassigned',
            description=f'ارجاع مجدد از {old_tech.user.full_name if old_tech else "بدون تکنسین"} به {new_tech.user.full_name} توسط مدیر',
        )

        messages.success(request, f'گزارش #{report.id} به {new_tech.user.full_name} ارجاع شد.')

    return redirect('admin_panel:manage_reports')


@admin_required
def cancel_report_view(request, report_id):
    """Admin cancels a report with reason."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        reason = request.POST.get('reason', '')

        report.status = 'cancelled'
        report.cancellation_reason = reason
        report.closed_at = timezone.now()
        report.save()

        RepairLog.objects.create(
            report=report,
            action='cancelled',
            description=f'لغو توسط مدیر: {reason}',
        )

        messages.success(request, f'گزارش #{report.id} لغو شد.')

    return redirect('admin_panel:manage_reports')


@admin_required
def change_priority_view(request, report_id):
    """Admin changes report priority."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        new_priority = request.POST.get('priority', '')

        if new_priority in ['normal', 'important', 'urgent']:
            old = report.get_priority_display()
            report.priority = new_priority
            report.save()

            RepairLog.objects.create(
                report=report,
                action='priority_changed',
                description=f'تغییر اولویت از {old} به {report.get_priority_display()} توسط مدیر',
            )

            messages.success(request, f'اولویت گزارش #{report.id} تغییر کرد.')

    return redirect('admin_panel:manage_reports')
