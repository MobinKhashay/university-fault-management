"""URL patterns for admin_panel app."""

from django.urls import path
from . import views
from . import views, structure_views

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
    path('technicians/', views.manage_technicians_view, name='manage_technicians'),
    path('technicians/register/', views.register_technician_view, name='register_technician'),
    path('technicians/<int:tech_id>/toggle/', views.toggle_technician_view, name='toggle_technician'),
    path('technicians/<int:tech_id>/workload/', views.technician_workload_view, name='technician_workload'),
    path('reports/<int:report_id>/resume/', views.resume_report_view, name='resume_report'),
    path('verify-users/', views.verify_users_view, name='verify_users'),
    path('verify-users/<int:user_id>/approve/', views.approve_user_view, name='approve_user'),
    path('verify-users/<int:user_id>/reject/', views.reject_user_view, name='reject_user'),
    path('technicians/<int:tech_id>/edit/', views.edit_technician_view, name='edit_technician'),
    path('technicians/<int:tech_id>/reset-password/', views.reset_tech_password_view, name='reset_tech_password'),
    path('technicians/<int:tech_id>/change-status/', views.change_tech_status_view, name='change_tech_status'),
    # Structure settings
    path('structure/', structure_views.structure_settings_view, name='structure_settings'),
    path('structure/add-faculty/', structure_views.add_faculty_view, name='add_faculty'),
    path('structure/add-building/', structure_views.add_building_view, name='add_building'),
    path('structure/add-location/', structure_views.add_location_view, name='add_location'),
    path('structure/add-specialty/', structure_views.add_specialty_view, name='add_specialty'),
    path('structure/add-category/', structure_views.add_category_view, name='add_category'),
    path('structure/delete-faculty/<int:pk>/', structure_views.delete_faculty_view, name='delete_faculty'),
    path('structure/delete-building/<int:pk>/', structure_views.delete_building_view, name='delete_building'),
    path('structure/delete-location/<int:pk>/', structure_views.delete_location_view, name='delete_location'),
    path('structure/delete-specialty/<int:pk>/', structure_views.delete_specialty_view, name='delete_specialty'),
    path('structure/delete-category/<int:pk>/', structure_views.delete_category_view, name='delete_category'),
    path('users/', views.manage_users_view, name='manage_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_view, name='toggle_user'),
    path('users/<int:user_id>/detail/', views.user_detail_view, name='user_detail'),
]