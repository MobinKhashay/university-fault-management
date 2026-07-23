from django.contrib import admin
from .models import (
    Faculty, Building, Location, Specialty, FaultCategory,
    Report, ReportMedia, RepairLog, TicketMessage, PartRequest,
)

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(FaultCategory)
class FaultCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'specialty']

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'faculty']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'building', 'floor', 'room', 'location_type']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'reporter', 'technician', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority']

admin.site.register(ReportMedia)
admin.site.register(RepairLog)
admin.site.register(TicketMessage)
admin.site.register(PartRequest)