"""
URL configuration for ICASA-GEO project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/core/', include('apps.core.urls')),
    path('api/v1/knowledge/', include('apps.knowledge_base.urls')),
    path('api/v1/organizational/', include('apps.organizational.urls')),
    path('api/v1/positions/', include('apps.positions.urls')),
    
    # CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin site customization
admin.site.site_header = "ICASA-GEO Administración"
admin.site.site_title = "ICASA-GEO"
admin.site.index_title = "Panel de Administración"