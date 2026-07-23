"""
Admin panel views: Dashboard, Report Management, Statistics, Export.
Related User Stories: US-16, US-17, US-19
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from reports.models import Report, RepairLog, FaultCategory, Faculty, PartRequest
from technicians.models import Technician
from accounts.models import User
from django.core.paginator import Paginator


def admin_required(view_func):
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
    """US-16: داشبورد مدیر با KPI زنده و نمودارها"""
    active_tickets = Report.objects.filter(status__in=['assigned', 'in_progress', 'suspended']).count()
    queue_tickets = Report.objects.filter(status='pending').count()
    active_technicians = Technician.objects.filter(is_active=True, status='available').count()
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    avg_rating = Report.objects.filter(rating__isnull=False, closed_at__gte=month_start).aggregate(avg=Avg('rating'))['avg'] or 0

    status_data = Report.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_map = dict(Report.STATUS_CHOICES)
    status_labels = [status_map.get(s['status'], s['status']) for s in status_data]
    status_counts = [s['count'] for s in status_data]

    faculty_data = Report.objects.values('location__building__faculty__name').annotate(count=Count('id')).order_by('-count')[:10]
    faculty_labels = [f['location__building__faculty__name'] or 'نامشخص' for f in faculty_data]
    faculty_counts = [f['count'] for f in faculty_data]

    pending_parts = PartRequest.objects.filter(status='pending').select_related('report', 'technician__user')[:10]
    suspended_tickets = Report.objects.filter(status='suspended').select_related('technician__user')[:10]

    technicians = Technician.objects.filter(is_active=True).select_related('user', 'specialty')
    tech_list = []
    for tech in technicians:
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_completed = tech.assigned_reports.filter(closed_at__gte=today_start).count()
        tech_list.append({
            'name': tech.user.full_name, 'specialty': tech.specialty.name,
            'status': tech.get_status_display(), 'status_raw': tech.status,
            'active_tasks': tech.active_tasks_count, 'today_completed': today_completed,
        })

    context = {
        'active_tickets': active_tickets, 'queue_tickets': queue_tickets,
        'active_technicians': active_technicians, 'avg_rating': round(avg_rating, 1),
        'status_labels': json.dumps(status_labels), 'status_counts': json.dumps(status_counts),
        'faculty_labels': json.dumps(faculty_labels), 'faculty_counts': json.dumps(faculty_counts),
        'pending_parts': pending_parts, 'suspended_tickets': suspended_tickets, 'technicians': tech_list,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def manage_reports_view(request):
    """US-17: مدیریت گزارش‌ها"""
    from django.core.paginator import Paginator

    reports = Report.objects.all().select_related('reporter', 'technician__user', 'location__building__faculty', 'category')

    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    faculty_filter = request.GET.get('faculty', '')
    category_filter = request.GET.get('category', '')

    if search:
        reports = reports.filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(reporter__first_name__icontains=search) | Q(reporter__last_name__icontains=search))
    if status_filter:
        reports = reports.filter(status=status_filter)
    if faculty_filter:
        reports = reports.filter(location__building__faculty_id=faculty_filter)
    if category_filter:
        reports = reports.filter(category_id=category_filter)

    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_string = ''
    if search: query_string += f'q={search}&'
    if status_filter: query_string += f'status={status_filter}&'
    if faculty_filter: query_string += f'faculty={faculty_filter}&'
    if category_filter: query_string += f'category={category_filter}&'

    context = {
        'reports': page_obj,
        'page_obj': page_obj,
        'search': search,
        'current_status': status_filter,
        'current_faculty': faculty_filter,
        'current_category': category_filter,
        'faculties': Faculty.objects.all(),
        'categories': FaultCategory.objects.all(),
        'status_choices': Report.STATUS_CHOICES,
        'technicians_list': [{'id': t.id, 'name': t.user.full_name, 'specialty': t.specialty.name} for t in Technician.objects.filter(is_active=True)],
        'query_string': query_string,
    }
    return render(request, 'admin_panel/manage_reports.html', context)


@admin_required
def report_detail_modal(request, report_id):
    """Quick view modal data (AJAX)."""
    report = get_object_or_404(Report, id=report_id)
    logs = report.logs.all()
    data = {
        'id': report.id, 'title': report.title, 'description': report.description,
        'status': report.get_status_display(), 'priority': report.get_priority_display(),
        'reporter': report.reporter.full_name,
        'technician': report.technician.user.full_name if report.technician else 'ارجاع نشده',
        'location': str(report.location), 'category': str(report.category),
        'created_at': report.created_at.strftime('%Y/%m/%d %H:%M'),
        'duration': str(report.duration_open).split('.')[0],
        'logs': [{'action': l.get_action_display(), 'time': l.created_at.strftime('%Y/%m/%d %H:%M'), 'desc': l.description} for l in logs],
    }
    return JsonResponse(data)


@admin_required
def change_technician_view(request, report_id):
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
        RepairLog.objects.create(report=report, technician=new_tech, action='reassigned',
                                 description=f'ارجاع مجدد از {old_tech.user.full_name if old_tech else "-"} به {new_tech.user.full_name} توسط مدیر')
        messages.success(request, f'گزارش #{report.id} به {new_tech.user.full_name} ارجاع شد.')
    return redirect('admin_panel:manage_reports')


@admin_required
def cancel_report_view(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        reason = request.POST.get('reason', '')
        report.status = 'cancelled'
        report.cancellation_reason = reason
        report.closed_at = timezone.now()
        report.save()
        RepairLog.objects.create(report=report, action='cancelled', description=f'لغو توسط مدیر: {reason}')
        messages.success(request, f'گزارش #{report.id} لغو شد.')
    return redirect('admin_panel:manage_reports')


@admin_required
def change_priority_view(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        new_priority = request.POST.get('priority', '')
        if new_priority in ['normal', 'important', 'urgent']:
            old = report.get_priority_display()
            report.priority = new_priority
            report.save()
            RepairLog.objects.create(report=report, action='priority_changed',
                                     description=f'تغییر اولویت از {old} به {report.get_priority_display()} توسط مدیر')
            messages.success(request, f'اولویت گزارش #{report.id} تغییر کرد.')
    return redirect('admin_panel:manage_reports')


@admin_required
def statistics_view(request):
    """US-19: آمار و گزارش‌گیری جامع"""
    period = request.GET.get('period', 'month')
    now = timezone.now()
    if period == 'week': start_date = now - timezone.timedelta(days=7)
    elif period == 'quarter': start_date = now - timezone.timedelta(days=90)
    elif period == 'year': start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
    else: start_date = now.replace(day=1, hour=0, minute=0, second=0)

    rip = Report.objects.filter(created_at__gte=start_date)
    total_reports = rip.count()
    resolved_reports = rip.filter(status__in=['resolved', 'closed']).count()
    pending_reports = rip.filter(status='pending').count()
    avg_rating = rip.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg'] or 0
    resolution_rate = round((resolved_reports / total_reports * 100), 1) if total_reports > 0 else 0

    cat_data = rip.values('category__name').annotate(count=Count('id')).order_by('-count')
    cat_labels = [c['category__name'] or '?' for c in cat_data]
    cat_counts = [c['count'] for c in cat_data]

    fac_data = rip.values('location__building__faculty__name').annotate(count=Count('id')).order_by('-count')[:10]
    fac_labels = [f['location__building__faculty__name'] or '?' for f in fac_data]
    fac_counts = [f['count'] for f in fac_data]

    pri_data = rip.values('priority').annotate(count=Count('id'))
    pri_map = dict(Report.PRIORITY_CHOICES)
    pri_labels = [pri_map.get(p['priority'], p['priority']) for p in pri_data]
    pri_counts = [p['count'] for p in pri_data]

    tech_ranking = []
    for tech in Technician.objects.filter(is_active=True).select_related('user', 'specialty'):
        completed = tech.assigned_reports.filter(status__in=['resolved', 'closed'], closed_at__gte=start_date).count()
        rating = tech.assigned_reports.filter(rating__isnull=False, closed_at__gte=start_date).aggregate(avg=Avg('rating'))['avg'] or 0
        tech_ranking.append({'name': tech.user.full_name, 'specialty': tech.specialty.name, 'completed': completed, 'rating': round(rating, 1)})
    tech_ranking.sort(key=lambda x: (-x['completed'], -x['rating']))

    critical_points = rip.values('location__building__faculty__name', 'location__building__name').annotate(count=Count('id')).order_by('-count')[:10]

    context = {
        'period': period, 'total_reports': total_reports, 'resolved_reports': resolved_reports,
        'pending_reports': pending_reports, 'avg_rating': round(avg_rating, 1), 'resolution_rate': resolution_rate,
        'cat_labels': json.dumps(cat_labels), 'cat_counts': json.dumps(cat_counts),
        'fac_labels': json.dumps(fac_labels), 'fac_counts': json.dumps(fac_counts),
        'pri_labels': json.dumps(pri_labels), 'pri_counts': json.dumps(pri_counts),
        'tech_ranking': tech_ranking, 'critical_points': critical_points,
    }
    return render(request, 'admin_panel/statistics.html', context)


@admin_required
def export_excel_view(request):
    """US-19: خروجی اکسل"""
    import openpyxl
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = 'Reports'
    ws1.append(['#', 'Title', 'Location', 'Category', 'Priority', 'Status', 'Reporter', 'Technician', 'Created', 'Rating'])
    for r in Report.objects.all().select_related('reporter', 'technician__user', 'location__building__faculty', 'category'):
        ws1.append([r.id, r.title, str(r.location), str(r.category), r.get_priority_display(), r.get_status_display(),
                    r.reporter.full_name, r.technician.user.full_name if r.technician else '-', r.created_at.strftime('%Y/%m/%d %H:%M'), r.rating or '-'])
    ws2 = wb.create_sheet('Technicians')
    ws2.append(['Name', 'Specialty', 'Completed', 'Average Rating'])
    for tech in Technician.objects.filter(is_active=True).select_related('user', 'specialty'):
        ws2.append([tech.user.full_name, tech.specialty.name, tech.total_completed, round(tech.average_rating, 1)])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reports_statistics.xlsx"'
    wb.save(response)
    return response


@admin_required
def export_pdf_view(request):
    """US-19: خروجی PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reports_statistics.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph('University Fault Management - Statistics Report', styles['Title']))
    elements.append(Spacer(1, 20))
    total = Report.objects.count()
    resolved = Report.objects.filter(status__in=['resolved', 'closed']).count()
    summary_data = [['Metric', 'Value'], ['Total Reports', str(total)], ['Resolved', str(resolved)],
                    ['Resolution Rate', f'{round(resolved/total*100,1) if total>0 else 0}%']]
    t = RLTable(summary_data, colWidths=[200, 200])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E79')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                           ('FONTSIZE', (0,0), (-1,-1), 10), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    elements.append(t)
    doc.build(elements)
    return response


@admin_required
def approve_part_view(request, part_id):
    if request.method == 'POST':
        part = get_object_or_404(PartRequest, id=part_id)
        part.status = 'approved'
        part.save()
        messages.success(request, f'درخواست قطعه «{part.part_name}» تایید شد.')
    return redirect('admin_panel:dashboard')


@admin_required
def reject_part_view(request, part_id):
    if request.method == 'POST':
        part = get_object_or_404(PartRequest, id=part_id)
        part.status = 'rejected'
        part.save()
        messages.success(request, f'درخواست قطعه «{part.part_name}» رد شد.')
    return redirect('admin_panel:dashboard')

# ============================================================
# Technician Management Views (US-04, US-18)
# ============================================================

@admin_required
def manage_technicians_view(request):
    technicians = Technician.objects.filter(is_active=True).select_related('user', 'specialty')
    inactive = Technician.objects.filter(is_active=False).select_related('user', 'specialty')
    return render(request, 'admin_panel/manage_technicians.html', {
        'technicians': technicians, 'inactive_technicians': inactive,
    })


@admin_required
def register_technician_view(request):
    from .forms import TechnicianRegistrationForm
    if request.method == 'POST':
        form = TechnicianRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                student_id=form.cleaned_data['personnel_code'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role='technician',
                is_verified=True,
            )
            Technician.objects.create(
                user=user,
                specialty=form.cleaned_data['specialty'],
                personnel_code=form.cleaned_data['personnel_code'],
                shift_start=form.cleaned_data['shift_start'],
                shift_end=form.cleaned_data['shift_end'],
            )
            messages.success(request, f'تکنسین {user.full_name} با موفقیت ثبت شد.')
            return redirect('admin_panel:manage_technicians')
    else:
        form = TechnicianRegistrationForm()
    return render(request, 'admin_panel/register_technician.html', {'form': form})


@admin_required
def toggle_technician_view(request, tech_id):
    if request.method == 'POST':
        tech = get_object_or_404(Technician, id=tech_id)
        tech.is_active = not tech.is_active
        tech.save()
        status = 'فعال' if tech.is_active else 'غیرفعال'
        messages.success(request, f'تکنسین {tech.user.full_name} {status} شد.')
    return redirect('admin_panel:manage_technicians')


@admin_required
def technician_workload_view(request, tech_id):
    """View technician's all tasks (AJAX)."""
    tech = get_object_or_404(Technician, id=tech_id)

    active_tasks = tech.assigned_reports.filter(
        status__in=['assigned', 'in_progress', 'suspended']
    ).values('id', 'title', 'status', 'priority', 'created_at')

    completed_tasks = tech.assigned_reports.filter(
        status__in=['resolved', 'closed', 'archived']
    ).values('id', 'title', 'status', 'priority', 'created_at', 'rating', 'closed_at').order_by('-closed_at')[:10]

    status_map = dict(Report.STATUS_CHOICES)
    priority_map = dict(Report.PRIORITY_CHOICES)

    def format_tasks(tasks):
        result = []
        for t in tasks:
            item = {
                'id': t['id'], 'title': t['title'],
                'status': status_map.get(t['status'], t['status']),
                'priority': priority_map.get(t['priority'], t['priority']),
                'created_at': t['created_at'].strftime('%Y/%m/%d'),
            }
            if 'rating' in t:
                item['rating'] = t['rating']
            if 'closed_at' in t and t['closed_at']:
                item['closed_at'] = t['closed_at'].strftime('%Y/%m/%d')
            result.append(item)
        return result

    return JsonResponse({
        'name': tech.user.full_name,
        'specialty': tech.specialty.name,
        'total_completed': tech.total_completed,
        'avg_rating': round(tech.average_rating, 1),
        'active_tasks': format_tasks(active_tasks),
        'completed_tasks': format_tasks(completed_tasks),
    })

@admin_required
def resume_report_view(request, report_id):
    """Admin resumes a suspended report."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        report.status = 'in_progress'
        report.suspension_reason = ''
        report.save()
        RepairLog.objects.create(
            report=report, action='resumed',
            description='ازسرگیری توسط مدیر',
        )
        messages.success(request, f'گزارش #{report.id} از تعلیق خارج شد.')
    return redirect('admin_panel:manage_reports')

@admin_required
def verify_users_view(request):
    """Admin verifies new users by checking their ID card."""
    unverified = User.objects.filter(
        is_verified=True,
        is_id_verified=False,
    ).exclude(role__in=['admin', 'technician']).exclude(id_card_image='')
    verified = User.objects.filter(is_id_verified=True).exclude(role__in=['admin', 'technician'])[:20]

    return render(request, 'admin_panel/verify_users.html', {
        'unverified': unverified,
        'verified': verified,
    })


@admin_required
def approve_user_view(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_id_verified = True
        user.save()
        from notifications.models import Notification
        Notification.objects.create(
            user=user,
            type='status_change',
            message='هویت شما تایید شد ✅',
        )
        messages.success(request, f'هویت {user.full_name} تایید شد.')
    return redirect('admin_panel:verify_users')


@admin_required
def reject_user_view(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        reason = request.POST.get('reason', 'تصویر کارت شناسایی نامعتبر')
        # Clear the image so user needs to re-upload
        user.id_card_image.delete(save=False)
        user.id_card_image = None
        user.save()
        from notifications.models import Notification
        Notification.objects.create(
            user=user,
            type='status_change',
            message=f'تصویر کارت شناسایی شما رد شد. دلیل: {reason}. لطفاً از طریق پروفایل تصویر جدید آپلود کنید.',
        )
        messages.success(request, f'هویت {user.full_name} رد شد و از لیست حذف شد.')
    return redirect('admin_panel:verify_users')

@admin_required
def edit_technician_view(request, tech_id):
    """Admin edits technician info."""
    tech = get_object_or_404(Technician, id=tech_id)
    from reports.models import Specialty

    if request.method == 'POST':
        tech.user.first_name = request.POST.get('first_name', tech.user.first_name)
        tech.user.last_name = request.POST.get('last_name', tech.user.last_name)
        tech.user.email = request.POST.get('email', tech.user.email)
        tech.user.phone = request.POST.get('phone', tech.user.phone)
        tech.user.save()

        specialty_id = request.POST.get('specialty')
        if specialty_id:
            tech.specialty = Specialty.objects.get(id=specialty_id)
        tech.shift_start = request.POST.get('shift_start', tech.shift_start)
        tech.shift_end = request.POST.get('shift_end', tech.shift_end)
        tech.save()

        messages.success(request, f'اطلاعات {tech.user.full_name} بروزرسانی شد.')
        return redirect('admin_panel:manage_technicians')

    specialties = Specialty.objects.all()
    return render(request, 'admin_panel/edit_technician.html', {
        'tech': tech,
        'specialties': specialties,
    })

@admin_required
def reset_tech_password_view(request, tech_id):
    """Admin resets technician password."""
    tech = get_object_or_404(Technician, id=tech_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        if len(new_password) < 8:
            messages.error(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد.')
            return redirect('admin_panel:edit_technician', tech_id=tech_id)

        tech.user.set_password(new_password)
        tech.user.save()

        from notifications.models import Notification
        Notification.objects.create(
            user=tech.user,
            type='status_change',
            message='رمز عبور شما توسط مدیر تغییر کرد. لطفاً با رمز جدید وارد شوید.',
        )

        messages.success(request, f'رمز عبور {tech.user.full_name} تغییر کرد.')
    return redirect('admin_panel:manage_technicians')

@admin_required
def change_tech_status_view(request, tech_id):
    """Admin manually changes technician availability status."""
    if request.method == 'POST':
        tech = get_object_or_404(Technician, id=tech_id)
        new_status = request.POST.get('status', '')

        if new_status in ['available', 'busy', 'off_shift']:
            old_status = tech.get_status_display()
            tech.status = new_status
            tech.save()

            from notifications.models import Notification
            status_labels = dict(Technician.STATUS_CHOICES)
            Notification.objects.create(
                user=tech.user,
                type='status_change',
                message=f'وضعیت حضور شما توسط مدیر از «{old_status}» به «{status_labels[new_status]}» تغییر کرد.',
            )

            messages.success(request, f'وضعیت {tech.user.full_name} به «{status_labels[new_status]}» تغییر کرد.')
    return redirect('admin_panel:manage_technicians')

@admin_required
def manage_users_view(request):
    """Admin manages all users."""
    from django.core.paginator import Paginator

    users = User.objects.all().exclude(role='admin').order_by('-created_at')

    # Search
    search = request.GET.get('q', '')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(student_id__icontains=search) | Q(email__icontains=search)
        )

    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'verified':
        users = users.filter(is_verified=True)
    elif status_filter == 'unverified':
        users = users.filter(is_verified=False)
    elif status_filter == 'id_verified':
        users = users.filter(is_id_verified=True)
    elif status_filter == 'id_not_verified':
        users = users.filter(is_id_verified=False)

    paginator = Paginator(users, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_string = ''
    if search: query_string += f'q={search}&'
    if role_filter: query_string += f'role={role_filter}&'
    if status_filter: query_string += f'status={status_filter}&'

    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'search': search,
        'current_role': role_filter,
        'current_status': status_filter,
        'query_string': query_string,
        'total_users': User.objects.exclude(role='admin').count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_professors': User.objects.filter(role='professor').count(),
        'total_staff': User.objects.filter(role='staff').count(),
        'total_technicians': User.objects.filter(role='technician').count(),
    }
    return render(request, 'admin_panel/manage_users.html', context)


@admin_required
def toggle_user_view(request, user_id):
    """Activate/deactivate a user."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.is_admin_user:
            messages.error(request, 'نمی‌توان مدیر را غیرفعال کرد.')
            return redirect('admin_panel:manage_users')

        user.is_active = not user.is_active
        user.save()
        status = 'فعال' if user.is_active else 'غیرفعال'
        messages.success(request, f'کاربر {user.full_name} {status} شد.')
    return redirect('admin_panel:manage_users')


@admin_required
def user_detail_view(request, user_id):
    """AJAX user detail."""
    user = get_object_or_404(User, id=user_id)

    data = {
        'id': user.id,
        'full_name': user.full_name,
        'student_id': user.student_id,
        'email': user.email,
        'phone': user.phone or '—',
        'role': user.get_role_display(),
        'is_verified': user.is_verified,
        'is_id_verified': user.is_id_verified,
        'is_active': user.is_active,
        'date_joined': user.created_at.strftime('%Y/%m/%d %H:%M'),
        'has_id_card': bool(user.id_card_image),
        'id_card_url': user.id_card_image.url if user.id_card_image else '',
        'has_profile_image': bool(user.profile_image),
        'profile_image_url': user.profile_image.url if user.profile_image else '',
        'report_count': Report.objects.filter(reporter=user).count(),
    }
    return JsonResponse(data)