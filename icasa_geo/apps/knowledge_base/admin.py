"""
Configuración del admin para Knowledge Base
"""
from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from apps.core.admin import BaseModelAdmin, ApprovalModelAdmin
from .models import Category, DocumentTemplate, Document, DocumentRevision, DocumentView

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, BaseModelAdmin):
    """
    Admin para categorías con drag & drop
    """
    list_display = ('tree_actions', 'indented_title', 'document_count', 'is_active', 'created_at')
    list_display_links = ('indented_title',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Apariencia', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def indented_title(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * 20,
            instance.name,
        )
    indented_title.short_description = 'Nombre'

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(BaseModelAdmin):
    """
    Admin para templates de documentos
    """
    list_display = ('name', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'content')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Contenido', {
            'fields': ('content', 'variables')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )

@admin.register(Document)
class DocumentAdmin(ApprovalModelAdmin):
    """
    Admin para documentos con workflow de aprobación
    """
    list_display = (
        'document_code', 'title', 'category', 'status', 
        'version', 'effective_date', 'created_at'
    )
    list_filter = (
        'status', 'category', 'is_public', 'requires_acknowledgment',
        'effective_date', 'created_at'
    )
    search_fields = ('title', 'document_code', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'document_code', 'category', 'template')
        }),
        ('Contenido', {
            'fields': ('summary', 'content', 'tags')
        }),
        ('Metadatos', {
            'fields': ('effective_date', 'review_date')
        }),
        ('Configuración', {
            'fields': ('is_public', 'requires_acknowledgment', 'auto_save_enabled')
        }),
        ('Workflow', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Versionado', {
            'fields': ('version', 'is_current', 'version_notes')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_documents', 'reject_documents']
    
    def approve_documents(self, request, queryset):
        """Acción para aprobar documentos en lote"""
        count = 0
        for document in queryset:
            if document.status == 'review':
                document.approve(request.user)
                count += 1
        
        self.message_user(request, f'{count} documentos aprobados exitosamente.')
    approve_documents.short_description = "Aprobar documentos seleccionados"
    
    def reject_documents(self, request, queryset):
        """Acción para rechazar documentos en lote"""
        count = 0
        for document in queryset:
            if document.status == 'review':
                document.reject(request.user, "Rechazado desde admin")
                count += 1
        
        self.message_user(request, f'{count} documentos rechazados.')
    reject_documents.short_description = "Rechazar documentos seleccionados"

@admin.register(DocumentRevision)
class DocumentRevisionAdmin(BaseModelAdmin):
    """
    Admin para revisiones de documentos
    """
    list_display = ('document', 'change_summary', 'is_auto_save', 'created_at', 'created_by')
    list_filter = ('is_auto_save', 'created_at')
    search_fields = ('document__title', 'change_summary')
    readonly_fields = ('document', 'content', 'is_auto_save')
    
    def has_add_permission(self, request):
        return False  # No permitir crear revisiones manualmente

@admin.register(DocumentView)
class DocumentViewAdmin(admin.ModelAdmin):
    """
    Admin para visualizaciones (solo lectura)
    """
    list_display = ('document', 'user', 'created_at', 'ip_address')
    list_filter = ('created_at', 'document__category')
    search_fields = ('document__title', 'user__username')
    readonly_fields = ('document', 'user', 'ip_address', 'user_agent', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False