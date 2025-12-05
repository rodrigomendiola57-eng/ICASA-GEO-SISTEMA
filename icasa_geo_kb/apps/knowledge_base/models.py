from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField
from apps.core.models import TimeStampedModel, ApprovalWorkflowModel

class Category(MPTTModel, TimeStampedModel):
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
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class MPTTMeta:
        order_insertion_by = ['name']
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['tree_id', 'lft']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('knowledge_base:category_detail', kwargs={'slug': self.slug})
    
    def get_document_count(self):
        """Retorna el número de documentos en esta categoría y subcategorías"""
        descendants = self.get_descendants(include_self=True)
        return Document.objects.filter(category__in=descendants, status='approved').count()

class Document(ApprovalWorkflowModel):
    title = models.CharField(max_length=300, verbose_name="Título")
    slug = models.SlugField(max_length=300, unique=True, verbose_name="URL amigable")
    category = TreeForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    content = RichTextUploadingField(verbose_name="Contenido", config_name='icasa_document')
    summary = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Resumen"
    )
    tags = TaggableManager(blank=True, verbose_name="Etiquetas")
    document_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del documento"
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de vigencia"
    )
    version = models.PositiveIntegerField(default=1, verbose_name="Versión")
    is_public = models.BooleanField(default=False, verbose_name="Público")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.document_code} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.document_code:
            # Generar código automático basado en categoría y contador
            category_prefix = self.category.name[:3].upper() if self.category else 'DOC'
            count = Document.objects.filter(category=self.category).count() + 1
            self.document_code = f"{category_prefix}-{count:03d}"
        
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f"{self.document_code}-{self.title}")
        
        super().save(*args, **kwargs)
    
    @property
    def tags_list(self):
        """Retorna lista de tags como strings"""
        return [tag.name for tag in self.tags.all()]
    
    def get_absolute_url(self):
        return reverse('knowledge_base:document_detail', kwargs={'slug': self.slug})