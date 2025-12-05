from django.urls import path
from . import views, demo_views
# from . import corporate_views  # Comentado temporalmente

app_name = 'organizational'

urlpatterns = [
    # 1. 🕸️ ORGANIGRAMA POR DEPARTAMENTOS (Principal)
    path('', views.organizational_dashboard, name='dashboard'),
    
    # DEMO - Funcionalidad de demostración
    path('demo/', demo_views.demo_dashboard, name='demo_dashboard'),
    path('demo/api/create/', demo_views.demo_create_chart, name='demo_create_chart'),
    path('demo/api/upload/', demo_views.demo_upload_chart, name='demo_upload_chart'),
    path('demo/api/charts/', demo_views.demo_get_charts_api, name='demo_get_charts_api'),
    path('demo/api/<int:chart_id>/delete/', demo_views.demo_delete_chart, name='demo_delete_chart'),
    path('demo/chart/<int:chart_id>/', demo_views.demo_chart_detail, name='demo_chart_detail'),
    
    # FUNCIONALIDADES CORPORATIVAS (Comentadas temporalmente)
    # Se habilitarán después de ejecutar migraciones
    
    # Organigramas Departamentales - API
    path('api/departmental/create/', views.create_departmental_chart, name='create_departmental_chart'),
    path('api/departmental/upload/', views.upload_departmental_chart, name='upload_departmental_chart'),
    path('api/departmental/charts/', views.get_departmental_charts_api, name='get_departmental_charts_api'),
    path('api/departmental/<int:chart_id>/delete/', views.delete_departmental_chart, name='delete_departmental_chart'),
    
    # Detalle de organigrama departamental
    path('departamental/<int:chart_id>/', views.departmental_chart_detail, name='departmental_chart_detail'),
    
    # Editor de organigrama
    path('departamental/<int:chart_id>/editor/', views.organigram_editor, name='organigram_editor'),
    path('api/departmental/<int:chart_id>/positions/', views.get_chart_positions_api, name='get_chart_positions_api'),
    path('api/departmental/<int:chart_id>/save-positions/', views.save_chart_positions_api, name='save_chart_positions_api'),
    path('api/departmental/<int:chart_id>/add-position/', views.add_position_to_chart_api, name='add_position_to_chart_api'),
    path('api/departmental/<int:chart_id>/remove-position/', views.remove_position_from_chart_api, name='remove_position_from_chart_api'),
    path('api/departmental/<int:chart_id>/activate/', views.activate_version_api, name='activate_version_api'),
    path('api/departmental/version/<int:version_id>/delete/', views.delete_version_api, name='delete_version_api'),
    
    # Organigrama Interactivo (Funcionalidad avanzada)
    path('interactivo/', views.interactive_organigram, name='interactive_organigram'),
    path('api/organigram-data/', views.organigram_data_api, name='organigram_data_api'),
    path('api/position/<int:position_id>/', views.position_detail_api, name='position_detail_api'),
    path('api/save-positions/', views.save_position_coordinates, name='save_positions'),
    
    # 2. 📋 PERFILES DE PUESTO
    path('perfiles/', views.job_profiles_list, name='job_profiles'),
    path('perfiles/<int:profile_id>/', views.job_profile_detail, name='job_profile_detail'),
    
    # 3. 🎯 MATRIZ DE COMPETENCIAS
    path('competencias/', views.competency_matrix, name='competency_matrix'),
    
    # 4. 🤝 COMITÉS Y GRUPOS
    path('comites/', views.committees_list, name='committees'),
    path('comites/<int:committee_id>/', views.committee_detail, name='committee_detail'),
    
    # 5. 🏢 ADMINISTRACIÓN DE PUESTOS
    path('admin/puestos/', views.position_admin_list, name='position_admin_list'),
    path('admin/puestos/crear/', views.position_create, name='position_create'),
    path('admin/puestos/<int:pk>/editar/', views.position_edit, name='position_edit'),
    path('admin/puestos/<int:pk>/eliminar/', views.position_delete, name='position_delete'),
    path('admin/puestos/<int:pk>/asignar/', views.position_assign_employee, name='position_assign_employee'),
    path('admin/puestos/<int:pk>/desasignar/', views.position_unassign_employee, name='position_unassign_employee'),
    
    # Configuración y otros
    path('organigramas/', views.chart_list, name='chart_list'),
    path('organigramas/<int:pk>/', views.chart_detail, name='chart_detail'),
    path('puestos/', views.position_list, name='position_list'),
    # 6. 🔄 FLUJOGRAMAS
    path('flujogramas/', views.flow_list, name='flowcharts_dashboard'),
    path('flujogramas/editor/', views.flowchart_editor, name='flowchart_editor'),
    path('flujogramas/editor/<int:process_id>/', views.flowchart_editor, name='flowchart_editor_edit'),
    
    # APIs para flujogramas
    path('api/flujogramas/save/', views.save_flowchart, name='save_flowchart'),
    path('api/flujogramas/<int:process_id>/data/', views.get_flowchart_data, name='get_flowchart_data'),
    path('api/flujogramas/<int:process_id>/export/<str:format_type>/', views.export_flowchart, name='export_flowchart'),
    path('api/flujogramas/<int:process_id>/duplicate/', views.duplicate_flowchart, name='duplicate_flowchart'),
    path('api/flujogramas/<int:process_id>/delete/', views.delete_flowchart, name='delete_flowchart'),
]