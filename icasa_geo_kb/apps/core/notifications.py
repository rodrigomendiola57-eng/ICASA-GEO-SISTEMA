from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Notification, NotificationPreference

class NotificationService:
    """Servicio centralizado para gestionar notificaciones"""
    
    @staticmethod
    def create_notification(recipient, notification_type, title, message, 
                          sender=None, content_object=None, priority='medium', action_url=None):
        """Crear una nueva notificación"""
        
        # Verificar preferencias del usuario
        preferences, created = NotificationPreference.objects.get_or_create(user=recipient)
        
        # Verificar si el usuario quiere recibir este tipo de notificación web
        web_pref_field = f"web_{notification_type}"
        if hasattr(preferences, web_pref_field) and not getattr(preferences, web_pref_field):
            return None
        
        # Crear la notificación
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            content_object=content_object,
            action_url=action_url
        )
        
        return notification
    
    @staticmethod
    def notify_document_created(document, sender):
        """Notificar cuando se crea un documento"""
        # Notificar a gerentes y administradores
        managers = User.objects.filter(groups__name__in=['Gerentes', 'Administradores ICASA'])
        
        for manager in managers:
            if manager != sender:  # No notificar al creador
                NotificationService.create_notification(
                    recipient=manager,
                    sender=sender,
                    notification_type='document_created',
                    title=f'Nuevo documento: {document.title}',
                    message=f'{sender.get_full_name() or sender.username} ha creado un nuevo documento en {document.category.name}',
                    content_object=document,
                    priority='medium',
                    action_url=reverse('knowledge_base:document_detail', kwargs={'slug': document.slug})
                )
    
    @staticmethod
    def notify_document_review(document, sender):
        """Notificar cuando un documento se envía a revisión"""
        # Notificar a revisores, gerentes y administradores
        reviewers = User.objects.filter(groups__name__in=['Revisores', 'Gerentes', 'Administradores ICASA'])
        
        for reviewer in reviewers:
            if reviewer != sender:
                NotificationService.create_notification(
                    recipient=reviewer,
                    sender=sender,
                    notification_type='document_review',
                    title=f'Documento pendiente de revisión: {document.title}',
                    message=f'El documento "{document.title}" está esperando tu revisión',
                    content_object=document,
                    priority='high',
                    action_url=reverse('knowledge_base:document_detail', kwargs={'slug': document.slug})
                )
    
    @staticmethod
    def notify_document_approved(document, approver):
        """Notificar cuando un documento es aprobado"""
        # Notificar al creador del documento
        NotificationService.create_notification(
            recipient=document.created_by,
            sender=approver,
            notification_type='document_approved',
            title=f'Documento aprobado: {document.title}',
            message=f'Tu documento "{document.title}" ha sido aprobado por {approver.get_full_name() or approver.username}',
            content_object=document,
            priority='medium',
            action_url=reverse('knowledge_base:document_detail', kwargs={'slug': document.slug})
        )
    
    @staticmethod
    def notify_document_rejected(document, rejector, reason=None):
        """Notificar cuando un documento es rechazado"""
        message = f'Tu documento "{document.title}" ha sido rechazado por {rejector.get_full_name() or rejector.username}'
        if reason:
            message += f'. Motivo: {reason}'
        
        NotificationService.create_notification(
            recipient=document.created_by,
            sender=rejector,
            notification_type='document_rejected',
            title=f'Documento rechazado: {document.title}',
            message=message,
            content_object=document,
            priority='high',
            action_url=reverse('knowledge_base:document_detail', kwargs={'slug': document.slug})
        )
    
    @staticmethod
    def notify_system_update(title, message, priority='medium'):
        """Notificar actualizaciones del sistema a todos los usuarios"""
        users = User.objects.filter(is_active=True)
        
        for user in users:
            NotificationService.create_notification(
                recipient=user,
                notification_type='system_update',
                title=title,
                message=message,
                priority=priority
            )
    
    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=None):
        """Obtener notificaciones de un usuario"""
        notifications = Notification.objects.filter(recipient=user)
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    @staticmethod
    def get_unread_count(user):
        """Obtener cantidad de notificaciones no leídas"""
        return Notification.objects.filter(recipient=user, is_read=False).count()
    
    @staticmethod
    def mark_all_as_read(user):
        """Marcar todas las notificaciones como leídas"""
        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)