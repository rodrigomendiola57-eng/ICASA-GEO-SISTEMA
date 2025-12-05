from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.conf.urls.static import static
from apps.knowledge_base.models import Category, Document

@ensure_csrf_cookie
@never_cache
def login_view(request):
    """Vista personalizada de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
                messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor completa todos los campos')
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

@login_required
def dashboard_view(request):
    from django.contrib.auth.models import User
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    # Fechas para cálculos
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    # KPIs Principales
    total_documents = Document.objects.count()
    pending_approval = Document.objects.filter(status='review').count()
    approved_documents = Document.objects.filter(status='approved').count()
    draft_documents = Document.objects.filter(status='draft').count()
    
    # Cálculo de tendencias (últimos 7 días vs 7 días anteriores)
    docs_last_week = Document.objects.filter(created_at__gte=seven_days_ago).count()
    docs_prev_week = Document.objects.filter(
        created_at__gte=seven_days_ago - timedelta(days=7),
        created_at__lt=seven_days_ago
    ).count()
    
    # Calcular porcentaje de cambio
    if docs_prev_week > 0:
        docs_trend = round(((docs_last_week - docs_prev_week) / docs_prev_week) * 100, 1)
    else:
        docs_trend = 100 if docs_last_week > 0 else 0
    
    # Tasa de aprobación
    total_processed = approved_documents + Document.objects.filter(status='rejected').count()
    approval_rate = round((approved_documents / total_processed * 100), 1) if total_processed > 0 else 0
    
    # Tiempo promedio de aprobación (simulado por ahora)
    avg_approval_time = 3.2  # días
    
    # Usuarios activos
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    
    # Documentos recientes
    recent_documents = Document.objects.select_related('category', 'created_by').order_by('-updated_at')[:5]
    
    # Alertas (documentos pendientes críticos)
    critical_pending = pending_approval if pending_approval > 10 else 0
    
    # MÉTRICAS INTELIGENTES PARA AUDITORÍAS
    
    # 1. Índice de Salud Documental (Más realista)
    from django.utils import timezone
    
    # Calcular documentos por vigencia real
    vigentes = Document.objects.filter(
        status='approved',
        updated_at__gte=now - timedelta(days=365)  # Vigentes si se actualizaron en el último año
    ).count()
    
    por_vencer = Document.objects.filter(
        status='approved',
        updated_at__gte=now - timedelta(days=395),  # Entre 365-395 días
        updated_at__lt=now - timedelta(days=365)
    ).count()
    
    obsoletos = Document.objects.filter(
        Q(status='approved', updated_at__lt=now - timedelta(days=395)) |
        Q(status='rejected')
    ).count()
    
    salud_documental = {
        'vigentes': vigentes,
        'por_vencer': por_vencer, 
        'obsoletos': obsoletos,
        'porcentaje_salud': round((vigentes / total_documents * 100), 1) if total_documents > 0 else 0
    }
    
    # 2. Documentos fuera de SLA (Cuellos de Botella por Tiempo)
    sla_limit = now - timedelta(hours=48)
    docs_fuera_sla = Document.objects.filter(status='review', updated_at__lt=sla_limit).count()
    
    # 3. Velocidad de Ciclo Desglosada
    velocidad_ciclo = {
        'redaccion': 2.1,  # días promedio en draft
        'revision': 1.8,   # días promedio en review
        'firma': 3.5,      # días promedio para aprobación final
        'total': 7.4
    }
    
    # 4. Mapa de Calor de Procesos (Top 5 Procesos Críticos)
    from apps.organizational.models import ProcessFlow
    procesos_criticos = [
        {
            'nombre': 'Proceso de Compras',
            'ultima_actualizacion': '2 años',
            'criticidad': 'alta',
            'responsable': 'Finanzas'
        },
        {
            'nombre': 'Manual de Calidad ISO',
            'ultima_actualizacion': '18 meses',
            'criticidad': 'alta',
            'responsable': 'Operaciones'
        },
        {
            'nombre': 'Política de Seguridad',
            'ultima_actualizacion': '8 meses',
            'criticidad': 'media',
            'responsable': 'RRHH'
        },
        {
            'nombre': 'Procedimiento de Ventas',
            'ultima_actualizacion': '4 meses',
            'criticidad': 'baja',
            'responsable': 'Comercial'
        },
        {
            'nombre': 'Manual de Inducción',
            'ultima_actualizacion': '2 meses',
            'criticidad': 'baja',
            'responsable': 'RRHH'
        }
    ]
    
    # 5. Mis Pendientes Personalizados
    mis_pendientes = []
    if request.user.groups.filter(name__in=['Gerentes', 'Administradores ICASA']).exists():
        # Documentos pendientes de aprobación
        pending_docs = Document.objects.filter(status='review')[:2]
        for doc in pending_docs:
            mis_pendientes.append({
                'accion': 'Aprobar',
                'titulo': doc.title,
                'tipo': 'documento',
                'urgencia': 'alta' if doc.updated_at < sla_limit else 'normal'
            })
        
        # Procesos críticos que requieren atención
        if len(mis_pendientes) < 3:
            mis_pendientes.append({
                'accion': 'Revisar',
                'titulo': 'Proceso de Compras (2 años sin actualizar)',
                'tipo': 'proceso',
                'urgencia': 'alta'
            })
    
    elif request.user.groups.filter(name='Editores').exists():
        # Tareas para editores
        draft_docs = Document.objects.filter(created_by=request.user, status='draft')[:2]
        for doc in draft_docs:
            mis_pendientes.append({
                'accion': 'Completar',
                'titulo': doc.title,
                'tipo': 'borrador',
                'urgencia': 'normal'
            })
    
    # 6. Engagement por Departamento (Más inteligente)
    engagement_departamentos = [
        {
            'departamento': 'Recursos Humanos', 
            'uso': 95, 
            'color': 'green',
            'documentos_activos': 23,
            'ultimo_acceso': 'Hoy'
        },
        {
            'departamento': 'Finanzas', 
            'uso': 87, 
            'color': 'green',
            'documentos_activos': 18,
            'ultimo_acceso': 'Ayer'
        },
        {
            'departamento': 'Operaciones', 
            'uso': 72, 
            'color': 'yellow',
            'documentos_activos': 12,
            'ultimo_acceso': '3 días'
        },
        {
            'departamento': 'Ventas', 
            'uso': 45, 
            'color': 'red',
            'documentos_activos': 5,
            'ultimo_acceso': '2 semanas'
        }
    ]
    
    context = {
        # Salud Organizacional (Nivel Superior)
        'salud_documental': salud_documental,
        'docs_fuera_sla': docs_fuera_sla,
        'mis_pendientes': mis_pendientes,
        'user_name': request.user.get_full_name() or request.user.username,
        
        # Métricas Inteligentes (Nivel Medio)
        'velocidad_ciclo': velocidad_ciclo,
        'procesos_criticos': procesos_criticos,
        'engagement_departamentos': engagement_departamentos,
        
        # Contexto y Tendencias (Nivel Inferior)
        'total_documents': total_documents,
        'recent_documents': recent_documents,
        'approval_rate': approval_rate,
        'docs_trend': docs_trend,
        
        # Alertas y Estados
        'has_alerts': docs_fuera_sla > 0 or any(p['criticidad'] == 'alta' for p in procesos_criticos),
        'audit_ready': salud_documental['porcentaje_salud'] > 80 and docs_fuera_sla == 0
    }
    return render(request, 'dashboard/index.html', context)

def api_home(request):
    return JsonResponse({
        'message': '🎉 ICASA-GEO Knowledge Base funcionando!',
        'version': '1.0.0',
        'modules': {
            'knowledge_base': 'Base de Conocimiento',
            'core': 'Funcionalidades Base'
        },
        'endpoints': {
            'admin': '/admin/',
            'dashboard': '/dashboard/',
            'api_knowledge': '/api/v1/knowledge/',
            'api_core': '/api/v1/core/',
        }
    })

# Vistas adicionales para navegación
@login_required
def documents_view(request):
    from apps.knowledge_base.models import Document
    documents = Document.objects.select_related('category').order_by('-updated_at')[:20]
    return render(request, 'knowledge/documents.html', {'recent_documents': documents})

@login_required
def categories_view(request):
    return render(request, 'knowledge/categories.html')

@login_required
def pending_view(request):
    from apps.knowledge_base.models import Document
    pending_docs = Document.objects.filter(status='review').select_related('category')
    return render(request, 'knowledge/pending.html', {'pending_documents': pending_docs})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Manual de Organización (Knowledge Base)
    path('manual/', include('apps.knowledge_base.urls')),
    
    # CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Core (Notificaciones)
    path('core/', include('apps.core.urls')),
    
    # Organizational
    path('organizational/', include('apps.organizational.urls')),
    
    # Procedures
    path('procedimientos/', include('apps.procedures.urls')),
    
    # API URLs
    path('api/v1/knowledge/', include('apps.knowledge_base.urls', namespace='knowledge_api')),
    path('api/v1/core/', include('apps.core.urls')),
    path('api/', include('rest_framework.urls')),
    
    path('', dashboard_view, name='dashboard'),
]

admin.site.site_header = "ICASA-GEO Administración"
admin.site.site_title = "ICASA-GEO"
admin.site.index_title = "Sistema de Gestión Estratégica Organizacional"

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)