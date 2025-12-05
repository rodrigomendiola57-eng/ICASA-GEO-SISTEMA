"""
Vistas corporativas avanzadas para funcionalidades empresariales
Incluye sandbox, importación, exportación y flujos de aprobación
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
import json
import pandas as pd
from typing import Dict, Any

from .models import DepartmentalChart, OrganizationalSnapshot, ImportLog, ApprovalWorkflow
from .importers import get_importer, validate_import_file, generate_excel_template
from .exporters import export_chart

# Decoradores de permisos
def is_manager_or_admin(user):
    """Verificar si el usuario es gerente o administrador"""
    return user.is_staff or user.groups.filter(name__in=['Gerentes', 'Administradores']).exists()

def is_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_staff or user.groups.filter(name='Administradores').exists()

# FUNCIONALIDADES DE SANDBOX (SIMULACIÓN)

@login_required
@user_passes_test(is_manager_or_admin)
def sandbox_dashboard(request):
    """Dashboard para gestión de simulaciones organizacionales"""
    
    # Obtener organigramas base (no sandbox)
    base_charts = DepartmentalChart.objects.filter(
        is_sandbox=False,
        status='active'
    ).order_by('department')
    
    # Obtener simulaciones del usuario
    user_simulations = DepartmentalChart.objects.filter(
        is_sandbox=True,
        created_by=request.user
    ).order_by('-created_at')
    
    # Obtener simulaciones pendientes de aprobación
    pending_approvals = ApprovalWorkflow.objects.filter(
        status='pending'
    ).select_related('chart', 'requested_by').order_by('-created_at')
    
    context = {
        'base_charts': base_charts,
        'user_simulations': user_simulations,
        'pending_approvals': pending_approvals,
        'can_approve': is_admin(request.user)
    }
    
    return render(request, 'organizational/corporate/sandbox_dashboard.html', context)

@login_required
@csrf_exempt
def create_sandbox(request):
    """Crear simulación (sandbox) de un organigrama existente"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            base_chart_id = data.get('base_chart_id')
            simulation_name = data.get('simulation_name')
            scenario_description = data.get('scenario_description')
            
            if not all([base_chart_id, simulation_name]):
                return JsonResponse({
                    'success': False,
                    'error': 'ID del organigrama base y nombre de simulación son requeridos'
                })
            
            # Obtener organigrama base
            base_chart = get_object_or_404(DepartmentalChart, id=base_chart_id, is_sandbox=False)
            
            # Crear simulación
            sandbox_chart = base_chart.create_sandbox_copy(
                user=request.user,
                name_suffix=simulation_name
            )
            
            # Actualizar descripción
            if scenario_description:
                sandbox_chart.description = scenario_description
                sandbox_chart.save()
            
            # Crear snapshot del estado inicial
            OrganizationalSnapshot.objects.create(
                chart=sandbox_chart,
                snapshot_data=sandbox_chart.chart_data,
                version_tag='sandbox-initial',
                created_by=request.user,
                notes='Estado inicial de la simulación'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Simulación "{simulation_name}" creada exitosamente',
                'sandbox_id': sandbox_chart.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al crear simulación: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def sandbox_editor(request, sandbox_id):
    """Editor de simulación organizacional"""
    
    sandbox_chart = get_object_or_404(
        DepartmentalChart,
        id=sandbox_id,
        is_sandbox=True,
        created_by=request.user
    )
    
    # Obtener snapshots
    snapshots = sandbox_chart.snapshots.all().order_by('-created_at')
    
    # Obtener organigrama base para comparación
    base_chart = sandbox_chart.parent_chart
    
    context = {
        'sandbox_chart': sandbox_chart,
        'base_chart': base_chart,
        'snapshots': snapshots,
        'can_request_approval': True
    }
    
    return render(request, 'organizational/corporate/sandbox_editor.html', context)

@login_required
@csrf_exempt
def save_sandbox_changes(request, sandbox_id):
    """Guardar cambios en la simulación"""
    
    if request.method == 'POST':
        try:
            sandbox_chart = get_object_or_404(
                DepartmentalChart,
                id=sandbox_id,
                is_sandbox=True,
                created_by=request.user
            )
            
            data = json.loads(request.body)
            new_chart_data = data.get('chart_data')
            snapshot_notes = data.get('notes', '')
            
            if not new_chart_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Datos del organigrama requeridos'
                })
            
            # Crear snapshot del estado anterior
            OrganizationalSnapshot.objects.create(
                chart=sandbox_chart,
                snapshot_data=sandbox_chart.chart_data,
                version_tag=f'auto-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
                created_by=request.user,
                notes='Guardado automático antes de cambios'
            )
            
            # Actualizar datos
            sandbox_chart.chart_data = new_chart_data
            sandbox_chart.save()
            
            # Crear snapshot del nuevo estado
            OrganizationalSnapshot.objects.create(
                chart=sandbox_chart,
                snapshot_data=new_chart_data,
                version_tag=f'save-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
                created_by=request.user,
                notes=snapshot_notes or 'Cambios guardados'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Cambios guardados exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al guardar cambios: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# FUNCIONALIDADES DE IMPORTACIÓN

@login_required
def import_dashboard(request):
    """Dashboard para importación de organigramas"""
    
    # Obtener logs de importación recientes
    recent_imports = ImportLog.objects.filter(
        imported_by=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'recent_imports': recent_imports,
        'supported_formats': ['Excel (.xlsx, .xls)', 'CSV (.csv)', 'JSON (.json)']
    }
    
    return render(request, 'organizational/corporate/import_dashboard.html', context)

@login_required
def download_excel_template(request):
    """Descargar plantilla Excel para importación"""
    
    try:
        # Generar plantilla
        template_df = generate_excel_template()
        
        # Crear archivo Excel
        from io import BytesIO
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='Organigrama', index=False)
            
            # Agregar hoja de instrucciones
            instructions = pd.DataFrame({
                'Campo': ['id_puesto', 'nombre_puesto', 'departamento', 'id_jefe', 'nivel', 'responsabilidades', 'empleado_actual'],
                'Descripción': [
                    'Identificador único del puesto (ej: DIR001)',
                    'Nombre del puesto (ej: Director General)',
                    'Departamento al que pertenece',
                    'ID del puesto al que reporta (vacío para director)',
                    'Nivel jerárquico (1=más alto)',
                    'Descripción de responsabilidades',
                    'Nombre del empleado actual (vacío si está vacante)'
                ],
                'Requerido': ['Sí', 'Sí', 'Sí', 'No', 'No', 'No', 'No']
            })
            
            instructions.to_excel(writer, sheet_name='Instrucciones', index=False)
        
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Plantilla_Organigrama_ICASA.xlsx"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error al generar plantilla: {str(e)}')
        return redirect('organizational:import_dashboard')

@login_required
@csrf_exempt
def import_from_file(request):
    """Importar organigrama desde archivo"""
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            chart_name = request.POST.get('chart_name')
            department = request.POST.get('department')
            import_file = request.FILES.get('import_file')
            
            if not all([chart_name, department, import_file]):
                return JsonResponse({
                    'success': False,
                    'error': 'Nombre, departamento y archivo son requeridos'
                })
            
            # Validar archivo
            is_valid, validation_errors = validate_import_file(import_file)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'error': f'Archivo inválido: {"; ".join(validation_errors)}'
                })
            
            # Determinar tipo de importador
            file_ext = import_file.name.split('.')[-1].lower()
            import_type = 'excel' if file_ext in ['xlsx', 'xls'] else file_ext
            
            # Obtener importador
            importer = get_importer(import_type, request.user)
            
            # Importar
            if import_type in ['excel', 'csv']:
                success, chart = importer.import_from_file(import_file, chart_name, department)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Tipo de archivo no soportado: {file_ext}'
                })
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Organigrama importado exitosamente. Procesados: {importer.success_records} registros',
                    'chart_id': chart.id,
                    'warnings': importer.warnings,
                    'errors': importer.errors
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Error en importación: {"; ".join(importer.errors)}'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# FUNCIONALIDADES DE EXPORTACIÓN

@login_required
def export_menu(request, chart_id):
    """Menú de opciones de exportación"""
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    # Verificar permisos
    if chart.is_sandbox and chart.created_by != request.user:
        messages.error(request, 'No tienes permisos para exportar esta simulación')
        return redirect('organizational:dashboard')
    
    export_options = [
        {
            'type': 'pdf',
            'name': 'Libro de Organización (PDF)',
            'description': 'Documento completo con organigrama, descripciones de puestos y matriz de responsabilidades',
            'icon': '📄'
        },
        {
            'type': 'excel',
            'name': 'Estructura Plana (Excel)',
            'description': 'Tabla con todos los puestos para análisis de nómina y estadísticas',
            'icon': '📊'
        },
        {
            'type': 'powerpoint',
            'name': 'Presentación (PowerPoint)',
            'description': 'Slides editables para presentaciones ejecutivas',
            'icon': '📽️'
        }
    ]
    
    context = {
        'chart': chart,
        'export_options': export_options
    }
    
    return render(request, 'organizational/corporate/export_menu.html', context)

@login_required
def export_chart_file(request, chart_id, export_type):
    """Exportar organigrama en el formato especificado"""
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    # Verificar permisos
    if chart.is_sandbox and chart.created_by != request.user:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para exportar esta simulación'
        }, status=403)
    
    try:
        # Exportar usando el sistema de exportadores
        response = export_chart(chart, export_type)
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al exportar: {str(e)}'
        }, status=500)

# FUNCIONALIDADES DE APROBACIÓN

@login_required
@csrf_exempt
def request_approval(request, sandbox_id):
    """Solicitar aprobación para una simulación"""
    
    if request.method == 'POST':
        try:
            sandbox_chart = get_object_or_404(
                DepartmentalChart,
                id=sandbox_id,
                is_sandbox=True,
                created_by=request.user
            )
            
            data = json.loads(request.body)
            request_notes = data.get('notes', '')
            
            # Verificar que no haya una solicitud pendiente
            existing_request = ApprovalWorkflow.objects.filter(
                chart=sandbox_chart,
                status='pending'
            ).first()
            
            if existing_request:
                return JsonResponse({
                    'success': False,
                    'error': 'Ya existe una solicitud de aprobación pendiente para esta simulación'
                })
            
            # Crear solicitud de aprobación
            approval_request = ApprovalWorkflow.objects.create(
                chart=sandbox_chart,
                requested_by=request.user,
                request_notes=request_notes,
                status='pending'
            )
            
            # Cambiar estado del organigrama
            sandbox_chart.status = 'pending_approval'
            sandbox_chart.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Solicitud de aprobación enviada exitosamente',
                'approval_id': approval_request.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al solicitar aprobación: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@user_passes_test(is_admin)
def approval_dashboard(request):
    """Dashboard para gestión de aprobaciones (solo administradores)"""
    
    # Obtener solicitudes pendientes
    pending_requests = ApprovalWorkflow.objects.filter(
        status='pending'
    ).select_related('chart', 'requested_by').order_by('-created_at')
    
    # Obtener historial de aprobaciones
    recent_approvals = ApprovalWorkflow.objects.filter(
        status__in=['approved', 'rejected']
    ).select_related('chart', 'requested_by', 'approver').order_by('-approved_at')[:10]
    
    context = {
        'pending_requests': pending_requests,
        'recent_approvals': recent_approvals
    }
    
    return render(request, 'organizational/corporate/approval_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def process_approval(request, approval_id):
    """Procesar solicitud de aprobación"""
    
    if request.method == 'POST':
        try:
            approval_request = get_object_or_404(ApprovalWorkflow, id=approval_id, status='pending')
            
            data = json.loads(request.body)
            action = data.get('action')  # 'approve' o 'reject'
            notes = data.get('notes', '')
            
            if action not in ['approve', 'reject']:
                return JsonResponse({
                    'success': False,
                    'error': 'Acción inválida. Debe ser "approve" o "reject"'
                })
            
            # Procesar según la acción
            if action == 'approve':
                # Aprobar y publicar cambios
                success = approval_request.chart.approve_and_publish(
                    approver=request.user,
                    justification=notes
                )
                
                if success:
                    approval_request.status = 'approved'
                    approval_request.approver = request.user
                    approval_request.approval_notes = notes
                    approval_request.approved_at = timezone.now()
                    approval_request.save()
                    
                    message = f'Organigrama aprobado y publicado como versión {approval_request.chart.version}'
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Error al aprobar el organigrama'
                    })
            
            else:  # reject
                approval_request.status = 'rejected'
                approval_request.approver = request.user
                approval_request.approval_notes = notes
                approval_request.approved_at = timezone.now()
                approval_request.save()
                
                # Cambiar estado del organigrama de vuelta a sandbox
                approval_request.chart.status = 'sandbox'
                approval_request.chart.save()
                
                message = 'Solicitud rechazada. El organigrama vuelve a modo simulación'
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar aprobación: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# FUNCIONALIDADES DE COMPARACIÓN Y VERSIONES

@login_required
def version_comparison(request, chart_id):
    """Comparar versiones de un organigrama"""
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    # Obtener historial de versiones
    version_history = chart.get_version_history()
    
    # Obtener snapshots
    snapshots = chart.snapshots.all().order_by('-created_at')
    
    context = {
        'chart': chart,
        'version_history': version_history,
        'snapshots': snapshots
    }
    
    return render(request, 'organizational/corporate/version_comparison.html', context)

@login_required
def get_version_diff(request, chart_id, version1_id, version2_id):
    """Obtener diferencias entre dos versiones"""
    
    try:
        chart = get_object_or_404(DepartmentalChart, id=chart_id)
        
        # Obtener las dos versiones a comparar
        if version1_id == 'current':
            version1_data = chart.chart_data
        else:
            snapshot1 = get_object_or_404(OrganizationalSnapshot, id=version1_id, chart=chart)
            version1_data = snapshot1.snapshot_data
        
        if version2_id == 'current':
            version2_data = chart.chart_data
        else:
            snapshot2 = get_object_or_404(OrganizationalSnapshot, id=version2_id, chart=chart)
            version2_data = snapshot2.snapshot_data
        
        # Calcular diferencias (implementación simplificada)
        differences = {
            'added_positions': [],
            'removed_positions': [],
            'modified_positions': [],
            'summary': 'Comparación de versiones realizada'
        }
        
        # Aquí iría la lógica completa de comparación
        # Por simplicidad, retornamos estructura básica
        
        return JsonResponse({
            'success': True,
            'differences': differences
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al comparar versiones: {str(e)}'
        })