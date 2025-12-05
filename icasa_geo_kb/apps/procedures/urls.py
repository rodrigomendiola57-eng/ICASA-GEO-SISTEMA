from django.urls import path
from . import views

app_name = 'procedures'

urlpatterns = [
    # Dashboard
    path('', views.procedures_dashboard, name='dashboard'),
    
    # CRUD Procedimientos
    path('lista/', views.procedure_list, name='procedure_list'),
    path('crear/', views.procedure_create, name='procedure_create'),
    path('<int:pk>/', views.procedure_detail, name='procedure_detail'),
    path('<int:pk>/editar/', views.procedure_edit, name='procedure_edit'),
    path('<int:pk>/eliminar/', views.procedure_delete, name='procedure_delete'),
    
    # API
    path('api/template/<int:template_id>/', views.get_template_data, name='get_template_data'),
]