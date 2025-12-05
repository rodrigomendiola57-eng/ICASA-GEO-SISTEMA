from django.contrib import admin
from .models import ProcedureCategory, Procedure, ProcedureStep, ProcedureTemplate, ProcedureAttachment

@admin.register(ProcedureCategory)
class ProcedureCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']

class ProcedureStepInline(admin.TabularInline):
    model = ProcedureStep
    extra = 1
    ordering = ['step_number']

class ProcedureAttachmentInline(admin.TabularInline):
    model = ProcedureAttachment
    extra = 0

@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'department', 'status', 'criticality', 'owner', 'updated_at']
    list_filter = ['status', 'category', 'department', 'criticality', 'frequency']
    search_fields = ['title', 'code', 'objective']
    inlines = [ProcedureStepInline, ProcedureAttachmentInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'code', 'category', 'department')
        }),
        ('Contenido', {
            'fields': ('objective', 'scope', 'content')
        }),
        ('Clasificación', {
            'fields': ('criticality', 'frequency', 'tags')
        }),
        ('Responsabilidades', {
            'fields': ('owner', 'responsible_position')
        }),
        ('Control de Versiones', {
            'fields': ('version', 'effective_date', 'review_date', 'expiry_date')
        }),
        ('Estado', {
            'fields': ('status', 'estimated_duration')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProcedureTemplate)
class ProcedureTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'usage_count', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']