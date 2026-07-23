from django.contrib import admin
from .models import Technician

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'personnel_code', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'specialty']