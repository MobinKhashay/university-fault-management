"""University structure management. US-21"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from reports.models import Faculty, Building, Location, FaultCategory, Specialty


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def structure_settings_view(request):
    faculties = Faculty.objects.all().prefetch_related('buildings__locations')
    specialties = Specialty.objects.all().prefetch_related('categories')
    return render(request, 'admin_panel/structure_settings.html', {
        'faculties': faculties,
        'specialties': specialties,
    })


@admin_required
def add_faculty_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Faculty.objects.create(name=name)
            messages.success(request, f'دانشکده «{name}» اضافه شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def add_building_view(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        name = request.POST.get('name', '').strip()
        if faculty_id and name:
            faculty = get_object_or_404(Faculty, id=faculty_id)
            Building.objects.create(faculty=faculty, name=name)
            messages.success(request, f'ساختمان «{name}» اضافه شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def add_location_view(request):
    if request.method == 'POST':
        building_id = request.POST.get('building_id')
        floor = request.POST.get('floor', '').strip()
        room = request.POST.get('room', '').strip()
        if building_id:
            building = get_object_or_404(Building, id=building_id)
            Location.objects.create(building=building, floor=floor, room=room, location_type='faculty')
            messages.success(request, f'طبقه {floor} اتاق {room} اضافه شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def add_specialty_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Specialty.objects.create(name=name)
            messages.success(request, f'تخصص «{name}» اضافه شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def add_category_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        specialty_id = request.POST.get('specialty_id')
        if name and specialty_id:
            specialty = get_object_or_404(Specialty, id=specialty_id)
            FaultCategory.objects.create(name=name, specialty=specialty)
            messages.success(request, f'دسته‌بندی «{name}» اضافه شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def delete_faculty_view(request, pk):
    if request.method == 'POST':
        get_object_or_404(Faculty, id=pk).delete()
        messages.success(request, 'حذف شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def delete_building_view(request, pk):
    if request.method == 'POST':
        get_object_or_404(Building, id=pk).delete()
        messages.success(request, 'حذف شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def delete_location_view(request, pk):
    if request.method == 'POST':
        get_object_or_404(Location, id=pk).delete()
        messages.success(request, 'حذف شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def delete_specialty_view(request, pk):
    if request.method == 'POST':
        get_object_or_404(Specialty, id=pk).delete()
        messages.success(request, 'حذف شد.')
    return redirect('admin_panel:structure_settings')


@admin_required
def delete_category_view(request, pk):
    if request.method == 'POST':
        get_object_or_404(FaultCategory, id=pk).delete()
        messages.success(request, 'حذف شد.')
    return redirect('admin_panel:structure_settings')