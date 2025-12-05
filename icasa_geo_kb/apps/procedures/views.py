from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

from .models import Procedure, ProcedureCategory, ProcedureTemplate, ProcedureStep, ProcedureAttachment

@login_required
def procedures_dashboard(request):
    """Dashboard principal de procedimientos"""
    try:
        # Estadísticas generales
        total_procedures = Procedure.objects.count()
        draft_procedures = Procedure.objects.filter(status='draft').count()
        published_procedures = Procedure.objects.filter(status='published').count()
        expired_procedures = Procedure.objects.filter(
            expiry_date__lt=timezone.now().date()
        ).count()
        
        # Procedimientos por vencer (próximos 30 días)
        upcoming_expiry = Procedure.objects.filter(
            expiry_date__gte=timezone.now().date(),
            expiry_date__lte=timezone.now().date() + timedelta(days=30)
        ).count()
        
        # Procedimientos por departamento
        procedures_by_dept = Procedure.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Procedimientos por categoría
        procedures_by_category = Procedure.objects.values(
            'category__name', 'category__color'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Procedimientos recientes
        recent_procedures = Procedure.objects.select_related('category').order_by('-updated_at')[:10]
        
        # Plantillas populares
        popular_templates = ProcedureTemplate.objects.filter(is_active=True).order_by('-usage_count')[:6]
        
        # Alertas críticas
        critical_alerts = []
        
        # Procedimientos vencidos
        if expired_procedures > 0:
            critical_alerts.append({
                'type': 'danger',
                'icon': 'fas fa-exclamation-triangle',
                'title': f'{expired_procedures} Procedimientos Vencidos',
                'message': 'Requieren actualización inmediata'
            })
        
        # Procedimientos por vencer
        if upcoming_expiry > 0:
            critical_alerts.append({
                'type': 'warning',
                'icon': 'fas fa-clock',
                'title': f'{upcoming_expiry} Procedimientos por Vencer',
                'message': 'Vencen en los próximos 30 días'
            })
        
        # Procedimientos sin revisar
        pending_review = Procedure.objects.filter(status='review').count()
        if pending_review > 0:
            critical_alerts.append({
                'type': 'info',
                'icon': 'fas fa-eye',
                'title': f'{pending_review} Procedimientos en Revisión',
                'message': 'Pendientes de aprobación'
            })
        
        context = {
            'total_procedures': total_procedures,
            'draft_procedures': draft_procedures,
            'published_procedures': published_procedures,
            'expired_procedures': expired_procedures,
            'upcoming_expiry': upcoming_expiry,
            'procedures_by_dept': procedures_by_dept,
            'procedures_by_category': procedures_by_category,
            'recent_procedures': recent_procedures,
            'popular_templates': popular_templates,
            'critical_alerts': critical_alerts,
        }
        
        return render(request, 'procedures/dashboard.html', context)
        
    except Exception as e:
        context = {
            'total_procedures': 0,
            'draft_procedures': 0,
            'published_procedures': 0,
            'expired_procedures': 0,
            'upcoming_expiry': 0,
            'procedures_by_dept': [],
            'procedures_by_category': [],
            'recent_procedures': [],
            'popular_templates': [],
            'critical_alerts': [],
            'error_message': f'Error al cargar datos: {str(e)}'
        }
        return render(request, 'procedures/dashboard.html', context)

@login_required
def procedure_list(request):
    """Lista de procedimientos con filtros"""
    procedures = Procedure.objects.select_related('category').all()
    
    # Filtros
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    department_filter = request.GET.get('department')
    search_query = request.GET.get('search')
    
    if status_filter:
        procedures = procedures.filter(status=status_filter)
    
    if category_filter:
        procedures = procedures.filter(category_id=category_filter)
    
    if department_filter:
        procedures = procedures.filter(department=department_filter)
    
    if search_query:
        procedures = procedures.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(objective__icontains=search_query)
        )
    
    # Obtener opciones para filtros
    categories = ProcedureCategory.objects.filter(is_active=True)
    departments = Procedure.objects.values_list('department', flat=True).distinct()
    
    context = {
        'procedures': procedures.order_by('-updated_at'),
        'categories': categories,
        'departments': departments,
        'current_filters': {
            'status': status_filter,
            'category': category_filter,
            'department': department_filter,
            'search': search_query,
        }
    }
    
    return render(request, 'procedures/procedure_list.html', context)

@login_required
def procedure_detail(request, pk):
    """Detalle de procedimiento"""
    procedure = get_object_or_404(Procedure, pk=pk)
    steps = procedure.steps.all().order_by('step_number')
    attachments = procedure.attachments.all()
    
    context = {
        'procedure': procedure,
        'steps': steps,
        'attachments': attachments,
    }
    
    return render(request, 'procedures/procedure_detail.html', context)

@login_required
def procedure_create(request):
    """Crear nuevo procedimiento"""
    if request.method == 'POST':
        try:
            # Datos básicos
            title = request.POST.get('title')
            code = request.POST.get('code')
            category_id = request.POST.get('category')
            department = request.POST.get('department')
            objective = request.POST.get('objective')
            scope = request.POST.get('scope')
            content = request.POST.get('content')
            criticality = request.POST.get('criticality')
            frequency = request.POST.get('frequency')
            responsible_position = request.POST.get('responsible_position')
            
            # Validaciones
            if not all([title, code, category_id, department, objective]):
                messages.error(request, 'Todos los campos obligatorios deben ser completados')
                return redirect('procedures:procedure_create')
            
            # Verificar código único
            if Procedure.objects.filter(code=code).exists():
                messages.error(request, f'El código "{code}" ya existe')
                return redirect('procedures:procedure_create')
            
            # Crear procedimiento
            category = get_object_or_404(ProcedureCategory, pk=category_id)
            
            procedure = Procedure.objects.create(
                title=title,
                code=code,
                category=category,
                department=department,
                objective=objective,
                scope=scope or '',
                content=content or '',
                criticality=criticality,
                frequency=frequency,
                responsible_position=responsible_position,
                owner=request.user,
                status='draft'
            )
            
            messages.success(request, f'Procedimiento "{title}" creado exitosamente')
            return redirect('procedures:procedure_detail', pk=procedure.pk)
            
        except Exception as e:
            messages.error(request, f'Error al crear procedimiento: {str(e)}')
    
    # GET: Mostrar formulario
    categories = ProcedureCategory.objects.filter(is_active=True)
    templates = ProcedureTemplate.objects.filter(is_active=True)
    
    departments = [
        'Dirección General', 'Administrativo', 'Comercial', 'Operaciones',
        'RRHH', 'Finanzas', 'Mantenimiento', 'Sistemas', 'Calidad',
        'Seguridad', 'Logística', 'Compras', 'Legal'
    ]
    
    context = {
        'categories': categories,
        'templates': templates,
        'departments': departments,
    }
    
    return render(request, 'procedures/procedure_form.html', context)

@login_required
def procedure_edit(request, pk):
    """Editar procedimiento"""
    procedure = get_object_or_404(Procedure, pk=pk)
    
    # Verificar permisos
    if procedure.owner != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para editar este procedimiento')
        return redirect('procedures:procedure_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos
            procedure.title = request.POST.get('title', procedure.title)
            procedure.department = request.POST.get('department', procedure.department)
            procedure.objective = request.POST.get('objective', procedure.objective)
            procedure.scope = request.POST.get('scope', procedure.scope)
            procedure.content = request.POST.get('content', procedure.content)
            procedure.criticality = request.POST.get('criticality', procedure.criticality)
            procedure.frequency = request.POST.get('frequency', procedure.frequency)
            procedure.responsible_position = request.POST.get('responsible_position', procedure.responsible_position)
            
            # Actualizar categoría si se proporciona
            category_id = request.POST.get('category')
            if category_id:
                procedure.category = get_object_or_404(ProcedureCategory, pk=category_id)
            
            procedure.save()
            
            messages.success(request, f'Procedimiento "{procedure.title}" actualizado exitosamente')
            return redirect('procedures:procedure_detail', pk=procedure.pk)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar procedimiento: {str(e)}')
    
    # GET: Mostrar formulario con datos actuales
    categories = ProcedureCategory.objects.filter(is_active=True)
    
    departments = [
        'Dirección General', 'Administrativo', 'Comercial', 'Operaciones',
        'RRHH', 'Finanzas', 'Mantenimiento', 'Sistemas', 'Calidad',
        'Seguridad', 'Logística', 'Compras', 'Legal'
    ]
    
    context = {
        'procedure': procedure,
        'categories': categories,
        'departments': departments,
        'is_edit': True,
    }
    
    return render(request, 'procedures/procedure_form.html', context)

@login_required
@csrf_exempt
def procedure_delete(request, pk):
    """Eliminar procedimiento"""
    if request.method == 'POST':
        try:
            procedure = get_object_or_404(Procedure, pk=pk)
            
            # Verificar permisos
            if procedure.owner != request.user and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permisos para eliminar este procedimiento'
                }, status=403)
            
            title = procedure.title
            procedure.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Procedimiento "{title}" eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar procedimiento: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def get_template_data(request, template_id):
    """Obtener datos de plantilla para procedimiento"""
    try:
        template = get_object_or_404(ProcedureTemplate, pk=template_id)
        
        # Incrementar contador de uso
        template.usage_count += 1
        template.save()
        
        return JsonResponse({
            'success': True,
            'data': template.template_content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)