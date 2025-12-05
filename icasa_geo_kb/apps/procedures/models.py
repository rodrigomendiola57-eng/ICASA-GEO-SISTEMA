from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel, ApprovalWorkflowModel

class ProcedureCategory(TimeStampedModel):
    """Categorías de procedimientos"""
    CATEGORY_TYPES = [
        ('operational', 'Procedimientos Operativos'),
        ('administrative', 'Procedimientos Administrativos'),
        ('quality', 'Procedimientos de Calidad'),
        ('safety', 'Procedimientos de Seguridad'),
        ('audit', 'Procedimientos de Auditoría'),
        ('transport', 'Procedimientos de Transporte'),
        ('maintenance', 'Procedimientos de Mantenimiento'),
        ('hr', 'Procedimientos de RRHH'),
        ('finance', 'Procedimientos Financieros'),
        ('legal', 'Procedimientos Legales'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre")
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES, verbose_name="Tipo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    color = models.CharField(max_length=7, default="#3498db", verbose_name="Color")
    icon = models.CharField(max_length=50, default="fas fa-file-alt", verbose_name="Icono")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Categoría de Procedimiento"
        verbose_name_plural = "Categorías de Procedimientos"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Procedure(ApprovalWorkflowModel):
    """Procedimiento principal"""
    CRITICALITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
        ('on_demand', 'Por Demanda'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    
    # Información básica
    title = models.CharField(max_length=300, verbose_name="Título")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    category = models.ForeignKey(ProcedureCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    department = models.CharField(max_length=100, verbose_name="Departamento")
    
    # Contenido
    objective = models.TextField(verbose_name="Objetivo")
    scope = models.TextField(verbose_name="Alcance")
    content = models.TextField(verbose_name="Contenido")
    
    # Clasificación
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='medium', verbose_name="Criticidad")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Frecuencia")
    
    # Responsabilidades
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_procedures', verbose_name="Propietario")
    responsible_position = models.CharField(max_length=200, verbose_name="Puesto Responsable")
    
    # Control de versiones
    version = models.CharField(max_length=20, default="1.0", verbose_name="Versión")
    effective_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Vigencia")
    review_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Revisión")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    
    # Metadatos
    tags = models.CharField(max_length=500, blank=True, verbose_name="Etiquetas")
    estimated_duration = models.PositiveIntegerField(null=True, blank=True, verbose_name="Duración Estimada (minutos)")
    
    class Meta:
        verbose_name = "Procedimiento"
        verbose_name_plural = "Procedimientos"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def is_expired(self):
        """Verificar si el procedimiento está vencido"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
    
    def days_to_expiry(self):
        """Días hasta el vencimiento"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

class ProcedureStep(TimeStampedModel):
    """Pasos del procedimiento"""
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='steps', verbose_name="Procedimiento")
    step_number = models.PositiveIntegerField(verbose_name="Número de Paso")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    responsible = models.CharField(max_length=200, verbose_name="Responsable")
    estimated_time = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tiempo Estimado (minutos)")
    is_critical = models.BooleanField(default=False, verbose_name="Paso Crítico")
    
    class Meta:
        verbose_name = "Paso de Procedimiento"
        verbose_name_plural = "Pasos de Procedimientos"
        ordering = ['procedure', 'step_number']
        unique_together = ['procedure', 'step_number']
    
    def __str__(self):
        return f"{self.procedure.code} - Paso {self.step_number}: {self.title}"

class ProcedureTemplate(TimeStampedModel):
    """Plantillas de procedimientos"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    category = models.ForeignKey(ProcedureCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    description = models.TextField(verbose_name="Descripción")
    template_content = models.JSONField(verbose_name="Contenido de Plantilla")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Veces Usado")
    
    class Meta:
        verbose_name = "Plantilla de Procedimiento"
        verbose_name_plural = "Plantillas de Procedimientos"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name

class ProcedureAttachment(TimeStampedModel):
    """Archivos adjuntos a procedimientos"""
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='attachments', verbose_name="Procedimiento")
    name = models.CharField(max_length=200, verbose_name="Nombre")
    file = models.FileField(upload_to='procedures/attachments/', verbose_name="Archivo")
    file_type = models.CharField(max_length=50, verbose_name="Tipo de Archivo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
    
    def __str__(self):
        return f"{self.procedure.code} - {self.name}"