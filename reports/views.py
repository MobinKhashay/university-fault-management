"""
Report views: Dashboard, Submit Report, My Reports.
Related User Stories: US-05, US-06, US-07
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import (
    Report, ReportMedia, RepairLog, Faculty, Building,
    Location, FaultCategory, Specialty,
)
from .forms import ReportForm


@login_required
def dashboard_view(request):
    """
    Reporter dashboard.
    US-05: داشبورد گزارش‌دهنده با خلاصه وضعیت و ۵ گزارش اخیر
    """
    user = request.user
    reports = Report.objects.filter(reporter=user)

    context = {
        'total_reports': reports.count(),
        'pending_reports': reports.filter(status__in=['pending', 'assigned']).count(),
        'in_progress_reports': reports.filter(status='in_progress').count(),
        'resolved_reports': reports.filter(status__in=['resolved', 'closed']).count(),
        'recent_reports': reports[:5],
        'unread_notifications': user.notifications.filter(is_read=False).count(),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def submit_report_view(request):
    """
    Submit a new fault report.
    US-06: ثبت گزارش خرابی با مکان سلسله‌مراتبی، دسته‌بندی، آپلود عکس
    """
    # Check ID card verification
    if not request.user.is_admin_user and not request.user.is_technician:
        if not request.user.is_id_verified:
            messages.error(request,
                           '⚠️ برای ثبت گزارش خرابی، ابتدا باید تصویر کارت شناسایی شما توسط مدیر تایید شود. لطفاً از بخش پروفایل تصویر کارت شناسایی خود را آپلود کنید.')
            return redirect('accounts:profile')
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)

        # Debug: show form errors
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        else:
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()

            # Handle image uploads (max 3)
            images = request.FILES.getlist('images')
            for i, image in enumerate(images[:3]):
                ReportMedia.objects.create(
                    report=report,
                    file_path=image,
                    file_type='image',
                    is_after=False,
                )

            # Handle optional video
            video = request.FILES.get('video')
            if video:
                ReportMedia.objects.create(
                    report=report,
                    file_path=video,
                    file_type='video',
                    is_after=False,
                )

            # Handle optional audio
            audio = request.FILES.get('audio')
            if audio:
                report.audio_file = audio
                report.save()

            # Create initial log entry
            RepairLog.objects.create(
                report=report,
                action='created',
                description=f'گزارش توسط {request.user.full_name} ثبت شد.',
            )

            # Auto-assign technician (US-22)
            from .assignment_engine import AssignmentEngine
            engine = AssignmentEngine(report)
            success, assign_message = engine.assign()

            if success:
                messages.success(request, f'گزارش شما با شماره #{report.id} ثبت شد و به تکنسین ارجاع داده شد.')
            else:
                messages.success(request, f'گزارش شما با شماره #{report.id} ثبت شد. در صف انتظار برای ارجاع قرار گرفت.')
            return redirect('reports:my_reports')
    else:
        form = ReportForm()

    faculties = Faculty.objects.all()
    categories = FaultCategory.objects.all()

    return render(request, 'reports/submit_report.html', {
        'form': form,
        'faculties': faculties,
        'categories': categories,
    })


@login_required
def my_reports_view(request):
    from django.core.paginator import Paginator

    reports = Report.objects.filter(reporter=request.user)

    # Search
    search = request.GET.get('q', '')
    if search:
        reports = reports.filter(
            Q(id__icontains=search) | Q(title__icontains=search)
        )

    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if category_filter:
        reports = reports.filter(category_id=category_filter)

    categories = FaultCategory.objects.all()

    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_string = ''
    if search: query_string += f'q={search}&'
    if status_filter: query_string += f'status={status_filter}&'
    if category_filter: query_string += f'category={category_filter}&'

    context = {
        'reports': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
        'query_string': query_string,
        'search': search,
    }
    return render(request, 'reports/my_reports.html', context)


# ============================================================
# AJAX Endpoints for Dynamic Form
# ============================================================

def ajax_get_buildings(request):
    """Return buildings for a given faculty (AJAX)."""
    faculty_id = request.GET.get('faculty_id')
    if not faculty_id:
        return JsonResponse({'buildings': []})

    buildings = Building.objects.filter(faculty_id=faculty_id).values('id', 'name')
    return JsonResponse({'buildings': list(buildings)})


def ajax_get_locations(request):
    """Return floors and rooms for a given building (AJAX)."""
    building_id = request.GET.get('building_id')
    if not building_id:
        return JsonResponse({'locations': []})

    locations = Location.objects.filter(building_id=building_id).values(
        'id', 'floor', 'room', 'location_type'
    )
    return JsonResponse({'locations': list(locations)})


def ajax_check_duplicate(request):
    """
    Check for similar reports in the same location.
    US-06: تشخیص گزارش تکراری
    """
    location_id = request.GET.get('location_id')
    category_id = request.GET.get('category_id')

    if not location_id or not category_id:
        return JsonResponse({'duplicates': []})

    # Find open reports in same location with same category
    duplicates = Report.objects.filter(
        location_id=location_id,
        category_id=category_id,
        status__in=['pending', 'assigned', 'in_progress'],
    ).values('id', 'title', 'status', 'created_at')[:5]

    result = []
    for d in duplicates:
        result.append({
            'id': d['id'],
            'title': d['title'],
            'status': d['status'],
            'created_at': d['created_at'].strftime('%Y/%m/%d'),
        })

    return JsonResponse({'duplicates': result})


@login_required
def send_message_view(request, report_id):
    """Send a message within a ticket."""
    report = get_object_or_404(Report, id=report_id)

    # Check access: only reporter or assigned technician
    if request.user != report.reporter:
        if hasattr(request.user, 'technician_profile') and report.technician:
            if request.user.technician_profile != report.technician:
                messages.error(request, 'دسترسی ندارید.')
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'دسترسی ندارید.')
            return redirect('accounts:dashboard')

    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')

        if text:
            from .models import TicketMessage
            TicketMessage.objects.create(
                report=report,
                sender=request.user,
                message=text,
                attachment=attachment,
            )

            # Notify the other party
            from notifications.models import Notification
            if request.user == report.reporter and report.technician:
                Notification.objects.create(
                    user=report.technician.user, report=report,
                    type='new_message',
                    message=f'پیام جدید از گزارش‌دهنده در تیکت #{report.id}',
                )
            elif report.reporter:
                Notification.objects.create(
                    user=report.reporter, report=report,
                    type='new_message',
                    message=f'پیام جدید از تکنسین در تیکت #{report.id}',
                )

            messages.success(request, 'پیام ارسال شد.')

    # Redirect back to where they came from
    if hasattr(request.user, 'technician_profile') and request.user.is_technician:
        return redirect('technicians:task_detail', report_id=report_id)
    else:
        return redirect('reports:report_detail', report_id=report_id)


@login_required
def report_detail_view(request, report_id):
    """Reporter views report detail with messages and rating."""
    report = get_object_or_404(Report, id=report_id, reporter=request.user)
    logs = report.logs.all().order_by('created_at')
    media = report.media.filter(is_after=False)
    after_media = report.media.filter(is_after=True)
    ticket_messages = report.messages.all().order_by('created_at')

    return render(request, 'reports/report_detail.html', {
        'report': report, 'logs': logs, 'media': media,
        'after_media': after_media, 'ticket_messages': ticket_messages,
    })


@login_required
def rate_report_view(request, report_id):
    """Reporter rates a resolved report."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id, reporter=request.user)
        rating = request.POST.get('rating')
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                report.rating = rating
                report.status = 'closed'
                report.save()

                from .models import RepairLog
                RepairLog.objects.create(
                    report=report, action='rated',
                    description=f'امتیاز {rating} ستاره توسط گزارش‌دهنده',
                )
                messages.success(request, f'امتیاز {rating} ستاره ثبت شد.')
        except (ValueError, TypeError):
            messages.error(request, 'امتیاز نامعتبر.')

    return redirect('reports:report_detail', report_id=report_id)

def ajax_report_preview(request):
    """AJAX preview of a report for duplicate checking."""
    report_id = request.GET.get('report_id')
    if not report_id:
        return JsonResponse({'error': 'missing id'})
    try:
        report = Report.objects.select_related(
            'reporter', 'location__building__faculty', 'category', 'technician__user'
        ).get(id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'not found'})

    return JsonResponse({
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'location': str(report.location),
        'category': str(report.category),
        'status': report.get_status_display(),
        'priority': report.get_priority_display(),
        'reporter': report.reporter.full_name,
        'technician': report.technician.user.full_name if report.technician else 'ارجاع نشده',
        'created_at': report.created_at.strftime('%Y/%m/%d %H:%M'),
    })