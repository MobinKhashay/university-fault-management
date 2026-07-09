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
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
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

            # TODO: Auto-assign technician (US-22 - will be implemented later)

            messages.success(request, f'گزارش شما با شماره #{report.id} ثبت شد.')
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
    """
    List of user's reports with filtering and pagination.
    US-07: لیست گزارش‌های من با فیلتر و صفحه‌بندی
    """
    reports = Report.objects.filter(reporter=request.user)

    # Filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if category_filter:
        reports = reports.filter(category_id=category_filter)

    categories = FaultCategory.objects.all()

    context = {
        'reports': reports,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
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
