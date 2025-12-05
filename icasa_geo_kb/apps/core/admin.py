from django.contrib import admin
from .models import Notification, NotificationPreference

class BaseModelAdmin(admin.ModelAdmin):
    """Admin base para modelos con auditoría"""
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            if hasattr(obj, 'created_by'):
                obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('recipient', 'sender', 'notification_type', 'priority')
        }),
        ('Contenido', {
            'fields': ('title', 'message', 'action_url')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_document_created', 'web_document_created')
    search_fields = ('user__username', 'user__email')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Preferencias de Email', {
            'fields': (
                'email_document_created', 'email_document_approved', 
                'email_document_rejected', 'email_document_review'
            )
        }),
        ('Preferencias Web', {
            'fields': (
                'web_document_created', 'web_document_approved', 
                'web_document_rejected', 'web_document_review'
            )
        })
    )