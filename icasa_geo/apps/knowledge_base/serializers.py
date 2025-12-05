"""
Serializers para Knowledge Base API
"""
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from apps.core.serializers import BaseModelSerializer, UserSerializer
from .models import Category, DocumentTemplate, Document, DocumentRevision

class CategorySerializer(BaseModelSerializer, serializers.ModelSerializer):
    """
    Serializer para categorías con información jerárquica
    """
    children = serializers.SerializerMethodField()
    document_count = serializers.ReadOnlyField()
    breadcrumb = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = BaseModelSerializer.Meta.fields + [
            'name', 'slug', 'description', 'parent', 'icon', 'color',
            'order', 'is_active', 'children', 'document_count', 'breadcrumb', 'level'
        ]
    
    def get_children(self, obj):
        """Obtener categorías hijas"""
        if hasattr(obj, 'prefetched_children'):
            children = obj.prefetched_children
        else:
            children = obj.get_children()
        
        return CategorySerializer(children, many=True, context=self.context).data
    
    def get_breadcrumb(self, obj):
        """Generar breadcrumb"""
        ancestors = obj.get_ancestors(include_self=True)
        return [{'name': cat.name, 'slug': cat.slug} for cat in ancestors]

class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para árbol de categorías
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'color', 'children']
    
    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data

class DocumentTemplateSerializer(BaseModelSerializer, serializers.ModelSerializer):
    """
    Serializer para templates de documentos
    """
    class Meta:
        model = DocumentTemplate
        fields = BaseModelSerializer.Meta.fields + [
            'name', 'template_type', 'content', 'variables', 'is_active'
        ]

class DocumentListSerializer(BaseModelSerializer, TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer para lista de documentos (información básica)
    """
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Document
        fields = BaseModelSerializer.Meta.fields + [
            'title', 'slug', 'category', 'document_code', 'summary',
            'status', 'status_display', 'version', 'effective_date',
            'is_public', 'tags'
        ]

class DocumentDetailSerializer(BaseModelSerializer, TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer completo para documentos
    """
    category = CategorySerializer(read_only=True)
    template = DocumentTemplateSerializer(read_only=True)
    tags = TagListSerializerField()
    breadcrumb_path = serializers.SerializerMethodField()
    rendered_content = serializers.SerializerMethodField()
    approved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Document
        fields = BaseModelSerializer.Meta.fields + [
            'title', 'slug', 'category', 'template', 'content', 'rendered_content',
            'summary', 'tags', 'document_code', 'effective_date', 'review_date',
            'status', 'approved_by', 'approved_at', 'rejection_reason',
            'version', 'is_current', 'version_notes', 'is_public',
            'requires_acknowledgment', 'auto_save_enabled', 'breadcrumb_path'
        ]
    
    def get_breadcrumb_path(self, obj):
        """Generar breadcrumb completo"""
        path = []
        for item in obj.breadcrumb_path:
            if hasattr(item, 'get_absolute_url'):
                path.append({
                    'name': item.name if hasattr(item, 'name') else item.title,
                    'url': item.get_absolute_url(),
                    'type': 'category' if hasattr(item, 'name') else 'document'
                })
        return path
    
    def get_rendered_content(self, obj):
        """Obtener contenido con variables renderizadas"""
        return obj.render_content_with_variables()

class DocumentCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer para crear/actualizar documentos
    """
    tags = TagListSerializerField()
    
    class Meta:
        model = Document
        fields = [
            'title', 'category', 'template', 'content', 'summary', 'tags',
            'document_code', 'effective_date', 'review_date', 'is_public',
            'requires_acknowledgment', 'auto_save_enabled', 'version_notes'
        ]
    
    def validate_document_code(self, value):
        """Validar que el código de documento sea único"""
        instance = getattr(self, 'instance', None)
        if Document.objects.filter(document_code=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un documento con este código.")
        return value

class DocumentRevisionSerializer(BaseModelSerializer, serializers.ModelSerializer):
    """
    Serializer para revisiones de documentos
    """
    class Meta:
        model = DocumentRevision
        fields = BaseModelSerializer.Meta.fields + [
            'document', 'content', 'change_summary', 'is_auto_save'
        ]