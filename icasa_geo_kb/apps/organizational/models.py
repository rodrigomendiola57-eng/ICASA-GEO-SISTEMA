from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel, ApprovalWorkflowModel



# PASO A: SEPARACIÓN DE "CAJAS" Y "PERSONAS"

class Position(TimeStampedModel):
    """LA CAJA - El Puesto existe siempre, aunque nadie trabaje ahí"""
    title = models.CharField(max_length=200, verbose_name="Título del Puesto")
    department = models.CharField(max_length=100, verbose_name="Departamento")
    level = models.IntegerField(default=1, verbose_name="Nivel Jerárquico")
    reports_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Reporta a")
    
    # Información del puesto (no de la persona)
    responsibilities = models.TextField(blank=True, verbose_name="Responsabilidades")
    kpis = models.JSONField(default=list, verbose_name="KPIs del Puesto")
    required_processes = models.JSONField(default=list, verbose_name="Procesos Requeridos")
    
    # Posición en el organigrama
    x_position = models.IntegerField(default=0, verbose_name="Posición X")
    y_position = models.IntegerField(default=0, verbose_name="Posición Y")
    
    class Meta:
        verbose_name = "Puesto (Caja)"
        verbose_name_plural = "Puestos (Cajas)"
        
    def __str__(self):
        return f"{self.title} - {self.department}"
    
    def get_current_employee(self, date=None):
        """Obtiene el empleado actual en este puesto"""
        if date is None:
            date = timezone.now().date()
        
        assignment = self.assignments.filter(
            start_date__lte=date,
            end_date__isnull=True
        ).first()
        
        return assignment.employee if assignment else None
    
    def is_vacant(self, date=None):
        """Verifica si el puesto está vacante en una fecha"""
        return self.get_current_employee(date) is None

class Employee(TimeStampedModel):
    """LA PERSONA - Viene y va"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="ID Empleado")
    first_name = models.CharField(max_length=100, verbose_name="Nombres")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    photo = models.ImageField(upload_to='employees/', blank=True, verbose_name="Foto")
    
    # Datos laborales
    hire_date = models.DateField(verbose_name="Fecha de Ingreso")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Empleado (Persona)"
        verbose_name_plural = "Empleados (Personas)"
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    def get_current_position(self, date=None):
        """Obtiene el puesto actual del empleado"""
        if date is None:
            date = timezone.now().date()
        
        assignment = self.assignments.filter(
            start_date__lte=date,
            end_date__isnull=True
        ).first()
        
        return assignment.position if assignment else None

class PositionAssignment(TimeStampedModel):
    """EL PEGAMENTO - Asignación de persona a puesto"""
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments')
    
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")
    
    # Metadatos de la asignación
    assignment_type = models.CharField(
        max_length=20,
        choices=[
            ('permanent', 'Permanente'),
            ('temporary', 'Temporal'),
            ('interim', 'Interino')
        ],
        default='permanent',
        verbose_name="Tipo de Asignación"
    )
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        unique_together = ['position', 'employee', 'start_date']
        
    def __str__(self):
        return f"{self.employee} → {self.position} ({self.start_date})"
    
    def is_active(self, date=None):
        """Verifica si la asignación está activa en una fecha"""
        if date is None:
            date = timezone.now().date()
        
        return (self.start_date <= date and 
                (self.end_date is None or self.end_date >= date))

# 2. 📋 PERFILES DE PUESTO (La "Biblia" del Puesto)
class JobProfile(TimeStampedModel):
    """Perfil completo del puesto - La Biblia del Puesto"""
    position = models.OneToOneField(Position, on_delete=models.CASCADE, related_name='profile')
    
    # Información básica
    objective = models.TextField(verbose_name="Objetivo del Puesto")
    education_required = models.CharField(max_length=200, verbose_name="Escolaridad Requerida")
    experience_required = models.CharField(max_length=200, verbose_name="Experiencia Requerida")
    
    # Competencias y habilidades
    technical_skills = models.JSONField(default=list, verbose_name="Habilidades Técnicas")
    soft_skills = models.JSONField(default=list, verbose_name="Habilidades Blandas")
    
    # Relación con procesos
    owned_processes = models.JSONField(default=list, verbose_name="Procesos que Posee")
    participates_in = models.JSONField(default=list, verbose_name="Procesos en los que Participa")
    
    # KPIs específicos
    performance_indicators = models.JSONField(default=list, verbose_name="Indicadores de Desempeño")
    
    class Meta:
        verbose_name = "Perfil de Puesto"
        verbose_name_plural = "Perfiles de Puesto"
        
    def __str__(self):
        return f"Perfil: {self.position.title}"

# 3. 🎯 MATRIZ DE COMPETENCIAS (Polivalencia)
class Skill(TimeStampedModel):
    """Habilidades/Competencias del sistema"""
    name = models.CharField(max_length=200, verbose_name="Nombre de la Habilidad")
    category = models.CharField(
        max_length=50,
        choices=[
            ('technical', 'Técnica'),
            ('safety', 'Seguridad'),
            ('quality', 'Calidad'),
            ('language', 'Idioma'),
            ('certification', 'Certificación'),
            ('software', 'Software')
        ],
        default='technical',
        verbose_name="Categoría"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_certification = models.BooleanField(default=False, verbose_name="Requiere Certificación")
    
    class Meta:
        verbose_name = "Habilidad/Competencia"
        verbose_name_plural = "Habilidades/Competencias"
        
    def __str__(self):
        return self.name

class EmployeeSkill(TimeStampedModel):
    """Matriz de competencias: Empleado vs Habilidad"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='employees')
    
    level = models.IntegerField(
        choices=[
            (1, 'Básico'),
            (2, 'Intermedio'),
            (3, 'Avanzado'),
            (4, 'Experto')
        ],
        default=1,
        verbose_name="Nivel"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('certified', 'Certificado'),
            ('training', 'En Capacitación'),
            ('needs_training', 'Necesita Capacitación'),
            ('expired', 'Certificación Vencida')
        ],
        default='needs_training',
        verbose_name="Estado"
    )
    
    certification_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Certificación")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Competencia del Empleado"
        verbose_name_plural = "Competencias de Empleados"
        unique_together = ['employee', 'skill']
        
    def __str__(self):
        return f"{self.employee} - {self.skill} (Nivel {self.level})"

# 4. 🤝 COMITÉS Y GRUPOS (Estructura "Invisible")
class Committee(TimeStampedModel):
    """Comités y grupos de trabajo"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Comité")
    type = models.CharField(
        max_length=50,
        choices=[
            ('quality', 'Comité de Calidad'),
            ('safety', 'Comité de Seguridad e Higiene'),
            ('ethics', 'Comité de Ética'),
            ('emergency', 'Brigada de Protección Civil'),
            ('improvement', 'Comité de Mejora Continua'),
            ('other', 'Otro')
        ],
        verbose_name="Tipo de Comité"
    )
    
    purpose = models.TextField(verbose_name="Propósito")
    responsibilities = models.JSONField(default=list, verbose_name="Responsabilidades")
    meeting_frequency = models.CharField(max_length=100, verbose_name="Frecuencia de Reuniones")
    
    # Miembros
    members = models.ManyToManyField(Employee, through='CommitteeMembership', verbose_name="Miembros")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Comité/Grupo"
        verbose_name_plural = "Comités/Grupos"
        
    def __str__(self):
        return self.name

class CommitteeMembership(TimeStampedModel):
    """Membresía en comités"""
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    role = models.CharField(
        max_length=50,
        choices=[
            ('president', 'Presidente'),
            ('secretary', 'Secretario'),
            ('member', 'Miembro'),
            ('coordinator', 'Coordinador')
        ],
        default='member',
        verbose_name="Rol"
    )
    
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")
    
    class Meta:
        verbose_name = "Membresía en Comité"
        verbose_name_plural = "Membresías en Comités"
        unique_together = ['committee', 'employee', 'start_date']
        
    def __str__(self):
        return f"{self.employee} - {self.committee} ({self.get_role_display()})"

class ProcessFlow(ApprovalWorkflowModel, TimeStampedModel):
    """Modelo para flujogramas de procesos"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Proceso")
    description = models.TextField(blank=True, verbose_name="Descripción")
    flow_data = models.JSONField(default=dict, verbose_name="Datos del Flujo")
    related_positions = models.ManyToManyField(Position, blank=True, verbose_name="Puestos Relacionados")
    
    class Meta:
        verbose_name = "Flujograma"
        verbose_name_plural = "Flujogramas"
        
    def __str__(self):
        return self.name

# Modelo para organigramas por departamento
class DepartmentalChart(TimeStampedModel):
    """Organigramas específicos por departamento"""
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
    
    # Archivo del organigrama
    chart_file = models.FileField(
        upload_to='organigramas/',
        blank=True,
        null=True,
        verbose_name="Archivo del Organigrama"
    )
    
    # Datos del organigrama (para organigramas creados en el sistema)
    chart_data = models.JSONField(default=dict, blank=True, verbose_name="Datos del Organigrama")
    
    # Metadatos
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Creado por"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('sandbox', 'Simulación'),
            ('pending_approval', 'Pendiente Aprobación'),
            ('active', 'Activo'),
            ('archived', 'Archivado')
        ],
        default='draft',
        verbose_name="Estado"
    )
    
    is_external = models.BooleanField(
        default=False,
        verbose_name="Archivo Externo",
        help_text="Indica si el organigrama fue subido desde un archivo externo"
    )
    
    # NUEVAS FUNCIONALIDADES CORPORATIVAS
    
    # Modo Sandbox
    is_sandbox = models.BooleanField(
        default=False,
        verbose_name="Modo Simulación",
        help_text="Indica si es una simulación/propuesta de reestructura"
    )
    
    parent_chart = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Organigrama Base",
        help_text="Organigrama del cual se clonó esta simulación"
    )
    
    # Control de Versiones
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name="Versión"
    )
    
    change_justification = models.TextField(
        blank=True,
        verbose_name="Justificación del Cambio",
        help_text="Razón por la cual se realizó este cambio"
    )
    
    # Flujo de Aprobación
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_charts',
        verbose_name="Aprobado por"
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Aprobación"
    )
    
    # Metadatos de Importación
    import_source = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Creación Manual'),
            ('excel', 'Importación Excel'),
            ('csv', 'Importación CSV'),
            ('visio', 'Importación Visio'),
            ('api', 'API Externa')
        ],
        default='manual',
        verbose_name="Origen de Datos"
    )
    
    import_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos de Importación"
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
    
    # NUEVOS MÉTODOS CORPORATIVOS
    
    def create_sandbox_copy(self, user, name_suffix="Simulación"):
        """Crear una copia en modo sandbox para simulaciones"""
        sandbox_copy = DepartmentalChart.objects.create(
            name=f"{self.name} - {name_suffix}",
            department=self.department,
            description=f"Simulación basada en: {self.name}",
            chart_data=self.chart_data.copy(),
            created_by=user,
            status='sandbox',
            is_sandbox=True,
            parent_chart=self,
            version=f"{self.version}-sandbox",
            import_source=self.import_source
        )
        return sandbox_copy
    
    def get_version_history(self):
        """Obtener historial de versiones"""
        if self.parent_chart:
            # Si es una copia, obtener historial del original
            base_chart = self.parent_chart
        else:
            base_chart = self
        
        # Obtener todas las versiones relacionadas
        versions = DepartmentalChart.objects.filter(
            models.Q(id=base_chart.id) | 
            models.Q(parent_chart=base_chart)
        ).order_by('-created_at')
        
        return versions
    
    def approve_and_publish(self, approver, justification=""):
        """Aprobar y publicar cambios"""
        from django.utils import timezone
        
        if self.is_sandbox:
            # Si es sandbox, crear nueva versión oficial
            if self.parent_chart:
                # Archivar versión anterior
                self.parent_chart.status = 'archived'
                self.parent_chart.save()
                
                # Incrementar versión
                old_version = self.parent_chart.version
                version_parts = old_version.split('.')
                new_minor = int(version_parts[1]) + 1
                new_version = f"{version_parts[0]}.{new_minor}"
            else:
                new_version = "2.0"
            
            # Actualizar este organigrama
            self.is_sandbox = False
            self.status = 'active'
            self.version = new_version
            self.approved_by = approver
            self.approved_at = timezone.now()
            self.change_justification = justification
            self.save()
            
            return True
        
        return False
    
    def get_changes_summary(self):
        """Obtener resumen de cambios respecto a la versión anterior"""
        if not self.parent_chart:
            return "Versión inicial"
        
        # Comparar datos del organigrama
        old_data = self.parent_chart.chart_data
        new_data = self.chart_data
        
        changes = {
            'positions_added': [],
            'positions_removed': [],
            'positions_moved': [],
            'summary': ''
        }
        
        # Aquí iría la lógica de comparación
        # Por simplicidad, retornamos un resumen básico
        changes['summary'] = f"Cambios realizados el {self.updated_at.strftime('%d/%m/%Y')}"
        
        return changes
    
    def get_changes_summary(self):
        """Obtener resumen de cambios respecto a la versión anterior"""
        if not self.parent_chart:
            return "Versión inicial"
        
        # Comparar datos del organigrama
        old_data = self.parent_chart.chart_data
        new_data = self.chart_data
        
        changes = {
            'positions_added': [],
            'positions_removed': [],
            'positions_moved': [],
            'summary': ''
        }
        
        # Aquí iría la lógica de comparación
        # Por simplicidad, retornamos un resumen básico
        changes['summary'] = f"Cambios realizados el {self.updated_at.strftime('%d/%m/%Y')}"
        
        return changes

# Modelo para el organigrama principal
class OrganizationalChart(ApprovalWorkflowModel, TimeStampedModel):
    """Configuración del organigrama principal"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Organigrama")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_main = models.BooleanField(default=False, verbose_name="Organigrama Principal")
    
    class Meta:
        verbose_name = "Organigrama"
        verbose_name_plural = "Organigramas"
        
    def __str__(self):
        return self.name

# MODELOS CORPORATIVOS (Definidos después de DepartmentalChart)

class OrganizationalSnapshot(TimeStampedModel):
    """Instantáneas del organigrama para control de versiones"""
    chart = models.ForeignKey(DepartmentalChart, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_data = models.JSONField(verbose_name="Datos de la Instantánea")
    version_tag = models.CharField(max_length=50, verbose_name="Etiqueta de Versión")
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Instantánea Organizacional"
        verbose_name_plural = "Instantáneas Organizacionales"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.chart.name} - {self.version_tag}"

class ImportLog(TimeStampedModel):
    """Registro de importaciones de datos"""
    chart = models.ForeignKey(DepartmentalChart, on_delete=models.CASCADE, related_name='import_logs')
    import_type = models.CharField(
        max_length=20,
        choices=[
            ('excel', 'Excel/CSV'),
            ('visio', 'Microsoft Visio'),
            ('api', 'API Externa'),
            ('json', 'Archivo JSON')
        ]
    )
    file_name = models.CharField(max_length=255, blank=True)
    records_processed = models.IntegerField(default=0)
    records_success = models.IntegerField(default=0)
    records_errors = models.IntegerField(default=0)
    error_log = models.JSONField(default=list, blank=True)
    imported_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Registro de Importación"
        verbose_name_plural = "Registros de Importación"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Importación {self.import_type} - {self.created_at.strftime('%d/%m/%Y')}"

class ApprovalWorkflow(TimeStampedModel):
    """Flujo de aprobación para cambios organizacionales"""
    chart = models.ForeignKey(DepartmentalChart, on_delete=models.CASCADE, related_name='approvals')
    requested_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='approval_requests')
    approver = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='approvals_given')
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('approved', 'Aprobado'),
            ('rejected', 'Rechazado'),
            ('cancelled', 'Cancelado')
        ],
        default='pending'
    )
    
    request_notes = models.TextField(verbose_name="Notas de Solicitud")
    approval_notes = models.TextField(blank=True, verbose_name="Notas de Aprobación")
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Flujo de Aprobación"
        verbose_name_plural = "Flujos de Aprobación"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Aprobación {self.chart.name} - {self.get_status_display()}"

# FLOWCHART MODELS - Agregados directamente al archivo models.py

class ProcessCategory(TimeStampedModel):
    """Categorías de procesos para organización"""
    CATEGORY_TYPES = [
        ('operational', 'Procesos Operativos'),
        ('strategic', 'Procesos Estratégicos'),
        ('support', 'Procesos de Soporte'),
        ('audit', 'Procesos de Auditoría'),
        ('quality', 'Procesos de Calidad'),
        ('safety', 'Procesos de Seguridad'),
        ('finance', 'Procesos Financieros'),
        ('hr', 'Procesos de RRHH'),
        ('it', 'Procesos de TI'),
        ('legal', 'Procesos Legales'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="Tipo")
    color = models.CharField(max_length=7, default="#059669", verbose_name="Color")
    icon = models.CharField(max_length=50, default="fas fa-sitemap", verbose_name="Icono")
    
    class Meta:
        verbose_name = "Categoría de Proceso"
        verbose_name_plural = "Categorías de Procesos"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class FlowchartProcess(TimeStampedModel):
    """Flujograma principal"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    
    COMPLEXITY_LEVELS = [
        ('simple', 'Simple (1-5 pasos)'),
        ('medium', 'Medio (6-15 pasos)'),
        ('complex', 'Complejo (16+ pasos)'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título del Proceso")
    description = models.TextField(verbose_name="Descripción")
    category = models.ForeignKey(ProcessCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_flowchart_processes', verbose_name="Propietario")
    responsible_department = models.CharField(max_length=100, verbose_name="Departamento Responsable")
    
    # Metadatos del proceso
    complexity_level = models.CharField(max_length=10, choices=COMPLEXITY_LEVELS, default='simple', verbose_name="Nivel de Complejidad")
    estimated_duration = models.DurationField(null=True, blank=True, verbose_name="Duración Estimada")
    frequency = models.CharField(max_length=50, blank=True, verbose_name="Frecuencia de Ejecución")
    
    # Control de versiones y aprobación
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    is_template = models.BooleanField(default=False, verbose_name="Es Plantilla")
    parent_flow = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Proceso Padre")
    version = models.CharField(max_length=20, default='1.0', verbose_name="Versión")
    
    # Campos de aprobación
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_flowchart_processes', verbose_name="Aprobado por")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    approval_notes = models.TextField(blank=True, verbose_name="Notas de Aprobación")
    
    # Datos del diagrama
    diagram_data = models.JSONField(default=dict, verbose_name="Datos del Diagrama")
    canvas_settings = models.JSONField(default=dict, verbose_name="Configuración del Canvas")
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizaciones")
    last_executed = models.DateTimeField(null=True, blank=True, verbose_name="Última Ejecución")
    
    class Meta:
        verbose_name = "Proceso de Flujograma"
        verbose_name_plural = "Procesos de Flujogramas"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"

class FlowchartTemplate(TimeStampedModel):
    """Plantillas predefinidas de flujogramas"""
    TEMPLATE_CATEGORIES = [
        ('hr', 'Recursos Humanos'),
        ('finance', 'Finanzas'),
        ('operations', 'Operaciones'),
        ('quality', 'Calidad'),
        ('it', 'Tecnología'),
        ('audit', 'Auditoría'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la Plantilla")
    description = models.TextField(verbose_name="Descripción")
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORIES, verbose_name="Categoría")
    template_data = models.JSONField(verbose_name="Datos de la Plantilla")
    difficulty_level = models.CharField(max_length=10, choices=FlowchartProcess.COMPLEXITY_LEVELS, verbose_name="Nivel de Dificultad")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Veces Utilizada")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Plantilla de Flujograma"
        verbose_name_plural = "Plantillas de Flujogramas"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name