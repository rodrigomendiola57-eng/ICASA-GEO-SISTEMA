from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        abstract = True

class ApprovalWorkflowModel(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)s_created", verbose_name="Creado por")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_approved", verbose_name="Aprobado por")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")
    
    class Meta:
        abstract = True
    
    def approve(self, user):
        from django.utils import timezone
        from apps.core.notifications import NotificationService
        
        old_status = self.status
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
        
        # Enviar notificación si cambió el estado
        if old_status != 'approved':
            NotificationService.notify_document_approved(self, user)
    
    def reject(self, user, reason=None):
        from apps.core.notifications import NotificationService
        
        old_status = self.status
        self.status = 'rejected'
        self.approved_by = user
        self.save()
        
        # Enviar notificación si cambió el estado
        if old_status != 'rejected':
            NotificationService.notify_document_rejected(self, user, reason)
    
    def submit_for_review(self):
        from apps.core.notifications import NotificationService
        
        old_status = self.status
        self.status = 'review'
        self.save()
        
        # Enviar notificación si cambió el estado
        if old_status != 'review':
            NotificationService.notify_document_review(self, self.created_by)

class VersionedModel(models.Model):
    version = models.PositiveIntegerField(default=1, verbose_name="Versión")
    
    class Meta:
        abstract = True

class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = [
        ('document_created', 'Documento Creado'),
        ('document_approved', 'Documento Aprobado'),
        ('document_rejected', 'Documento Rechazado'),
        ('document_review', 'Documento en Revisión'),
        ('user_mentioned', 'Usuario Mencionado'),
        ('system_update', 'Actualización del Sistema'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Destinatario")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications', verbose_name="Remitente")
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name="Tipo")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Prioridad")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    
    # Referencia genérica al objeto relacionado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de lectura")
    
    # URL de acción (opcional)
    action_url = models.URLField(blank=True, null=True, verbose_name="URL de acción")
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def get_priority_class(self):
        """Retorna clase CSS según prioridad"""
        priority_classes = {
            'low': 'bg-gray-100 text-gray-800',
            'medium': 'bg-blue-100 text-blue-800',
            'high': 'bg-yellow-100 text-yellow-800',
            'urgent': 'bg-red-100 text-red-800',
        }
        return priority_classes.get(self.priority, 'bg-gray-100 text-gray-800')

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Preferencias por tipo de notificación
    email_document_created = models.BooleanField(default=True, verbose_name="Email: Documento creado")
    email_document_approved = models.BooleanField(default=True, verbose_name="Email: Documento aprobado")
    email_document_rejected = models.BooleanField(default=True, verbose_name="Email: Documento rechazado")
    email_document_review = models.BooleanField(default=True, verbose_name="Email: Documento en revisión")
    
    web_document_created = models.BooleanField(default=True, verbose_name="Web: Documento creado")
    web_document_approved = models.BooleanField(default=True, verbose_name="Web: Documento aprobado")
    web_document_rejected = models.BooleanField(default=True, verbose_name="Web: Documento rechazado")
    web_document_review = models.BooleanField(default=True, verbose_name="Web: Documento en revisión")
    
    class Meta:
        verbose_name = "Preferencia de Notificación"
        verbose_name_plural = "Preferencias de Notificación"
    
    def __str__(self):
        return f"Preferencias de {self.user.username}"