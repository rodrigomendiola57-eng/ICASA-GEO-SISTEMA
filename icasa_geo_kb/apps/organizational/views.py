from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import json
# Importar modelos organizacionales
from .models import (
    OrganizationalChart, Position, ProcessFlow, Employee, PositionAssignment,
    JobProfile, Skill, EmployeeSkill, Committee, CommitteeMembership, DepartmentalChart,
    ProcessCategory, FlowchartProcess, FlowchartTemplate
)


def calculate_hierarchical_positions():
    """Organigrama con posiciones fijas y muy espaciadas"""
    positions = Position.objects.all().order_by('level', 'title')
    position_map = {}
    
    # Posiciones fijas predefinidas por nivel
    level_positions = {
        1: [(1000, 200)],  # Director General
        2: [(400, 800), (800, 800), (1200, 800), (1600, 800)],  # Gerentes
        3: [(200, 1400), (600, 1400), (1000, 1400), (1400, 1400), (1800, 1400)]  # Jefes
    }
    
    # Agrupar por nivel
    by_level = {}
    for pos in positions:
        if pos.level not in by_level:
            by_level[pos.level] = []
        by_level[pos.level].append(pos)
    
    # Asignar posiciones fijas
    for level, positions_list in by_level.items():
        if level in level_positions:
            coords = level_positions[level]
            for i, pos in enumerate(positions_list):
                if i < len(coords):
                    x, y = coords[i]
                    position_map[pos.id] = {'x': x, 'y': y}
                else:
                    # Si hay más posiciones que coordenadas, usar espaciado
                    x = 200 + (i * 400)
                    y = 200 + (level - 1) * 600
                    position_map[pos.id] = {'x': x, 'y': y}
    
    return position_map

@login_required
def organizational_dashboard(request):
    """Página principal - Galería de organigramas por departamento"""
    
    # Obtener solo la versión activa de cada departamento
    active_charts = DepartmentalChart.objects.filter(status='active').order_by('department', '-updated_at')
    
    # Obtener solo un organigrama por departamento (el activo)
    charts_by_department = {}
    department_charts = []
    
    for chart in active_charts:
        dept = chart.department
        if dept not in charts_by_department:
            charts_by_department[dept] = chart
            department_charts.append(chart)
    
    # Estadísticas
    total_versions = DepartmentalChart.objects.count()
    active_charts_count = len(department_charts)
    departments_with_charts = len(charts_by_department.keys())
    
    # Departamentos disponibles
    available_departments = [
        'Administrativo', 'Comercial', 'Operaciones', 
        'RRHH', 'Finanzas', 'Mantenimiento', 'Dirección'
    ]
    
    context = {
        'charts': department_charts,  # Solo un organigrama por departamento
        'charts_by_department': charts_by_department,
        'total_charts': total_versions,
        'active_charts': active_charts_count,
        'departments_with_charts': departments_with_charts,
        'available_departments': available_departments,
        'can_create': request.user.has_perm('organizational.add_departmentalchart'),
        'can_edit': request.user.has_perm('organizational.change_departmentalchart'),
    }
    
    return render(request, 'organizational/dashboard.html', context)

@login_required
def interactive_organigram(request):
    """Organigrama Interactivo Moderno"""
    from django.utils import timezone
    from datetime import datetime
    
    # Verificar si existen datos
    try:
        positions_exist = Position.objects.exists()
        if not positions_exist:
            context = {
                'error_message': 'No hay posiciones organizacionales creadas. Crea algunas posiciones desde el admin.',
                'show_create_button': True
            }
            return render(request, 'organizational/interactive_organigram.html', context)
    except Exception as e:
        context = {
            'error_message': f'Error en la base de datos: {str(e)}. Ejecuta las migraciones.',
            'show_create_button': False
        }
        return render(request, 'organizational/interactive_organigram.html', context)
    
    # Obtener estadísticas básicas
    total_positions = Position.objects.count()
    filled_positions = Position.objects.filter(assignments__end_date__isnull=True).distinct().count()
    vacant_count = total_positions - filled_positions
    fill_rate = (filled_positions / total_positions * 100) if total_positions > 0 else 0
    departments = Position.objects.values_list('department', flat=True).distinct()
    
    context = {
        'total_positions': total_positions,
        'filled_positions': filled_positions,
        'vacant_count': vacant_count,
        'fill_rate': round(fill_rate, 1),
        'departments': list(departments),
        'can_edit': request.user.is_staff
    }
    
    return render(request, 'organizational/interactive_organigram.html', context)
    
    # PASO C: Lógica de "Acéfalos" (Alerta Roja)
    org_data = []
    vacant_count = 0
    
    # Calcular posiciones jerárquicas si no están definidas manualmente
    hierarchical_positions = calculate_hierarchical_positions()
    
    for position in positions:
        # Obtener empleado actual para esta posición
        employee = position.get_current_employee(view_date)
        is_vacant = position.is_vacant(view_date)
        
        if is_vacant:
            vacant_count += 1
        
        # Usar posición manual si existe, sino usar la calculada
        if position.x_position and position.y_position:
            x_pos = position.x_position
            y_pos = position.y_position
        else:
            pos_data = hierarchical_positions.get(position.id, {'x': 500, 'y': 100})
            x_pos = pos_data['x']
            y_pos = pos_data['y']
        
        org_data.append({
            'id': position.id,
            'title': position.title,
            'department': position.department,
            'level': position.level,
            'reports_to': position.reports_to.id if position.reports_to else None,
            'employee': {
                'name': f"{employee.first_name} {employee.last_name}" if employee else None,
                'photo': employee.photo.url if employee and employee.photo else None,
                'employee_id': employee.employee_id if employee else None
            } if employee else None,
            'is_vacant': is_vacant,
            'x_position': x_pos,
            'y_position': y_pos,
            'kpis': position.kpis or [],
            'processes': position.required_processes or []
        })
    
    # Estadísticas
    total_positions = positions.count()
    filled_positions = total_positions - vacant_count
    
    # Obtener departamentos únicos para el filtro
    departments = Position.objects.values_list('department', flat=True).distinct().order_by('department')
    
    context = {
        'org_data': org_data,
        'view_date': view_date,
        'selected_date': selected_date or view_date.strftime('%Y-%m-%d'),
        'vacant_count': vacant_count,
        'total_positions': total_positions,
        'filled_positions': filled_positions,
        'fill_rate': round((filled_positions / total_positions * 100), 1) if total_positions > 0 else 0,
        'departments': departments
    }
    return render(request, 'organizational/interactive_organigram.html', context)

@login_required
def chart_list(request):
    """Lista de organigramas"""
    charts = OrganizationalChart.objects.all().order_by('-created_at')
    return render(request, 'organizational/chart_list.html', {'charts': charts})

@login_required
def chart_detail(request, pk):
    """Detalle de organigrama"""
    chart = get_object_or_404(OrganizationalChart, pk=pk)
    return render(request, 'organizational/chart_detail.html', {'chart': chart})

@login_required
def position_detail_api(request, position_id):
    """PASO D: API para Panel Lateral con información del puesto"""
    try:
        position = get_object_or_404(Position, id=position_id)
        
        # Fecha para consulta
        selected_date = request.GET.get('date')
        if selected_date:
            try:
                view_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                view_date = timezone.now().date()
        else:
            view_date = timezone.now().date()
        
        # Empleado actual
        current_employee = position.get_current_employee(view_date)
        
        data = {
            'position': {
                'id': position.id,
                'title': position.title,
                'department': position.department,
                'level': position.level,
                'responsibilities': position.responsibilities or 'No definidas',
                'kpis': position.kpis or [],
                'required_processes': position.required_processes or []
            },
            'current_employee': {
                'name': f"{current_employee.first_name} {current_employee.last_name}",
                'employee_id': current_employee.employee_id,
                'email': current_employee.email,
                'phone': current_employee.phone or 'No disponible',
                'photo': current_employee.photo.url if current_employee.photo else None,
                'hire_date': current_employee.hire_date.strftime('%Y-%m-%d')
            } if current_employee else None,
            'is_vacant': position.is_vacant(view_date),
            'assignments_history': []
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def position_list(request):
    """Lista de puestos"""
    positions = Position.objects.all().order_by('department', 'title')
    return render(request, 'organizational/position_list.html', {'positions': positions})

# 2. 📋 PERFILES DE PUESTO
@login_required
def job_profiles_list(request):
    """Lista de perfiles de puesto"""
    profiles = JobProfile.objects.select_related('position').all()
    return render(request, 'organizational/job_profiles.html', {'profiles': profiles})

@login_required
def job_profile_detail(request, profile_id):
    """Detalle del perfil de puesto con opción de generar PDF"""
    profile = get_object_or_404(JobProfile, id=profile_id)
    return render(request, 'organizational/job_profile_detail.html', {'profile': profile})

# 3. 🎯 MATRIZ DE COMPETENCIAS
@login_required
def competency_matrix(request):
    """Matriz de competencias: Empleados vs Habilidades"""
    employees = Employee.objects.filter(is_active=True)
    skills = Skill.objects.all().order_by('category', 'name')
    
    # Crear matriz
    matrix_data = []
    for employee in employees:
        employee_skills = {}
        for skill in skills:
            try:
                emp_skill = EmployeeSkill.objects.get(employee=employee, skill=skill)
                employee_skills[skill.id] = {
                    'level': emp_skill.level,
                    'status': emp_skill.status,
                    'color': {
                        'certified': 'green',
                        'training': 'yellow', 
                        'needs_training': 'red',
                        'expired': 'gray'
                    }.get(emp_skill.status, 'gray')
                }
            except EmployeeSkill.DoesNotExist:
                employee_skills[skill.id] = {'level': 0, 'status': 'not_assigned', 'color': 'white'}
        
        matrix_data.append({
            'employee': employee,
            'skills': employee_skills
        })
    
    context = {
        'matrix_data': matrix_data,
        'skills': skills,
        'skill_categories': Skill.objects.values_list('category', flat=True).distinct()
    }
    return render(request, 'organizational/competency_matrix.html', context)

# 4. 🤝 COMITÉS Y GRUPOS
@login_required
def committees_list(request):
    """Lista de comités y grupos"""
    committees = Committee.objects.filter(is_active=True).prefetch_related('members')
    return render(request, 'organizational/committees.html', {'committees': committees})

@login_required
def committee_detail(request, committee_id):
    """Detalle del comité con miembros actuales"""
    committee = get_object_or_404(Committee, id=committee_id)
    current_members = CommitteeMembership.objects.filter(
        committee=committee,
        end_date__isnull=True
    ).select_related('employee')
    
    context = {
        'committee': committee,
        'current_members': current_members
    }
    return render(request, 'organizational/committee_detail.html', context)

@login_required
def flow_list(request):
    """Dashboard guiado de flujogramas"""
    try:
        # Obtener estadísticas
        total_flows = FlowchartProcess.objects.filter(owner=request.user).count()
        published_flows = FlowchartProcess.objects.filter(owner=request.user, status='published').count()
        draft_flows = FlowchartProcess.objects.filter(owner=request.user, status='draft').count()
        pending_review = FlowchartProcess.objects.filter(owner=request.user, status='review').count()
        
        # Plantillas populares
        popular_templates = FlowchartTemplate.objects.filter(is_active=True).order_by('-usage_count')[:8]
        
        # Agregar colores y categorías a las plantillas
        for template in popular_templates:
            if template.category == 'hr':
                template.category_color = 'green'
                template.icon = 'fas fa-user-plus'
            elif template.category == 'finance':
                template.category_color = 'blue'
                template.icon = 'fas fa-dollar-sign'
            elif template.category == 'operations':
                template.category_color = 'orange'
                template.icon = 'fas fa-cogs'
            elif template.category == 'audit':
                template.category_color = 'red'
                template.icon = 'fas fa-search'
            else:
                template.category_color = 'gray'
                template.icon = 'fas fa-sitemap'
        
        # Procesos recientes del usuario organizados por departamento
        recent_flows = FlowchartProcess.objects.filter(owner=request.user).select_related('category').order_by('-updated_at')[:10]
        
        # Agregar colores de estado y organizar por departamento
        flows_by_department = {}
        for flow in recent_flows:
            if flow.status == 'published':
                flow.status_color = 'green'
            elif flow.status == 'draft':
                flow.status_color = 'gray'
            elif flow.status == 'review':
                flow.status_color = 'yellow'
            else:
                flow.status_color = 'blue'
            
            # Organizar por departamento
            dept = flow.responsible_department or 'Sin Departamento'
            if dept not in flows_by_department:
                flows_by_department[dept] = []
            flows_by_department[dept].append(flow)
        
        # Colaboradores únicos
        collaborators = FlowchartProcess.objects.filter(owner=request.user).values('owner').distinct().count()
        
        # Estadísticas por departamento
        department_stats = {}
        departments = ['Dirección General', 'Administrativo', 'Comercial', 'Operaciones', 'RRHH', 'Finanzas', 'Mantenimiento', 'Sistemas', 'Calidad', 'Seguridad', 'Logística', 'Compras', 'Legal']
        for dept in departments:
            dept_flows = FlowchartProcess.objects.filter(owner=request.user, responsible_department=dept)
            count = dept_flows.count()
            if count > 0:  # Solo mostrar departamentos con procesos
                department_stats[dept] = {
                    'total': count,
                    'published': dept_flows.filter(status='published').count(),
                    'draft': dept_flows.filter(status='draft').count()
                }
        
        context = {
            'total_flows': total_flows,
            'published_flows': published_flows,
            'draft_flows': draft_flows,
            'pending_review': pending_review,
            'collaborators': collaborators,
            'popular_templates': popular_templates,
            'recent_flows': recent_flows,
            'flows': recent_flows,  # Para compatibilidad
            'flows_by_department': flows_by_department,
            'department_stats': department_stats,
        }
        
        return render(request, 'organizational/flowcharts_dashboard.html', context)
        
    except Exception as e:
        # En caso de error, mostrar dashboard básico
        context = {
            'total_flows': 0,
            'published_flows': 0,
            'draft_flows': 0,
            'pending_review': 0,
            'collaborators': 0,
            'popular_templates': [],
            'recent_flows': [],
            'flows': [],
            'flows_by_department': {},
            'department_stats': {},
            'error_message': f'Error al cargar datos: {str(e)}'
        }
        return render(request, 'organizational/flowcharts_dashboard.html', context)

@login_required
def flowchart_editor(request, process_id=None):
    """Editor de fluogramas con Mermaid Chart"""
    process = None
    if process_id:
        process = get_object_or_404(FlowchartProcess, id=process_id)
    
    # Obtener categorías y templates para el editor
    categories = ProcessCategory.objects.all()
    templates = FlowchartTemplate.objects.filter(is_active=True)
    
    context = {
        'process': process,
        'categories': categories,
        'templates': templates,
        'departments': [
            ('Dirección General', 'Dirección General'),
            ('Administrativo', 'Administrativo'),
            ('Comercial', 'Comercial'),
            ('Operaciones', 'Operaciones'),
            ('RRHH', 'Recursos Humanos'),
            ('Finanzas', 'Finanzas'),
            ('Mantenimiento', 'Mantenimiento'),
            ('Sistemas', 'Sistemas'),
            ('Calidad', 'Calidad'),
            ('Seguridad', 'Seguridad'),
            ('Logística', 'Logística'),
            ('Compras', 'Compras'),
            ('Legal', 'Legal'),
        ]
    }
    
    return render(request, 'organizational/flowchart_editor.html', context)

@login_required
@csrf_exempt
def save_flowchart(request):
    """Guardar o actualizar un flujo de trabajo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar campos obligatorios
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            department = data.get('department', '').strip()
            category_type = data.get('category', '').strip()
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'message': 'El título del proceso es obligatorio'
                })
            
            if not description:
                return JsonResponse({
                    'success': False,
                    'message': 'La descripción del proceso es obligatoria'
                })
            
            if not department:
                return JsonResponse({
                    'success': False,
                    'message': 'El departamento del proceso es obligatorio'
                })
            
            if not category_type:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría del proceso es obligatoria'
                })
            
            # Obtener o crear el proceso
            process_id = data.get('process_id')
            if process_id:
                try:
                    process = FlowchartProcess.objects.get(id=process_id)
                    # Verificar que el usuario sea el propietario
                    if process.owner != request.user and not request.user.is_staff:
                        return JsonResponse({
                            'success': False,
                            'message': 'No tienes permisos para editar este proceso'
                        })
                except FlowchartProcess.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'El proceso no existe'
                    })
            else:
                process = FlowchartProcess()
            
            # Actualizar campos obligatorios
            process.title = title
            process.description = description
            process.responsible_department = department
            process.owner = request.user
            
            # Obtener o crear categoría
            category_mapping = {
                'operational': 'Procesos Operativos',
                'strategic': 'Procesos Estratégicos', 
                'support': 'Procesos de Soporte',
                'audit': 'Procesos de Auditoría',
                'quality': 'Procesos de Calidad',
                'safety': 'Procesos de Seguridad',
                'finance': 'Procesos Financieros',
                'hr': 'Procesos de RRHH',
                'it': 'Procesos de TI',
                'legal': 'Procesos Legales'
            }
            
            category_name = category_mapping.get(category_type, 'Procesos Operativos')
            category, created = ProcessCategory.objects.get_or_create(
                category_type=category_type,
                defaults={
                    'name': category_name,
                    'description': f'Categoría para {category_name.lower()}'
                }
            )
            process.category = category
            
            # Guardar datos del diagrama
            diagram_data = data.get('diagram_data', {})
            process.diagram_data = diagram_data
            
            # Determinar complejidad basada en el código Mermaid
            mermaid_code = diagram_data.get('mermaid_code', '')
            lines = len([line for line in mermaid_code.split('\n') if line.strip()])
            if lines <= 5:
                process.complexity_level = 'simple'
            elif lines <= 15:
                process.complexity_level = 'medium'
            else:
                process.complexity_level = 'complex'
            
            process.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Proceso "{title}" guardado exitosamente en {department}',
                'process_id': process.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def get_flowchart_data(request, process_id):
    """Obtener datos de un flujo específico para el editor"""
    try:
        process = FlowchartProcess.objects.select_related('category').get(id=process_id)
        
        data = {
            'id': process.id,
            'title': process.title,
            'description': process.description,
            'category': process.category.name if process.category else '',
            'department': process.responsible_department,
            'diagram_data': process.diagram_data or {},
            'status': process.status,
            'version': process.version,
            'complexity_level': process.complexity_level,
        }
        
        return JsonResponse(data)
        
    except FlowchartProcess.DoesNotExist:
        return JsonResponse({
            'error': 'Proceso no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos: {str(e)}'
        }, status=500)

@login_required
def export_flowchart(request, process_id, format_type):
    """Exportar flujo en diferentes formatos"""
    try:
        process = FlowchartProcess.objects.get(id=process_id)
        
        if format_type == 'mermaid':
            diagram_data = process.diagram_data or {}
            mermaid_code = diagram_data.get('mermaid_code', '')
            response = JsonResponse({
                'success': True,
                'data': mermaid_code,
                'filename': f'{process.title}.mmd'
            })
            return response
        
        # Para otros formatos (PNG, SVG, PDF) se manejarían aquí
        return JsonResponse({
            'success': False,
            'message': f'Formato {format_type} no soportado aún'
        })
        
    except FlowchartProcess.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Proceso no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al exportar: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
def duplicate_flowchart(request, process_id):
    """Duplicar un proceso existente"""
    if request.method == 'POST':
        try:
            original = get_object_or_404(FlowchartProcess, id=process_id)
            
            # Crear copia
            duplicate = FlowchartProcess.objects.create(
                title=f"{original.title} (Copia)",
                description=original.description,
                category=original.category,
                owner=request.user,
                responsible_department=original.responsible_department,
                complexity_level=original.complexity_level,
                diagram_data=original.diagram_data.copy() if original.diagram_data else {},
                status='draft',
                version='1.0'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Proceso "{original.title}" duplicado exitosamente',
                'new_process_id': duplicate.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al duplicar proceso: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def delete_flowchart(request, process_id):
    """Eliminar un proceso de fluograma"""
    if request.method in ['DELETE', 'POST']:
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Verificar que el proceso existe
                try:
                    process = FlowchartProcess.objects.select_for_update().get(id=process_id)
                except FlowchartProcess.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'El proceso no existe o ya fue eliminado'
                    }, status=404)
                
                # Verificar permisos (solo el propietario o admin puede eliminar)
                if process.owner != request.user and not request.user.is_staff:
                    return JsonResponse({
                        'success': False,
                        'error': 'No tienes permisos para eliminar este proceso'
                    }, status=403)
                
                process_title = process.title
                process_id_to_delete = process.id
                
                # Eliminar el proceso de forma atómica
                process.delete()
                
                # Verificar que realmente se eliminó
                still_exists = FlowchartProcess.objects.filter(id=process_id_to_delete).exists()
                if still_exists:
                    raise Exception("El proceso no se pudo eliminar completamente")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Proceso "{process_title}" eliminado exitosamente',
                    'deleted_id': process_id_to_delete
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar proceso: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# 5. 🏢 ADMINISTRACIÓN DE PUESTOS
@login_required
def position_admin_list(request):
    """Lista administrativa de puestos con todas las funciones CRUD"""
    positions = Position.objects.all().order_by('level', 'department', 'title')
    
    # Agregar información del empleado actual a cada posición
    positions_data = []
    for position in positions:
        current_employee = position.get_current_employee()
        positions_data.append({
            'position': position,
            'current_employee': current_employee,
            'is_vacant': position.is_vacant()
        })
    
    context = {
        'positions_data': positions_data,
        'total_positions': positions.count(),
        'vacant_positions': sum(1 for p in positions if p.is_vacant()),
        'departments': Position.objects.values_list('department', flat=True).distinct().order_by('department')
    }
    return render(request, 'organizational/admin/position_list.html', context)

@login_required
def position_create(request):
    """Crear nuevo puesto"""
    if request.method == 'POST':
        title = request.POST.get('title')
        department = request.POST.get('department')
        level = int(request.POST.get('level', 1))
        reports_to_id = request.POST.get('reports_to')
        responsibilities = request.POST.get('responsibilities', '')
        
        # Validaciones básicas
        if not title or not department:
            messages.error(request, 'El título y departamento son obligatorios')
            return redirect('organizational:position_create')
        
        # Crear posición
        position = Position.objects.create(
            title=title,
            department=department,
            level=level,
            responsibilities=responsibilities
        )
        
        # Asignar jefe si se especificó
        if reports_to_id:
            try:
                reports_to = Position.objects.get(id=reports_to_id)
                position.reports_to = reports_to
                position.save()
            except Position.DoesNotExist:
                pass
        
        messages.success(request, f'Puesto "{title}" creado exitosamente')
        return redirect('organizational:position_admin_list')
    
    # GET: Mostrar formulario
    potential_bosses = Position.objects.all().order_by('level', 'title')
    departments = Position.objects.values_list('department', flat=True).distinct().order_by('department')
    
    context = {
        'potential_bosses': potential_bosses,
        'departments': departments
    }
    return render(request, 'organizational/admin/position_form.html', context)

@login_required
def position_edit(request, pk):
    """Editar puesto existente"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        position.title = request.POST.get('title', position.title)
        position.department = request.POST.get('department', position.department)
        position.level = int(request.POST.get('level', position.level))
        position.responsibilities = request.POST.get('responsibilities', position.responsibilities)
        
        # Actualizar jefe
        reports_to_id = request.POST.get('reports_to')
        if reports_to_id:
            try:
                position.reports_to = Position.objects.get(id=reports_to_id)
            except Position.DoesNotExist:
                position.reports_to = None
        else:
            position.reports_to = None
        
        position.save()
        messages.success(request, f'Puesto "{position.title}" actualizado exitosamente')
        return redirect('organizational:position_admin_list')
    
    # GET: Mostrar formulario con datos actuales
    potential_bosses = Position.objects.exclude(id=position.id).order_by('level', 'title')
    departments = Position.objects.values_list('department', flat=True).distinct().order_by('department')
    
    context = {
        'position': position,
        'potential_bosses': potential_bosses,
        'departments': departments,
        'is_edit': True
    }
    return render(request, 'organizational/admin/position_form.html', context)

@login_required
def position_delete(request, pk):
    """Eliminar puesto"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        title = position.title
        position.delete()
        messages.success(request, f'Puesto "{title}" eliminado exitosamente')
        return redirect('organizational:position_admin_list')
    
    # Verificar si tiene empleados asignados o subordinados
    current_employee = position.get_current_employee()
    subordinates = Position.objects.filter(reports_to=position)
    
    context = {
        'position': position,
        'current_employee': current_employee,
        'subordinates': subordinates,
        'can_delete': not current_employee and not subordinates.exists()
    }
    return render(request, 'organizational/admin/position_delete.html', context)

@login_required
def position_assign_employee(request, pk):
    """Asignar empleado a puesto"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        start_date = request.POST.get('start_date')
        assignment_type = request.POST.get('assignment_type', 'permanent')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Verificar si el empleado ya tiene una asignación activa
            current_position = employee.get_current_position()
            if current_position:
                messages.error(request, f'{employee.first_name} {employee.last_name} ya está asignado al puesto: {current_position.title}')
                return redirect('organizational:position_assign_employee', pk=pk)
            
            # Crear nueva asignación
            assignment = PositionAssignment.objects.create(
                position=position,
                employee=employee,
                start_date=start_date,
                assignment_type=assignment_type
            )
            
            messages.success(request, f'{employee.first_name} {employee.last_name} asignado exitosamente al puesto {position.title}')
            return redirect('organizational:position_admin_list')
            
        except Employee.DoesNotExist:
            messages.error(request, 'Empleado no encontrado')
    
    # GET: Mostrar formulario
    # Solo empleados sin asignación activa
    available_employees = []
    for employee in Employee.objects.filter(is_active=True).order_by('first_name', 'last_name'):
        if not employee.get_current_position():
            available_employees.append(employee)
    
    context = {
        'position': position,
        'available_employees': available_employees
    }
    return render(request, 'organizational/admin/position_assign.html', context)

@login_required
def position_unassign_employee(request, pk):
    """Desasignar empleado de puesto"""
    position = get_object_or_404(Position, pk=pk)
    current_employee = position.get_current_employee()
    
    if not current_employee:
        messages.error(request, 'Este puesto no tiene empleado asignado')
        return redirect('organizational:position_admin_list')
    
    if request.method == 'POST':
        end_date = request.POST.get('end_date')
        notes = request.POST.get('notes', '')
        
        # Finalizar asignación actual
        current_assignment = PositionAssignment.objects.filter(
            position=position,
            employee=current_employee,
            end_date__isnull=True
        ).first()
        
        if current_assignment:
            current_assignment.end_date = end_date
            current_assignment.notes = notes
            current_assignment.save()
            
            messages.success(request, f'{current_employee.first_name} {current_employee.last_name} desasignado del puesto {position.title}')
        
        return redirect('organizational:position_admin_list')
    
    context = {
        'position': position,
        'current_employee': current_employee
    }
    return render(request, 'organizational/admin/position_unassign.html', context)

@csrf_exempt
@login_required
def save_position_coordinates(request):
    """API para guardar coordenadas de posiciones editadas manualmente"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            positions_data = data.get('positions', [])
            
            # Si el array está vacío, resetear todas las posiciones
            if not positions_data:
                Position.objects.all().update(x_position=None, y_position=None)
                return JsonResponse({
                    'success': True, 
                    'message': 'Posiciones reseteadas al layout automático',
                    'reset': True
                })
            
            updated_count = 0
            for pos_data in positions_data:
                try:
                    position = Position.objects.get(id=pos_data['id'])
                    position.x_position = int(pos_data['x'])
                    position.y_position = int(pos_data['y'])
                    position.save()
                    updated_count += 1
                except Position.DoesNotExist:
                    continue
            
            return JsonResponse({
                'success': True, 
                'message': f'Se actualizaron {updated_count} posiciones correctamente',
                'updated_count': updated_count
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# NUEVAS VISTAS PARA ORGANIGRAMAS DEPARTAMENTALES

@login_required
@csrf_exempt
def create_departmental_chart(request):
    """Crear nuevo organigrama departamental"""
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        description = request.POST.get('description', '')
        
        if not name or not department:
            return JsonResponse({
                'success': False, 
                'error': 'Nombre y departamento son obligatorios'
            })
        
        try:
            # Verificar si ya existe un organigrama activo para este departamento
            existing = DepartmentalChart.objects.filter(
                department=department, 
                status='active'
            ).first()
            
            if existing:
                # Archivar el anterior
                existing.status = 'archived'
                existing.save()
            
            # Crear nuevo organigrama
            chart = DepartmentalChart.objects.create(
                name=name,
                department=department,
                description=description,
                created_by=request.user,
                status='active',
                version='1.0',
                is_external=False,
                chart_data={
                    'positions': [],
                    'connections': [],
                    'metadata': {
                        'created_date': timezone.now().isoformat(),
                        'department': department,
                        'type': 'system_created'
                    }
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Organigrama "{name}" creado exitosamente',
                'chart_id': chart.id,
                'redirect_url': f'/organizational/departamental/{chart.id}/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al crear organigrama: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def upload_departmental_chart(request):
    """Subir archivo de organigrama departmental"""
    if request.method == 'POST':
        department = request.POST.get('department')
        chart_file = request.FILES.get('chart_file')
        chart_id = request.POST.get('chart_id')  # ID del organigrama a actualizar
        description = request.POST.get('description', '')
        
        if not chart_file:
            return JsonResponse({
                'success': False,
                'error': 'Archivo es obligatorio'
            })
        
        # Validar tipo de archivo
        allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'vsd', 'vsdx', 'svg', 'ppt', 'pptx']
        file_extension = chart_file.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de archivo no permitido. Permitidos: {", ".join(allowed_extensions)}'
            })
        
        try:
            if chart_id:
                # Crear nueva versión en lugar de reemplazar
                base_chart = get_object_or_404(DepartmentalChart, id=chart_id)
                
                # Archivar la versión anterior
                base_chart.status = 'archived'
                base_chart.save()
                
                # Calcular nuevo número de versión secuencial
                existing_versions = DepartmentalChart.objects.filter(
                    department=base_chart.department
                ).count()
                
                new_version_number = existing_versions + 1
                
                # Crear nueva versión
                new_chart = DepartmentalChart.objects.create(
                    name=f"Organigrama {base_chart.department} - Versión {new_version_number}",
                    department=base_chart.department,
                    description=description or f"Versión {new_version_number} - {timezone.now().strftime('%d/%m/%Y')}",
                    chart_file=chart_file,
                    created_by=request.user,
                    status='active',
                    is_external=True,
                    version=str(new_version_number),
                    parent_chart=base_chart,
                    import_source='visio' if file_extension in ['vsd', 'vsdx'] else 'file_upload',
                    import_metadata={
                        'original_filename': chart_file.name,
                        'file_size': chart_file.size,
                        'file_type': file_extension,
                        'upload_date': timezone.now().isoformat(),
                        'version_number': new_version_number,
                        'previous_version_id': base_chart.id
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Nueva versión creada: Organigrama v{new_version_number}',
                    'chart_id': new_chart.id,
                    'version': new_version_number
                })
            else:
                # Crear primer organigrama para el departamento
                if not department:
                    return JsonResponse({
                        'success': False,
                        'error': 'Departamento es obligatorio para crear nuevo organigrama'
                    })
                
                chart = DepartmentalChart.objects.create(
                    name=f"Organigrama {department} - Versión 1",
                    department=department,
                    description=description or f"Versión inicial - {timezone.now().strftime('%d/%m/%Y')}",
                    chart_file=chart_file,
                    created_by=request.user,
                    status='active',
                    is_external=True,
                    version='1',
                    import_source='visio' if file_extension in ['vsd', 'vsdx'] else 'file_upload',
                    import_metadata={
                        'original_filename': chart_file.name,
                        'file_size': chart_file.size,
                        'file_type': file_extension,
                        'upload_date': timezone.now().isoformat(),
                        'version_number': 1
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Organigrama Versión 1 creado para {department}',
                    'chart_id': chart.id,
                    'redirect_url': f'/organizational/departamental/{chart.id}/'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar archivo: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def departmental_chart_detail(request, chart_id):
    """Ver detalle de organigrama departamental"""
    from .models import DepartmentalChart
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    # Obtener historial de versiones del departamento
    all_versions = DepartmentalChart.objects.filter(
        department=chart.department
    ).order_by('-created_at')
    
    # Obtener versión activa actual
    current_version = all_versions.filter(status='active').first()
    if not current_version:
        current_version = chart
    
    # Obtener estadísticas del departamento
    department_positions = Position.objects.filter(department=chart.department)
    department_employees = []
    
    for position in department_positions:
        employee = position.get_current_employee()
        if employee:
            employee.current_position = position  # Agregar posición actual
            department_employees.append(employee)
    
    # Estadísticas
    total_positions = department_positions.count()
    occupied_positions = sum(1 for pos in department_positions if not pos.is_vacant())
    vacant_positions = total_positions - occupied_positions
    hierarchy_levels = department_positions.values_list('level', flat=True).distinct().count()
    
    # Funciones del departamento (ejemplo)
    department_functions = {
        'Administrativo': [
            'Gestión de recursos humanos',
            'Administración de contratos',
            'Control de documentación',
            'Gestión de proveedores'
        ],
        'Comercial': [
            'Desarrollo de nuevos clientes',
            'Gestión de ventas',
            'Atención al cliente',
            'Marketing y promoción'
        ],
        'Operaciones': [
            'Producción y manufactura',
            'Control de calidad',
            'Logística y distribución',
            'Mantenimiento preventivo'
        ],
        'RRHH': [
            'Reclutamiento y selección',
            'Capacitación y desarrollo',
            'Nómina y prestaciones',
            'Relaciones laborales'
        ],
        'Finanzas': [
            'Contabilidad general',
            'Presupuestos y proyecciones',
            'Tesorería y flujo de caja',
            'Auditoría interna'
        ],
        'Mantenimiento': [
            'Mantenimiento preventivo',
            'Reparaciones correctivas',
            'Gestión de inventarios',
            'Seguridad industrial'
        ]
    }.get(chart.department, ['Funciones no definidas'])
    
    context = {
        'chart': chart,
        'current_version': current_version,
        'all_versions': all_versions,
        'department_positions': department_positions,
        'department_employees': department_employees,
        'department_stats': {
            'total_positions': total_positions,
            'occupied_positions': occupied_positions,
            'vacant_positions': vacant_positions,
            'hierarchy_levels': hierarchy_levels,
            'total_versions': all_versions.count()
        },
        'department_functions': department_functions
    }
    
    return render(request, 'organizational/departmental_chart_detail.html', context)

@login_required
def delete_departmental_chart(request, chart_id):
    """Eliminar organigrama departamental completo (solo administradores)"""
    from .models import DepartmentalChart
    
    # Verificar permisos de administrador
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para eliminar departamentos'
        }, status=403)
    
    if request.method == 'POST':
        try:
            chart = get_object_or_404(DepartmentalChart, id=chart_id)
            department = chart.department
            
            # Eliminar TODAS las versiones del departamento
            all_versions = DepartmentalChart.objects.filter(department=department)
            version_count = all_versions.count()
            
            # Eliminar archivos físicos
            for version in all_versions:
                if version.chart_file:
                    try:
                        version.chart_file.delete(save=False)
                    except:
                        pass  # Continuar aunque falle eliminar archivo
            
            # Eliminar registros de base de datos
            all_versions.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Departamento "{department}" eliminado exitosamente ({version_count} versiones eliminadas)'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar departamento: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def delete_version_api(request, version_id):
    """Eliminar versión individual de organigrama (solo administradores)"""
    from .models import DepartmentalChart
    
    # Verificar permisos de administrador
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para eliminar archivos'
        }, status=403)
    
    if request.method == 'POST':
        try:
            version = get_object_or_404(DepartmentalChart, id=version_id)
            
            # Verificar que no sea la única versión activa
            department_versions = DepartmentalChart.objects.filter(
                department=version.department
            )
            
            if department_versions.count() == 1:
                return JsonResponse({
                    'success': False,
                    'error': 'No puedes eliminar la única versión del departamento. Elimina el departamento completo si es necesario.'
                })
            
            # Si es la versión activa y hay otras versiones, activar la más reciente
            if version.status == 'active':
                other_versions = department_versions.exclude(id=version_id).order_by('-created_at')
                if other_versions.exists():
                    latest_version = other_versions.first()
                    latest_version.status = 'active'
                    latest_version.save()
            
            # Eliminar archivo físico
            if version.chart_file:
                try:
                    version.chart_file.delete(save=False)
                except:
                    pass  # Continuar aunque falle eliminar archivo
            
            # Eliminar registro
            version_name = version.name
            version.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Archivo "{version_name}" eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar archivo: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def get_departmental_charts_api(request):
    """API para obtener organigramas por departamento"""
    from .models import DepartmentalChart
    
    department = request.GET.get('department')
    
    charts = DepartmentalChart.objects.all()
    if department:
        charts = charts.filter(department=department)
    
    charts_data = []
    for chart in charts:
        charts_data.append({
            'id': chart.id,
            'name': chart.name,
            'department': chart.department,
            'status': chart.status,
            'is_external': chart.is_external,
            'file_url': chart.chart_file.url if chart.chart_file else None,
            'created_at': chart.created_at.strftime('%Y-%m-%d'),
            'updated_at': chart.updated_at.strftime('%Y-%m-%d'),
            'created_by': chart.created_by.get_full_name() if chart.created_by else 'Sistema'
        })
    
    return JsonResponse({
        'success': True,
        'charts': charts_data
    })

@login_required
def organigram_data_api(request):
    """API para obtener datos del organigrama interactivo"""
    try:
        positions = Position.objects.select_related('reports_to').prefetch_related('assignments__employee')
        
        org_data = []
        for position in positions:
            # Obtener empleado actual
            current_assignment = position.assignments.filter(end_date__isnull=True).first()
            employee = current_assignment.employee if current_assignment else None
            
            # Datos de la posición
            position_data = {
                'id': position.id,
                'title': position.title,
                'department': position.department,
                'level': position.level,
                'x_position': position.x_position,
                'y_position': position.y_position,
                'reports_to': position.reports_to.id if position.reports_to else None,
                'is_vacant': employee is None,
                'employee': None
            }
            
            # Datos del empleado si existe
            if employee:
                position_data['employee'] = {
                    'id': employee.id,
                    'name': f"{employee.first_name} {employee.last_name}",
                    'employee_id': employee.employee_id,
                    'email': employee.email,
                    'phone': employee.phone,
                    'photo': employee.photo.url if employee.photo else None,
                    'hire_date': employee.hire_date.strftime('%Y-%m-%d')
                }
            
            org_data.append(position_data)
        
        # Estadísticas
        total_positions = len(org_data)
        vacant_positions = sum(1 for p in org_data if p['is_vacant'])
        filled_positions = total_positions - vacant_positions
        fill_rate = (filled_positions / total_positions * 100) if total_positions > 0 else 0
        
        return JsonResponse({
            'success': True,
            'positions': org_data,
            'stats': {
                'total_positions': total_positions,
                'filled_positions': filled_positions,
                'vacant_positions': vacant_positions,
                'fill_rate': round(fill_rate, 1)
            },
            'departments': list(Position.objects.values_list('department', flat=True).distinct())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# NUEVAS VISTAS PARA EL EDITOR DE ORGANIGRAMAS

@login_required
def organigram_editor(request, chart_id):
    """Editor visual de organigramas"""
    from .models import DepartmentalChart
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    # Solo permitir editar organigramas creados en el sistema
    if chart.is_external:
        messages.error(request, 'No se pueden editar organigramas subidos como archivo. Solo los creados en el sistema.')
        return redirect('organizational:departmental_chart_detail', chart_id=chart_id)
    
    # Obtener todas las posiciones disponibles ordenadas jerárquicamente
    all_positions = Position.objects.all().order_by('level', 'department', 'title')
    
    # Obtener posiciones ya asignadas a este organigrama
    chart_positions = []
    if chart.chart_data and 'positions' in chart.chart_data:
        position_ids = [p['position_id'] for p in chart.chart_data['positions']]
        chart_positions = Position.objects.filter(id__in=position_ids)
    
    context = {
        'chart': chart,
        'all_positions': all_positions,
        'chart_positions': chart_positions,
        'departments': Position.objects.values_list('department', flat=True).distinct().order_by('department'),
        'can_edit': request.user.has_perm('organizational.change_departmentalchart')
    }
    
    return render(request, 'organizational/organigram_editor.html', context)

@login_required
def get_chart_positions_api(request, chart_id):
    """API para obtener posiciones del organigrama"""
    from .models import DepartmentalChart
    
    chart = get_object_or_404(DepartmentalChart, id=chart_id)
    
    positions_data = []
    
    if chart.chart_data and 'positions' in chart.chart_data:
        for pos_data in chart.chart_data['positions']:
            try:
                position = Position.objects.get(id=pos_data['position_id'])
                
                # Obtener empleado actual
                current_assignment = position.assignments.filter(end_date__isnull=True).first()
                employee = current_assignment.employee if current_assignment else None
                
                positions_data.append({
                    'id': position.id,
                    'title': position.title,
                    'department': position.department,
                    'level': position.level,
                    'x': pos_data.get('x', 100),
                    'y': pos_data.get('y', 100),
                    'reports_to': position.reports_to.id if position.reports_to else None,
                    'is_vacant': employee is None,
                    'employee': {
                        'name': f"{employee.first_name} {employee.last_name}",
                        'employee_id': employee.employee_id,
                        'photo': employee.photo.url if employee.photo else None
                    } if employee else None
                })
            except Position.DoesNotExist:
                continue
    
    return JsonResponse({
        'success': True,
        'positions': positions_data,
        'connections': chart.chart_data.get('connections', []) if chart.chart_data else []
    })

@login_required
@csrf_exempt
def save_chart_positions_api(request, chart_id):
    """API para guardar posiciones del organigrama"""
    from .models import DepartmentalChart
    
    if request.method == 'POST':
        try:
            chart = get_object_or_404(DepartmentalChart, id=chart_id)
            data = json.loads(request.body)
            
            positions = data.get('positions', [])
            connections = data.get('connections', [])
            
            # Actualizar datos del organigrama
            chart.chart_data = {
                'positions': positions,
                'connections': connections,
                'metadata': {
                    'last_updated': timezone.now().isoformat(),
                    'updated_by': request.user.username,
                    'version': chart.version
                }
            }
            chart.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Organigrama guardado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def add_position_to_chart_api(request, chart_id):
    """API para agregar posición al organigrama"""
    from .models import DepartmentalChart
    
    if request.method == 'POST':
        try:
            chart = get_object_or_404(DepartmentalChart, id=chart_id)
            data = json.loads(request.body)
            
            position_id = data.get('position_id')
            x = data.get('x', 100)
            y = data.get('y', 100)
            
            position = get_object_or_404(Position, id=position_id)
            
            # Inicializar chart_data si no existe
            if not chart.chart_data:
                chart.chart_data = {'positions': [], 'connections': []}
            
            # Verificar si la posición ya está en el organigrama
            existing_positions = [p['position_id'] for p in chart.chart_data.get('positions', [])]
            if position_id in existing_positions:
                return JsonResponse({
                    'success': False,
                    'error': 'Esta posición ya está en el organigrama'
                })
            
            # Agregar nueva posición
            new_position = {
                'position_id': position_id,
                'x': x,
                'y': y,
                'added_at': timezone.now().isoformat()
            }
            
            chart.chart_data['positions'].append(new_position)
            chart.save()
            
            # Obtener datos completos de la posición para respuesta
            current_assignment = position.assignments.filter(end_date__isnull=True).first()
            employee = current_assignment.employee if current_assignment else None
            
            position_data = {
                'id': position.id,
                'title': position.title,
                'department': position.department,
                'level': position.level,
                'x': x,
                'y': y,
                'reports_to': position.reports_to.id if position.reports_to else None,
                'is_vacant': employee is None,
                'employee': {
                    'name': f"{employee.first_name} {employee.last_name}",
                    'employee_id': employee.employee_id,
                    'photo': employee.photo.url if employee.photo else None
                } if employee else None
            }
            
            return JsonResponse({
                'success': True,
                'message': f'Posición "{position.title}" agregada al organigrama',
                'position': position_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def remove_position_from_chart_api(request, chart_id):
    """API para remover posición del organigrama"""
    from .models import DepartmentalChart
    
    if request.method == 'POST':
        try:
            chart = get_object_or_404(DepartmentalChart, id=chart_id)
            data = json.loads(request.body)
            
            position_id = data.get('position_id')
            
            if not chart.chart_data or 'positions' not in chart.chart_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay posiciones en este organigrama'
                })
            
            # Remover posición
            original_count = len(chart.chart_data['positions'])
            chart.chart_data['positions'] = [
                p for p in chart.chart_data['positions'] 
                if p['position_id'] != position_id
            ]
            
            # Remover conexiones relacionadas
            if 'connections' in chart.chart_data:
                chart.chart_data['connections'] = [
                    c for c in chart.chart_data['connections']
                    if c.get('from') != position_id and c.get('to') != position_id
                ]
            
            new_count = len(chart.chart_data['positions'])
            
            if original_count == new_count:
                return JsonResponse({
                    'success': False,
                    'error': 'La posición no estaba en el organigrama'
                })
            
            chart.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Posición removida del organigrama'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def activate_version_api(request, chart_id):
    """Activar una versión anterior como la versión actual"""
    if request.method == 'POST':
        try:
            version_to_activate = get_object_or_404(DepartmentalChart, id=chart_id)
            
            # Desactivar versión actual
            current_active = DepartmentalChart.objects.filter(
                department=version_to_activate.department,
                status='active'
            ).first()
            
            if current_active:
                current_active.status = 'archived'
                current_active.save()
            
            # Activar la versión seleccionada
            version_to_activate.status = 'active'
            version_to_activate.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Versión {version_to_activate.version} activada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al activar versión: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)