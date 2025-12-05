"""
Vistas para Knowledge Base
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.views import BaseViewSet
from apps.core.permissions import IsOwnerOrReadOnly, CanApprovePermission
from .models import Category, DocumentTemplate, Document, DocumentRevision
from .serializers import (
    CategorySerializer, CategoryTreeSerializer, DocumentTemplateSerializer,
    DocumentListSerializer, DocumentDetailSerializer, DocumentCreateUpdateSerializer,
    DocumentRevisionSerializer
)

class CategoryViewSet(BaseViewSet):
    """
    ViewSet para categorías con funcionalidades jerárquicas
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch children para optimizar consultas
        queryset = queryset.prefetch_related(
            Prefetch('children', queryset=Category.objects.filter(is_active=True))
        )
        
        # Filtrar por nivel si se especifica
        level = self.request.query_params.get('level')
        if level is not None:
            queryset = queryset.filter(level=level)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Obtener árbol completo de categorías"""
        root_categories = Category.objects.filter(parent=None, is_active=True)
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, slug=None):
        """Obtener documentos de una categoría"""
        category = self.get_object()
        
        # Incluir documentos de subcategorías
        categories = category.get_descendants(include_self=True)
        documents = Document.objects.filter(
            category__in=categories,
            status='approved'
        ).select_related('category', 'created_by')
        
        # Filtros adicionales
        search = request.query_params.get('search')
        if search:
            documents = documents.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(document_code__icontains=search)
            )
        
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)

class DocumentTemplateViewSet(BaseViewSet):
    """
    ViewSet para templates de documentos
    """
    queryset = DocumentTemplate.objects.filter(is_active=True)
    serializer_class = DocumentTemplateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo si se especifica
        template_type = self.request.query_params.get('type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        return queryset

class DocumentViewSet(BaseViewSet):
    """
    ViewSet para documentos con funcionalidades avanzadas
    """
    queryset = Document.objects.select_related('category', 'template', 'created_by', 'approved_by')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DocumentCreateUpdateSerializer
        return DocumentDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # Por defecto, solo mostrar documentos aprobados para usuarios normales
            if not self.request.user.has_perm('knowledge_base.can_view_draft'):
                queryset = queryset.filter(status='approved')
        
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
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(document_code__icontains=search) |
                Q(summary__icontains=search)
            )
        
        # Filtro por tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener documento y registrar visualización"""
        instance = self.get_object()
        
        # Registrar visualización
        from .models import DocumentView
        DocumentView.objects.get_or_create(
            document=instance,
            user=request.user,
            defaults={
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'], permission_classes=[CanApprovePermission])
    def approve(self, request, slug=None):
        """Aprobar documento"""
        document = self.get_object()
        
        if document.status != 'review':
            return Response(
                {'error': 'Solo se pueden aprobar documentos en revisión'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document.approve(request.user)
        return Response({'message': 'Documento aprobado exitosamente'})
    
    @action(detail=True, methods=['post'], permission_classes=[CanApprovePermission])
    def reject(self, request, slug=None):
        """Rechazar documento"""
        document = self.get_object()
        reason = request.data.get('reason', '')
        
        if document.status != 'review':
            return Response(
                {'error': 'Solo se pueden rechazar documentos en revisión'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document.reject(request.user, reason)
        return Response({'message': 'Documento rechazado'})
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, slug=None):
        """Enviar documento para revisión"""
        document = self.get_object()
        
        if document.status != 'draft':
            return Response(
                {'error': 'Solo se pueden enviar borradores para revisión'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document.status = 'review'
        document.save()
        return Response({'message': 'Documento enviado para revisión'})
    
    @action(detail=True, methods=['post'])
    def auto_save(self, request, slug=None):
        """Autoguardado del documento"""
        document = self.get_object()
        content = request.data.get('content', '')
        
        if not document.auto_save_enabled:
            return Response(
                {'error': 'Autoguardado deshabilitado para este documento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear revisión de autoguardado
        DocumentRevision.objects.create(
            document=document,
            content=content,
            is_auto_save=True,
            created_by=request.user
        )
        
        return Response({'message': 'Autoguardado realizado'})
    
    @action(detail=True, methods=['get'])
    def revisions(self, request, slug=None):
        """Obtener historial de revisiones"""
        document = self.get_object()
        revisions = document.revisions.all()[:20]  # Últimas 20 revisiones
        serializer = DocumentRevisionSerializer(revisions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """Obtener documentos del usuario actual"""
        documents = self.get_queryset().filter(created_by=request.user)
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Obtener documentos pendientes de aprobación"""
        if not request.user.has_perm('knowledge_base.can_approve'):
            return Response(
                {'error': 'Sin permisos para ver documentos pendientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documents = self.get_queryset().filter(status='review')
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)