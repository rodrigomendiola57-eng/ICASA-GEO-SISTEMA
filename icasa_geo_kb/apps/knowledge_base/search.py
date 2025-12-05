"""
Motor de Búsqueda Avanzado para Knowledge Base
Implementa búsqueda full-text, filtros inteligentes y sugerencias automáticas
"""

from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone
from datetime import timedelta
from .models import Document, Category
import re

class DocumentSearchEngine:
    """Motor de búsqueda inteligente para documentos"""
    
    @staticmethod
    def search_documents(query, user, filters=None):
        """
        Búsqueda full-text de documentos con filtros avanzados
        """
        if not query or len(query.strip()) < 2:
            return Document.objects.none()
        
        # Limpiar query
        clean_query = re.sub(r'[^\w\s]', '', query.strip())
        
        # Base queryset con permisos
        queryset = Document.objects.select_related('category', 'created_by')
        
        # Aplicar permisos de usuario
        if not user.has_perm('knowledge_base.view_all_documents'):
            queryset = queryset.filter(
                Q(status='approved') | Q(created_by=user)
            )
        
        # Búsqueda PostgreSQL full-text
        search_vector = SearchVector('title', weight='A') + \
                       SearchVector('content', weight='B') + \
                       SearchVector('document_code', weight='A') + \
                       SearchVector('category__name', weight='C')
        
        search_query = SearchQuery(clean_query)
        
        queryset = queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank', '-updated_at')
        
        # Aplicar filtros adicionales
        if filters:
            queryset = DocumentSearchEngine._apply_filters(queryset, filters)
        
        return queryset[:50]  # Limitar resultados
    
    @staticmethod
    def search_categories(query):
        """Búsqueda en categorías"""
        if not query or len(query.strip()) < 2:
            return Category.objects.none()
        
        return Category.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).order_by('name')[:10]
    
    @staticmethod
    def get_suggestions(query):
        """Generar sugerencias automáticas mientras se escribe"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = []
        
        # Sugerencias de títulos de documentos
        doc_titles = Document.objects.filter(
            title__icontains=query,
            status='approved'
        ).values_list('title', flat=True)[:5]
        
        for title in doc_titles:
            suggestions.append({
                'type': 'document',
                'text': title,
                'icon': 'fas fa-file-alt',
                'category': 'Documento'
            })
        
        # Sugerencias de categorías
        categories = Category.objects.filter(
            name__icontains=query,
            is_active=True
        ).values_list('name', flat=True)[:3]
        
        for cat_name in categories:
            suggestions.append({
                'type': 'category',
                'text': cat_name,
                'icon': 'fas fa-folder',
                'category': 'Categoría'
            })
        
        # Sugerencias de términos comunes
        common_terms = DocumentSearchEngine._get_common_terms(query)
        for term in common_terms:
            suggestions.append({
                'type': 'term',
                'text': term,
                'icon': 'fas fa-search',
                'category': 'Término'
            })
        
        return suggestions[:8]
    
    @staticmethod
    def _apply_filters(queryset, filters):
        """Aplicar filtros avanzados"""
        
        # Filtro por categoría
        if filters.get('category'):
            try:
                category = Category.objects.get(slug=filters['category'])
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=categories)
            except Category.DoesNotExist:
                pass
        
        # Filtro por estado
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        # Filtro por autor
        if filters.get('author'):
            queryset = queryset.filter(created_by__username__icontains=filters['author'])
        
        # Filtro por fecha
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        # Filtro por actualización reciente
        if filters.get('recent_only'):
            thirty_days_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(updated_at__gte=thirty_days_ago)
        
        return queryset
    
    @staticmethod
    def _get_common_terms(query):
        """Obtener términos comunes relacionados"""
        common_terms = [
            f"política de {query}",
            f"procedimiento de {query}",
            f"manual de {query}",
            f"proceso de {query}",
            f"normativa de {query}"
        ]
        return common_terms[:3]
    
    @staticmethod
    def get_search_analytics():
        """Obtener analytics de búsquedas (para dashboard)"""
        # Implementar tracking de búsquedas populares
        return {
            'total_searches_today': 0,  # Implementar con modelo SearchLog
            'popular_terms': [],        # Top términos buscados
            'zero_results': 0,          # Búsquedas sin resultados
        }

class SmartSearchFilters:
    """Filtros inteligentes para búsqueda avanzada"""
    
    @staticmethod
    def get_available_filters():
        """Obtener filtros disponibles dinámicamente"""
        return {
            'categories': Category.objects.filter(
                is_active=True,
                document__isnull=False
            ).distinct().values('slug', 'name'),
            
            'authors': Document.objects.values_list(
                'created_by__username', 
                'created_by__first_name'
            ).distinct()[:20],
            
            'status_choices': Document.STATUS_CHOICES,
            
            'date_ranges': [
                {'key': 'today', 'label': 'Hoy'},
                {'key': 'week', 'label': 'Esta semana'},
                {'key': 'month', 'label': 'Este mes'},
                {'key': 'quarter', 'label': 'Este trimestre'},
                {'key': 'year', 'label': 'Este año'},
            ]
        }

class SearchHistory:
    """Gestión del historial de búsquedas por usuario"""
    
    @staticmethod
    def save_search(user, query, results_count):
        """Guardar búsqueda en historial (implementar modelo SearchLog)"""
        # TODO: Crear modelo SearchLog para tracking
        pass
    
    @staticmethod
    def get_user_history(user, limit=10):
        """Obtener historial de búsquedas del usuario"""
        # TODO: Implementar con modelo SearchLog
        return []
    
    @staticmethod
    def get_popular_searches(limit=10):
        """Obtener búsquedas más populares"""
        # TODO: Implementar con agregaciones
        return []