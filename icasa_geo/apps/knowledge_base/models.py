"""
Modelos para el módulo Knowledge Base
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from apps.core.models import TimeStampedModel, ApprovalWorkflowModel, VersionedModel
from apps.core.utils import create_slug

class Category(MPTTModel, TimeStampedModel):
    """
    Estructura jerárquica para organizar documentos
    Soporta múltiples niveles: Capítulo → Sección → Subsección
    """
    name = models.CharField(max_length=200, verbose_name="Nombre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL amigable")
    description = models.TextField(blank=True, verbose_name="Descripción")
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name="Categoría padre"
    )
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icono")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Color")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class MPTTMeta:
        order_insertion_by = ['order', 'name']
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['tree_id', 'lft']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('knowledge_base:category_detail', kwargs={'slug': self.slug})
    
    @property
    def breadcrumb(self):
        """Genera breadcrumb automático"""
        return self.get_ancestors(include_self=True)
    
    @property
    def document_count(self):
        """Cuenta documentos en esta categoría y subcategorías"""
        return Document.objects.filter(
            category__in=self.get_descendants(include_self=True),
            status='approved'
        ).count()

class DocumentTemplate(TimeStampedModel):
    """
    Templates predefinidos para diferentes tipos de documentos
    """
    class TemplateType(models.TextChoices):
        POLICY = 'policy', 'Política'
        PROCEDURE = 'procedure', 'Procedimiento'
        MANUAL = 'manual', 'Manual'
        GUIDELINE = 'guideline', 'Directriz'
        FORM = 'form', 'Formulario'
    
    name = models.CharField(max_length=200, verbose_name="Nombre del template")
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
        verbose_name="Tipo de template"
    )
    content = RichTextUploadingField(verbose_name="Contenido del template")
    variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Variables disponibles",
        help_text="Variables que se pueden usar: {{company_name}}, {{current_date}}, etc."
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Template de Documento"
        verbose_name_plural = "Templates de Documentos"
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"

class Document(ApprovalWorkflowModel, VersionedModel):
    """
    Documento principal del Knowledge Base
    """
    title = models.CharField(max_length=300, verbose_name="Título")
    slug = models.SlugField(max_length=300, unique=True, verbose_name="URL amigable")
    category = TreeForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template utilizado"
    )
    content = RichTextUploadingField(verbose_name="Contenido")
    summary = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Resumen",
        help_text="Resumen breve del documento"
    )
    tags = TaggableManager(blank=True, verbose_name="Etiquetas")
    
    # Metadatos del documento
    document_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del documento",
        help_text="Ej: POL-001, PROC-002"
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de vigencia"
    )
    review_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de revisión"
    )
    
    # Configuración del documento
    is_public = models.BooleanField(default=False, verbose_name="Público")
    requires_acknowledgment = models.BooleanField(
        default=False,
        verbose_name="Requiere confirmación de lectura"
    )
    auto_save_enabled = models.BooleanField(default=True, verbose_name="Autoguardado activado")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['document_code']),
            models.Index(fields=['effective_date']),
        ]
    
    def __str__(self):
        return f"{self.document_code} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(f"{self.document_code}-{self.title}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('knowledge_base:document_detail', kwargs={'slug': self.slug})
    
    @property
    def breadcrumb_path(self):
        """Genera path completo con categoría"""
        path = list(self.category.get_ancestors(include_self=True))
        path.append(self)
        return path
    
    def render_content_with_variables(self):
        """Renderiza contenido reemplazando variables dinámicas"""
        from django.conf import settings
        from datetime import datetime
        
        content = self.content
        variables = {
            'company_name': getattr(settings, 'ICASA_SETTINGS', {}).get('COMPANY_NAME', 'ICASA'),
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'document_code': self.document_code,
            'document_title': self.title,
            'effective_date': self.effective_date.strftime('%d/%m/%Y') if self.effective_date else '',
            'version': f"v{self.version}",
        }
        
        for key, value in variables.items():
            content = content.replace(f'{{{{{key}}}}}', str(value))
        
        return content

class DocumentRevision(TimeStampedModel):
    """
    Historial de revisiones para autoguardado y control de cambios
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='revisions',
        verbose_name="Documento"
    )
    content = RichTextUploadingField(verbose_name="Contenido de la revisión")
    change_summary = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Resumen de cambios"
    )
    is_auto_save = models.BooleanField(default=False, verbose_name="Autoguardado")
    
    class Meta:
        verbose_name = "Revisión de Documento"
        verbose_name_plural = "Revisiones de Documentos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document.title} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class DocumentView(TimeStampedModel):
    """
    Tracking de visualizaciones de documentos
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name="Documento"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Visualización de Documento"
        verbose_name_plural = "Visualizaciones de Documentos"
        unique_together = ['document', 'user', 'created_at__date']
    
    def __str__(self):
        return f"{self.user.username} - {self.document.title}"