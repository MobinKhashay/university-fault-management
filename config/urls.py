"""URL configuration for the project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import landing_view


urlpatterns = [
    path('', landing_view, name='landing'),
    path('django-admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('reports/', include('reports.urls')),
    path('technicians/', include('technicians.urls')),
    path('panel/', include('admin_panel.urls')),
    path('notifications/', include('notifications.urls')),
    path('faq/', include('faq.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

