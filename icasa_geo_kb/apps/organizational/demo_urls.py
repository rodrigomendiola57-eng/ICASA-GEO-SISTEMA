from django.urls import path
from . import demo_views

app_name = 'organizational_demo'

urlpatterns = [
    # Dashboard de demostración
    path('demo/', demo_views.demo_dashboard, name='demo_dashboard'),
    
    # APIs de demostración
    path('demo/api/create/', demo_views.demo_create_chart, name='demo_create_chart'),
    path('demo/api/upload/', demo_views.demo_upload_chart, name='demo_upload_chart'),
    path('demo/api/charts/', demo_views.demo_get_charts_api, name='demo_get_charts_api'),
    path('demo/api/<int:chart_id>/delete/', demo_views.demo_delete_chart, name='demo_delete_chart'),
    
    # Detalle de organigrama de demostración
    path('demo/chart/<int:chart_id>/', demo_views.demo_chart_detail, name='demo_chart_detail'),
]