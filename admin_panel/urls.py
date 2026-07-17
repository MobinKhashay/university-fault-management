"""URL patterns for admin_panel app."""

from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reports/', views.manage_reports_view, name='manage_reports'),
    path('reports/<int:report_id>/detail/', views.report_detail_modal, name='report_detail'),
    path('reports/<int:report_id>/change-technician/', views.change_technician_view, name='change_technician'),
    path('reports/<int:report_id>/cancel/', views.cancel_report_view, name='cancel_report'),
    path('reports/<int:report_id>/change-priority/', views.change_priority_view, name='change_priority'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('export/excel/', views.export_excel_view, name='export_excel'),
    path('export/pdf/', views.export_pdf_view, name='export_pdf'),
    path('parts/<int:part_id>/approve/', views.approve_part_view, name='approve_part'),
    path('parts/<int:part_id>/reject/', views.reject_part_view, name='reject_part'),
]
