"""
Modelos base para ICASA-GEO
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="%(class)s_created",
        verbose_name="Creado por"
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="%(class)s_updated",
        verbose_name="Actualizado por"
    )
    
    class Meta:
        abstract = True

class ApprovalWorkflowModel(TimeStampedModel):
    """
    Modelo abstracto para flujo de aprobación
    """
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        REVIEW = 'review', 'En Revisión'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        ARCHIVED = 'archived', 'Archivado'
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Estado"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_approved",
        verbose_name="Aprobado por"
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")
    rejection_reason = models.TextField(blank=True, verbose_name="Motivo de rechazo")
    
    class Meta:
        abstract = True
    
    def approve(self, user):
        """Aprobar el elemento"""
        self.status = self.StatusChoices.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, user, reason=""):
        """Rechazar el elemento"""
        self.status = self.StatusChoices.REJECTED
        self.rejection_reason = reason
        self.updated_by = user
        self.save()

class VersionedModel(TimeStampedModel):
    """
    Modelo abstracto para control de versiones
    """
    version = models.PositiveIntegerField(default=1, verbose_name="Versión")
    is_current = models.BooleanField(default=True, verbose_name="Versión actual")
    version_notes = models.TextField(blank=True, verbose_name="Notas de la versión")
    
    class Meta:
        abstract = True
    
    def create_new_version(self):
        """Crear una nueva versión del objeto"""
        # Marcar la versión actual como no actual
        self.__class__.objects.filter(pk=self.pk).update(is_current=False)
        
        # Crear nueva versión
        self.pk = None
        self.version += 1
        self.is_current = True
        self.save()
        return self