from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from apps.core.admin import BaseModelAdmin
from .models import Category, Document

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, BaseModelAdmin):
    list_display = ('tree_actions', 'indented_title', 'is_active', 'created_at')
    list_display_links = ('indented_title',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Apariencia', {
            'fields': ('icon', 'color')
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

@admin.register(Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = (
        'document_code', 'title', 'category', 'status', 
        'version', 'effective_date', 'created_at'
    )
    list_filter = (
        'status', 'category', 'is_public', 'effective_date', 'created_at'
    )
    search_fields = ('title', 'document_code', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'document_code', 'category')
        }),
        ('Contenido', {
            'fields': ('summary', 'content', 'tags')
        }),
        ('Metadatos', {
            'fields': ('effective_date', 'version', 'is_public')
        }),
        ('Workflow', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_documents']
    
    def approve_documents(self, request, queryset):
        count = 0
        for document in queryset:
            if document.status == 'review':
                document.approve(request.user)
                count += 1
        
        self.message_user(request, f'{count} documentos aprobados exitosamente.')
    approve_documents.short_description = "Aprobar documentos seleccionados"