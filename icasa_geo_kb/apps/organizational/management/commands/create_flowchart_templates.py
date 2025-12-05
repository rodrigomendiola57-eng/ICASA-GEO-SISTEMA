from django.core.management.base import BaseCommand
from apps.organizational.models import ProcessCategory, FlowchartTemplate
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crear plantillas predefinidas de flujogramas para ICASA'

    def handle(self, *args, **options):
        # Crear categorías si no existen
        categories = [
            ('operational', 'Procesos Operativos', '#059669', 'fas fa-cogs'),
            ('strategic', 'Procesos Estratégicos', '#3b82f6', 'fas fa-chess'),
            ('support', 'Procesos de Soporte', '#8b5cf6', 'fas fa-hands-helping'),
            ('audit', 'Procesos de Auditoría', '#ef4444', 'fas fa-search'),
        ]
        
        for cat_type, name, color, icon in categories:
            category, created = ProcessCategory.objects.get_or_create(
                category_type=cat_type,
                defaults={
                    'name': name,
                    'color': color,
                    'icon': icon,
                    'description': f'Categoría para {name.lower()}'
                }
            )
            if created:
                self.stdout.write(f'Categoría creada: {name}')

        # Obtener usuario admin para asignar como creador
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()

        # Plantillas predefinidas
        templates = [
            {
                'name': 'Proceso de Compras',
                'description': 'Flujo estándar para el proceso de adquisiciones y compras',
                'category': 'hr',
                'difficulty_level': 'medium',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Solicitud de Compra] --> B{¿Presupuesto Aprobado?}
    B -->|Sí| C[Cotización Proveedores]
    B -->|No| D[Solicitar Aprobación Presupuestal]
    D --> E{¿Aprobado?}
    E -->|Sí| C
    E -->|No| F[Rechazado]
    C --> G[Evaluación de Propuestas]
    G --> H[Selección de Proveedor]
    H --> I[Orden de Compra]
    I --> J[Recepción de Mercancía]
    J --> K[Verificación de Calidad]
    K --> L{¿Conforme?}
    L -->|Sí| M[Autorización de Pago]
    L -->|No| N[Devolución/Reclamo]
    M --> O[Fin del Proceso]
    N --> O''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'medium'
                }
            },
            {
                'name': 'Reclutamiento y Selección',
                'description': 'Proceso completo de contratación de personal',
                'category': 'hr',
                'difficulty_level': 'complex',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Requisición de Personal] --> B[Análisis del Puesto]
    B --> C[Publicación de Vacante]
    C --> D[Recepción de CVs]
    D --> E[Filtro Inicial]
    E --> F{¿Candidatos Aptos?}
    F -->|No| G[Ampliar Búsqueda]
    G --> C
    F -->|Sí| H[Entrevista Inicial RRHH]
    H --> I{¿Pasa Filtro?}
    I -->|No| J[Descartado]
    I -->|Sí| K[Entrevista Técnica]
    K --> L{¿Aprobado?}
    L -->|No| J
    L -->|Sí| M[Verificación de Referencias]
    M --> N[Oferta Laboral]
    N --> O{¿Acepta?}
    O -->|No| P[Fin - No Contratado]
    O -->|Sí| Q[Contratación]
    Q --> R[Inducción]
    R --> S[Fin del Proceso]''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'complex'
                }
            },
            {
                'name': 'Auditoría Interna',
                'description': 'Proceso estándar de auditoría interna',
                'category': 'audit',
                'difficulty_level': 'complex',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Planificación de Auditoría] --> B[Definir Alcance y Objetivos]
    B --> C[Asignación de Equipo Auditor]
    C --> D[Revisión Documental]
    D --> E[Programa de Auditoría]
    E --> F[Reunión de Apertura]
    F --> G[Ejecución de Auditoría]
    G --> H[Recopilación de Evidencias]
    H --> I[Análisis de Hallazgos]
    I --> J{¿Hay No Conformidades?}
    J -->|Sí| K[Documentar No Conformidades]
    J -->|No| L[Documentar Observaciones]
    K --> M[Reunión de Cierre]
    L --> M
    M --> N[Elaboración de Informe]
    N --> O[Entrega de Informe]
    O --> P[Plan de Acciones Correctivas]
    P --> Q[Seguimiento]
    Q --> R[Cierre de Auditoría]''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'complex'
                }
            },
            {
                'name': 'Flujo de Aprobación Simple',
                'description': 'Proceso básico de aprobación de documentos',
                'category': 'operations',
                'difficulty_level': 'simple',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Solicitud de Aprobación] --> B[Revisión Inicial]
    B --> C{¿Documentación Completa?}
    C -->|No| D[Solicitar Documentos Faltantes]
    D --> A
    C -->|Sí| E[Evaluación Técnica]
    E --> F{¿Cumple Criterios?}
    F -->|No| G[Rechazar con Observaciones]
    F -->|Sí| H[Aprobación Nivel 1]
    H --> I{¿Requiere Aprobación Superior?}
    I -->|No| J[Aprobado]
    I -->|Sí| K[Enviar a Nivel Superior]
    K --> L[Aprobación Nivel 2]
    L --> M{¿Aprobado?}
    M -->|No| N[Rechazado]
    M -->|Sí| J
    G --> O[Fin del Proceso]
    J --> O
    N --> O''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'simple'
                }
            },
            {
                'name': 'Proceso de Capacitación',
                'description': 'Flujo para gestión de capacitaciones del personal',
                'category': 'hr',
                'difficulty_level': 'medium',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Detección de Necesidad] --> B[Evaluación de Competencias]
    B --> C[Diseño del Programa]
    C --> D[Aprobación Presupuestal]
    D --> E{¿Aprobado?}
    E -->|No| F[Buscar Alternativas]
    F --> C
    E -->|Sí| G[Selección de Instructor]
    G --> H[Programación de Fechas]
    H --> I[Convocatoria]
    I --> J[Ejecución de Capacitación]
    J --> K[Evaluación de Aprendizaje]
    K --> L[Evaluación de Satisfacción]
    L --> M[Certificación]
    M --> N[Seguimiento Post-Capacitación]
    N --> O[Fin del Proceso]''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'medium'
                }
            },
            {
                'name': 'Control de Calidad',
                'description': 'Proceso de control de calidad de productos/servicios',
                'category': 'quality',
                'difficulty_level': 'medium',
                'template_data': {
                    'mermaid_code': '''flowchart TD
    A[Recepción de Producto] --> B[Inspección Visual]
    B --> C[Pruebas de Calidad]
    C --> D{¿Cumple Especificaciones?}
    D -->|No| E[Registro de No Conformidad]
    E --> F[Análisis de Causa]
    F --> G[Acción Correctiva]
    G --> H[Re-inspección]
    H --> D
    D -->|Sí| I[Aprobación de Calidad]
    I --> J[Etiquetado/Certificación]
    J --> K[Liberación para Uso/Venta]
    K --> L[Registro de Calidad]
    L --> M[Fin del Proceso]''',
                    'elements': ['start', 'decision', 'process', 'end'],
                    'complexity': 'medium'
                }
            }
        ]

        # Crear plantillas
        for template_data in templates:
            template, created = FlowchartTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'category': template_data['category'],
                    'difficulty_level': template_data['difficulty_level'],
                    'template_data': template_data['template_data'],
                    'created_by': admin_user,
                    'is_active': True,
                    'usage_count': 0
                }
            )
            if created:
                self.stdout.write(f'Plantilla creada: {template_data["name"]}')
            else:
                self.stdout.write(f'Plantilla ya existe: {template_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS('Plantillas de flujogramas creadas exitosamente')
        )