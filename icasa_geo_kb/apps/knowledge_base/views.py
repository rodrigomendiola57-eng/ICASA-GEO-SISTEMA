from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Document
from .serializers import CategorySerializer, DocumentSerializer
from .forms import DocumentForm, CategoryForm

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        root_categories = Category.objects.filter(parent=None, is_active=True)
        serializer = CategorySerializer(root_categories, many=True)
        return Response(serializer.data)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('category')
    serializer_class = DocumentSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por categoría
        category_slug = self.request.query_params.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=categories)
            except Category.DoesNotExist:
                pass
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, slug=None):
        document = self.get_object()
        
        if document.status != 'review':
            return Response(
                {'error': 'Solo se pueden aprobar documentos en revisión'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document.approve(request.user)
        return Response({'message': 'Documento aprobado exitosamente'})

# Web Views
@login_required
def knowledge_base_dashboard(request):
    """Dashboard Ejecutivo Inteligente del Manual de Organización"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Q, Avg
    from django.utils import timezone
    
    # Categorías principales
    main_categories = Category.objects.filter(parent=None, is_active=True)
    
    # Agregar documentos recientes a cada categoría
    for category in main_categories:
        category.recent_documents = Document.objects.filter(
            category__in=category.get_descendants(include_self=True),
            status='approved'
        ).order_by('-updated_at')[:1]
    
    # === MÉTRICAS EJECUTIVAS INTELIGENTES ===
    
    # 1. Índice de Salud Documental
    now = timezone.now()
    thirty_days = now - timedelta(days=30)
    ninety_days = now - timedelta(days=90)
    
    total_docs = Document.objects.count()
    vigentes = Document.objects.filter(updated_at__gte=ninety_days).count()
    por_vencer = Document.objects.filter(
        updated_at__lt=ninety_days, updated_at__gte=ninety_days - timedelta(days=30)
    ).count()
    obsoletos = Document.objects.filter(updated_at__lt=ninety_days - timedelta(days=30)).count()
    
    # 2. Documentos Fuera de SLA (más de 48 horas en revisión)
    sla_limit = now - timedelta(hours=48)
    docs_fuera_sla = Document.objects.filter(
        status='review', updated_at__lt=sla_limit
    ).count()
    
    # 3. Mis Tareas Pendientes (personalizado por usuario)
    mis_pendientes = Document.objects.filter(
        created_by=request.user,
        status__in=['draft', 'review']
    )[:5]
    
    # 4. Top 5 Categorías con Documentos Desactualizados
    categorias_criticas = Category.objects.annotate(
        docs_obsoletos=Count('document', filter=Q(
            document__updated_at__lt=ninety_days,
            document__status='approved'
        ))
    ).filter(docs_obsoletos__gt=0).order_by('-docs_obsoletos')[:5]
    
    # 5. Métricas de Actividad (últimos 30 días)
    docs_creados_mes = Document.objects.filter(created_at__gte=thirty_days).count()
    docs_aprobados_mes = Document.objects.filter(
        status='approved', updated_at__gte=thirty_days
    ).count()
    
    # 6. Tiempo Promedio de Aprobación
    from django.db.models import F, ExpressionWrapper, DurationField
    tiempo_promedio = Document.objects.filter(
        status='approved', created_at__gte=thirty_days
    ).aggregate(
        promedio=Avg(ExpressionWrapper(
            F('updated_at') - F('created_at'),
            output_field=DurationField()
        ))
    )['promedio']
    
    # 7. Documentos más consultados (simulado - implementar tracking real)
    docs_populares = Document.objects.filter(status='approved').order_by('-updated_at')[:5]
    
    # 8. Alertas Críticas
    alertas = []
    if docs_fuera_sla > 0:
        alertas.append({
            'tipo': 'danger',
            'mensaje': f'{docs_fuera_sla} documentos llevan más de 48h en revisión',
            'icono': 'fas fa-exclamation-triangle'
        })
    if obsoletos > total_docs * 0.2:  # Más del 20% obsoletos
        alertas.append({
            'tipo': 'warning', 
            'mensaje': f'{obsoletos} documentos necesitan actualización urgente',
            'icono': 'fas fa-clock'
        })
    
    # Documentos recientes globales
    recent_documents = Document.objects.filter(status='approved').order_by('-updated_at')[:6]
    
    context = {
        'main_categories': main_categories,
        'recent_documents': recent_documents,
        'mis_pendientes': mis_pendientes,
        
        # Métricas de Salud
        'total_documents': total_docs,
        'vigentes': vigentes,
        'por_vencer': por_vencer, 
        'obsoletos': obsoletos,
        'salud_porcentaje': round((vigentes / total_docs * 100) if total_docs > 0 else 0),
        
        # KPIs Ejecutivos
        'docs_fuera_sla': docs_fuera_sla,
        'docs_creados_mes': docs_creados_mes,
        'docs_aprobados_mes': docs_aprobados_mes,
        'tiempo_promedio_dias': tiempo_promedio.days if tiempo_promedio else 0,
        
        # Análisis
        'categorias_criticas': categorias_criticas,
        'docs_populares': docs_populares,
        'alertas': alertas,
        
        # Permisos
        'can_create': request.user.has_perm('knowledge_base.add_document'),
        'is_manager': request.user.groups.filter(name__in=['Managers', 'Directivos']).exists(),
    }
    
    return render(request, 'knowledge_base/dashboard.html', context)

@login_required
def category_detail(request, slug):
    """Vista de detalle de categoría con documentos y subcategorías"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Documentos de esta categoría (solo aprobados para usuarios normales)
    documents = Document.objects.filter(category=category)
    if not request.user.has_perm('knowledge_base.view_all_documents'):
        documents = documents.filter(status='approved')
    
    documents = documents.select_related('created_by', 'category').prefetch_related('tags').order_by('-updated_at')
    
    # Subcategorías directas
    subcategories = category.get_children().filter(is_active=True).order_by('name')
    
    # Agregar conteo de documentos a cada subcategoría
    for subcat in subcategories:
        subcat.document_count = subcat.get_document_count()
    
    context = {
        'category': category,
        'documents': documents,
        'subcategories': subcategories,
    }
    return render(request, 'knowledge_base/category_detail.html', context)

@login_required
def document_detail(request, slug):
    document = get_object_or_404(Document, slug=slug)
    
    if document.status != 'approved' and not request.user.has_perm('knowledge_base.change_document'):
        messages.error(request, 'Documento no disponible')
        return redirect('knowledge_base:home')
    
    context = {'document': document}
    return render(request, 'knowledge_base/document_detail.html', context)

@login_required
def document_create(request):
    """Crear nuevo documento con editor colaborativo"""
    # Permitir acceso a usuarios autenticados por ahora
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para crear documentos')
        return redirect('login')
    
    if request.method == 'POST':
        # Procesar datos del editor colaborativo
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        document_code = request.POST.get('document_code')
        
        try:
            category = None
            if category_id:
                category = Category.objects.get(id=category_id)
            
            document = Document.objects.create(
                title=title or 'Documento sin título',
                content=content or '<p>Contenido del documento...</p>',
                category=category,
                document_code=document_code or 'DOC-TMP',
                created_by=request.user,
                status='draft'
            )
            
            messages.success(request, 'Documento creado exitosamente')
            return JsonResponse({
                'success': True,
                'redirect_url': f'/manual/document/{document.slug}/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - mostrar editor
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    # Obtener categoría preseleccionada
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        try:
            selected_category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            pass
    
    # Obtener plantilla preseleccionada
    template_key = request.GET.get('template')
    template_content = ''
    if template_key and category_slug:
        from .templates import DocumentTemplates
        template = DocumentTemplates.get_template(category_slug, template_key)
        if template:
            template_content = template['content']
    
    # Usar editor específico por categoría si existe
    if selected_category:
        category_editors = {
            'informacion-corporativa': 'knowledge_base/editors/informacion_corporativa.html',
            'marco-legal': 'knowledge_base/editors/marco_legal.html',
            'politicas-organizacionales': 'knowledge_base/editors/politicas.html',
            'manuales-operativos': 'knowledge_base/editors/manuales.html',
            'manuales': 'knowledge_base/editors/manuales.html',
            'objetivos-estrategicos': 'knowledge_base/editors/objetivos.html'
        }
        
        editor_template = category_editors.get(selected_category.slug)
        if editor_template:
            context = {
                'category': selected_category,
                'template_content': template_content
            }
            return render(request, editor_template, context)
    
    # Editor genérico por defecto
    context = {
        'document': None,
        'categories': categories,
        'selected_category': selected_category,
        'template_content': template_content,
        'is_new': True
    }
    return render(request, 'knowledge_base/document_editor.html', context)

@login_required
def document_edit(request, slug):
    """Editar documento existente con editor colaborativo"""
    document = get_object_or_404(Document, slug=slug)
    
    # Verificar permisos
    if not (document.created_by == request.user or 
            request.user.has_perm('knowledge_base.change_document')):
        messages.error(request, 'No tienes permisos para editar este documento')
        return redirect('knowledge_base:document_detail', slug=slug)
    
    if request.method == 'POST':
        # Procesar actualización
        document.title = request.POST.get('title', document.title)
        document.content = request.POST.get('content', document.content)
        
        category_id = request.POST.get('category')
        if category_id:
            try:
                document.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        document.document_code = request.POST.get('document_code', document.document_code)
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Documento actualizado exitosamente'
        })
    
    # GET request - mostrar editor
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'document': document,
        'categories': categories,
        'is_new': False
    }
    return render(request, 'knowledge_base/document_editor.html', context)

@login_required
def search_documents(request):
    """Búsqueda avanzada de documentos con filtros"""
    from .search import DocumentSearchEngine, SmartSearchFilters
    
    query = request.GET.get('q', '')
    documents = []
    categories = []
    
    # Obtener filtros de la request
    filters = {
        'category': request.GET.get('category'),
        'status': request.GET.get('status'),
        'author': request.GET.get('author'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
        'recent_only': request.GET.get('recent_only') == 'true'
    }
    
    # Limpiar filtros vacíos
    filters = {k: v for k, v in filters.items() if v}
    
    if query:
        documents = DocumentSearchEngine.search_documents(query, request.user, filters)
        categories = DocumentSearchEngine.search_categories(query)
    
    # Obtener filtros disponibles
    available_filters = SmartSearchFilters.get_available_filters()
    
    context = {
        'query': query,
        'documents': documents,
        'categories': categories,
        'total_results': len(documents) + len(categories),
        'applied_filters': filters,
        'available_filters': available_filters,
        'has_filters': bool(filters)
    }
    return render(request, 'knowledge_base/search_results.html', context)

@login_required
def search_suggestions(request):
    """API para sugerencias de búsqueda en tiempo real"""
    from .search import DocumentSearchEngine
    
    query = request.GET.get('q', '')
    suggestions = DocumentSearchEngine.get_suggestions(query)
    
    return JsonResponse({
        'suggestions': suggestions,
        'query': query,
        'count': len(suggestions)
    })

@login_required
def advanced_search(request):
    """Página de búsqueda avanzada"""
    from .search import SmartSearchFilters
    
    context = {
        'available_filters': SmartSearchFilters.get_available_filters()
    }
    return render(request, 'knowledge_base/advanced_search.html', context)

@login_required
def categories_management(request):
    """Gestión completa de categorías"""
    # Permitir acceso a usuarios staff por ahora
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para gestionar categorías')
        return redirect('knowledge_base:dashboard')
    
    # Categorías principales
    main_categories = Category.objects.filter(parent=None, is_active=True).order_by('name')
    
    # Todas las categorías para el selector padre
    all_categories = Category.objects.filter(is_active=True).order_by('name')
    
    # Estadísticas
    total_categories = Category.objects.filter(is_active=True).count()
    total_documents = Document.objects.count()
    from django.db import models
    max_depth = Category.objects.aggregate(
        max_level=models.Max('level')
    )['max_level'] or 0
    
    # Categorías vacías
    empty_categories = Category.objects.filter(
        is_active=True,
        document__isnull=True
    ).distinct().count()
    
    context = {
        'main_categories': main_categories,
        'all_categories': all_categories,
        'total_categories': total_categories,
        'total_documents': total_documents,
        'max_depth': max_depth + 1,
        'empty_categories': empty_categories,
    }
    
    return render(request, 'knowledge_base/categories_management.html', context)

@login_required
def category_create_ajax(request):
    """Crear categoría vía AJAX"""
    if request.method == 'POST':
        if not (request.user.is_staff or request.user.has_perm('knowledge_base.add_category')):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para crear categorías'
            })
        
        try:
            name = request.POST.get('name', '').strip()
            parent_id = request.POST.get('parent')
            description = request.POST.get('description', '').strip()
            icon = request.POST.get('icon', 'fas fa-folder')
            color = request.POST.get('color', '#22c55e')
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre de la categoría es obligatorio'
                })
            
            if len(name) < 3:
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre debe tener al menos 3 caracteres'
                })
            
            parent = None
            if parent_id:
                try:
                    parent = Category.objects.get(id=parent_id)
                except Category.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'La categoría padre no existe'
                    })
            
            existing = Category.objects.filter(
                name__iexact=name,
                parent=parent,
                is_active=True
            ).exists()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una categoría con el nombre "{name}" en este nivel'
                })
            
            category = Category.objects.create(
                name=name,
                parent=parent,
                description=description,
                icon=icon,
                color=color
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Categoría "{name}" creada exitosamente',
                'category_id': category.id,
                'category_slug': category.slug,
                'is_subcategory': parent is not None
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def category_templates(request, slug):
    """Mostrar plantillas disponibles para una categoría"""
    from .templates import DocumentTemplates
    import json
    
    category = get_object_or_404(Category, slug=slug, is_active=True)
    templates = DocumentTemplates.get_templates_by_category(slug)
    
    context = {
        'category': category,
        'templates': templates,
        'templates_json': json.dumps(templates)
    }
    
    return render(request, 'knowledge_base/category_templates.html', context)