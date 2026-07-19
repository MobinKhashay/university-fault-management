from django.urls import path
from . import views
app_name = 'faq'
urlpatterns = [
    path('', views.faq_list_view, name='list'),
    path('vote/<int:faq_id>/', views.faq_vote_view, name='vote'),
    path('manage/', views.faq_manage_view, name='manage'),
    path('create/', views.faq_create_view, name='create'),
    path('delete/<int:faq_id>/', views.faq_delete_view, name='delete'),
]
