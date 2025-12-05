"""
Modelos simplificados para pruebas rápidas del módulo organizacional
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel

class SimpleDepartmentalChart(TimeStampedModel):
    """Modelo simplificado para organigramas departamentales"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Organigrama")
    department = models.CharField(
        max_length=100,
        choices=[
            ('Administrativo', 'Administrativo'),
            ('Comercial', 'Comercial'),
            ('Operaciones', 'Operaciones'),
            ('RRHH', 'Recursos Humanos'),
            ('Finanzas', 'Finanzas'),
            ('Mantenimiento', 'Mantenimiento'),
        ],
        verbose_name="Departamento"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Archivo del organigrama (opcional)
    chart_file = models.FileField(
        upload_to='organigramas/',
        blank=True,
        null=True,
        verbose_name="Archivo del Organigrama"
    )
    
    # Metadatos básicos
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Creado por"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('active', 'Activo'),
            ('archived', 'Archivado')
        ],
        default='draft',
        verbose_name="Estado"
    )
    
    is_external = models.BooleanField(
        default=False,
        verbose_name="Archivo Externo"
    )
    
    class Meta:
        verbose_name = "Organigrama Departamental"
        verbose_name_plural = "Organigramas Departamentales"
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.name} - {self.department}"
    
    def get_file_extension(self):
        """Obtiene la extensión del archivo"""
        if self.chart_file:
            return self.chart_file.name.split('.')[-1].lower()
        return None
    
    def is_image(self):
        """Verifica si el archivo es una imagen"""
        ext = self.get_file_extension()
        return ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']
    
    def is_pdf(self):
        """Verifica si el archivo es un PDF"""
        return self.get_file_extension() == 'pdf'