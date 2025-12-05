"""
Signals para Knowledge Base
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Document
from .tasks import send_approval_notification

@receiver(post_save, sender=Document)
def document_status_changed(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando cambia el estado de un documento
    """
    if not created:  # Solo para actualizaciones
        # Obtener el estado anterior
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            
            # Si el estado cambió a aprobado o rechazado, enviar notificación
            if (old_instance.status != instance.status and 
                instance.status in ['approved', 'rejected']):
                
                send_approval_notification.delay(
                    instance.id, 
                    instance.status
                )
                
        except Document.DoesNotExist:
            pass

@receiver(pre_save, sender=Document)
def document_pre_save(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar un documento
    """
    # Auto-generar slug si no existe
    if not instance.slug:
        from apps.core.utils import create_slug
        instance.slug = create_slug(f"{instance.document_code}-{instance.title}")
    
    # Validar código de documento único
    if instance.pk:
        existing = Document.objects.filter(
            document_code=instance.document_code
        ).exclude(pk=instance.pk)
        
        if existing.exists():
            raise ValueError(f"Ya existe un documento con el código {instance.document_code}")