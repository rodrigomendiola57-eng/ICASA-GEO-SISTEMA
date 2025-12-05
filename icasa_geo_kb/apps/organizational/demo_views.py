"""
Vistas de demostración para el módulo organizacional
Usan datos en memoria para mostrar la funcionalidad sin base de datos
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json

# Datos de demostración en memoria
DEMO_CHARTS = [
    {
        'id': 1,
        'name': 'Organigrama Administrativo',
        'department': 'Administrativo',
        'description': 'Estructura organizacional del área administrativa de ICASA',
        'status': 'active',
        'is_external': False,
        'created_at': datetime.now() - timedelta(days=5),
        'updated_at': datetime.now() - timedelta(days=1),
        'created_by': 'Admin ICASA'
    },
    {
        'id': 2,
        'name': 'Organigrama Comercial',
        'department': 'Comercial',
        'description': 'Estructura organizacional del área comercial de ICASA',
        'status': 'active',
        'is_external': False,
        'created_at': datetime.now() - timedelta(days=10),
        'updated_at': datetime.now() - timedelta(days=2),
        'created_by': 'Admin ICASA'
    },
    {
        'id': 3,
        'name': 'Organigrama Operaciones',
        'department': 'Operaciones',
        'description': 'Estructura organizacional del área de operaciones',
        'status': 'draft',
        'is_external': True,
        'created_at': datetime.now() - timedelta(days=3),
        'updated_at': datetime.now(),
        'created_by': 'Gerente Operaciones'
    }
]

@login_required
def demo_dashboard(request):
    """Dashboard de demostración con datos en memoria"""
    
    # Agrupar por departamento
    charts_by_department = {}
    for chart in DEMO_CHARTS:
        dept = chart['department']
        if dept not in charts_by_department:
            charts_by_department[dept] = []
        charts_by_department[dept].append(chart)
    
    # Estadísticas
    total_charts = len(DEMO_CHARTS)
    active_charts = len([c for c in DEMO_CHARTS if c['status'] == 'active'])
    departments_with_charts = len(charts_by_department.keys())
    
    context = {
        'charts_by_department': charts_by_department,
        'total_charts': total_charts,
        'active_charts': active_charts,
        'departments_with_charts': departments_with_charts,
        'available_departments': [
            'Administrativo', 'Comercial', 'Operaciones', 
            'RRHH', 'Finanzas', 'Mantenimiento'
        ]
    }
    
    return render(request, 'organizational/demo_dashboard.html', context)

@login_required
@csrf_exempt
def demo_create_chart(request):
    """API de demostración para crear organigrama"""
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        description = request.POST.get('description', '')
        
        if not name or not department:
            return JsonResponse({
                'success': False,
                'error': 'Nombre y departamento son obligatorios'
            })
        
        # Simular creación
        new_chart = {
            'id': len(DEMO_CHARTS) + 1,
            'name': name,
            'department': department,
            'description': description,
            'status': 'draft',
            'is_external': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': request.user.get_full_name() or request.user.username
        }
        
        DEMO_CHARTS.append(new_chart)
        
        return JsonResponse({
            'success': True,
            'message': f'Organigrama "{name}" creado exitosamente',
            'chart_id': new_chart['id']
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def demo_upload_chart(request):
    """API de demostración para subir archivo"""
    if request.method == 'POST':
        department = request.POST.get('department')
        chart_file = request.FILES.get('chart_file')
        
        if not department or not chart_file:
            return JsonResponse({
                'success': False,
                'error': 'Departamento y archivo son obligatorios'
            })
        
        # Validar tipo de archivo
        allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx']
        file_extension = chart_file.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de archivo no permitido. Permitidos: {", ".join(allowed_extensions)}'
            })
        
        # Simular subida
        new_chart = {
            'id': len(DEMO_CHARTS) + 1,
            'name': f'Organigrama {department} - {chart_file.name}',
            'department': department,
            'description': f'Archivo subido: {chart_file.name}',
            'status': 'active',
            'is_external': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': request.user.get_full_name() or request.user.username,
            'file_name': chart_file.name,
            'file_size': chart_file.size
        }
        
        DEMO_CHARTS.append(new_chart)
        
        return JsonResponse({
            'success': True,
            'message': f'Archivo "{chart_file.name}" subido exitosamente para {department}',
            'chart_id': new_chart['id']
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def demo_get_charts_api(request):
    """API para obtener organigramas"""
    department = request.GET.get('department')
    
    charts = DEMO_CHARTS
    if department:
        charts = [c for c in charts if c['department'] == department]
    
    charts_data = []
    for chart in charts:
        charts_data.append({
            'id': chart['id'],
            'name': chart['name'],
            'department': chart['department'],
            'status': chart['status'],
            'is_external': chart['is_external'],
            'created_at': chart['created_at'].strftime('%Y-%m-%d'),
            'updated_at': chart['updated_at'].strftime('%Y-%m-%d'),
            'created_by': chart['created_by']
        })
    
    return JsonResponse({
        'success': True,
        'charts': charts_data
    })

@login_required
def demo_chart_detail(request, chart_id):
    """Vista de detalle de organigrama de demostración"""
    
    # Buscar chart por ID
    chart = None
    for c in DEMO_CHARTS:
        if c['id'] == chart_id:
            chart = c
            break
    
    if not chart:
        return render(request, '404.html', status=404)
    
    # Simular métodos del modelo
    chart['get_status_display'] = {
        'active': 'Activo',
        'draft': 'Borrador',
        'archived': 'Archivado'
    }.get(chart['status'], 'Desconocido')
    
    chart['get_file_extension'] = lambda: chart.get('file_name', '').split('.')[-1].lower() if chart.get('file_name') else None
    chart['is_image'] = lambda: chart['get_file_extension']() in ['png', 'jpg', 'jpeg', 'gif', 'svg'] if chart['get_file_extension']() else False
    chart['is_pdf'] = lambda: chart['get_file_extension']() == 'pdf' if chart['get_file_extension']() else False
    
    context = {
        'chart': chart
    }
    
    return render(request, 'organizational/demo_chart_detail.html', context)

@login_required
@csrf_exempt
def demo_delete_chart(request, chart_id):
    """API para eliminar organigrama de demostración"""
    if request.method == 'POST':
        global DEMO_CHARTS
        
        # Buscar y eliminar chart
        chart_to_delete = None
        for i, chart in enumerate(DEMO_CHARTS):
            if chart['id'] == chart_id:
                chart_to_delete = DEMO_CHARTS.pop(i)
                break
        
        if chart_to_delete:
            return JsonResponse({
                'success': True,
                'message': f'Organigrama "{chart_to_delete["name"]}" eliminado exitosamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Organigrama no encontrado'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)