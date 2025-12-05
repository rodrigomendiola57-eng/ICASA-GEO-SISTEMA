from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_home(request):
    return JsonResponse({
        'message': '🎉 ICASA-GEO funcionando correctamente!',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),
    path('', api_home),
]

admin.site.site_header = "ICASA-GEO Administración"
admin.site.site_title = "ICASA-GEO"
admin.site.index_title = "Panel de Administración"