"""
Configuración del admin para Core
"""
from django.contrib import admin

# Configuraciones base para admin que pueden ser heredadas por otras apps
class BaseModelAdmin(admin.ModelAdmin):
    """
    Configuración base para modelos con TimeStampedModel
    """
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un objeto nuevo
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class ApprovalModelAdmin(BaseModelAdmin):
    """
    Configuración base para modelos con ApprovalWorkflowModel
    """
    list_filter = ('status', 'created_at', 'approved_at')
    readonly_fields = BaseModelAdmin.readonly_fields + ('approved_by', 'approved_at')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.status == 'approved':
            # Si está aprobado, hacer más campos de solo lectura
            readonly_fields.extend(['status'])
        return readonly_fields