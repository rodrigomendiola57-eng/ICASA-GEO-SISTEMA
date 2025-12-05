#!/usr/bin/env python
"""
Script para inicializar datos básicos del sistema de fluogramas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import ProcessCategory, FlowchartTemplate
from django.contrib.auth.models import User

def create_process_categories():
    """Crear categorías de procesos"""
    categories = [
        {
            'name': 'Procesos Operativos',
            'description': 'Procesos principales del negocio',
            'category_type': 'operational',
            'color': '#059669',
            'icon': 'fas fa-cogs'
        },
        {
            'name': 'Procesos Estratégicos',
            'description': 'Procesos de dirección y planificación',
            'category_type': 'strategic',
            'color': '#3B82F6',
            'icon': 'fas fa-chess-king'
        },
        {
            'name': 'Procesos de Soporte',
            'description': 'Procesos de apoyo y recursos',
            'category_type': 'support',
            'color': '#8B5CF6',
            'icon': 'fas fa-hands-helping'
        },
        {
            'name': 'Procesos de Auditoría',
            'description': 'Procesos de control y verificación',
            'category_type': 'audit',
            'color': '#EF4444',
            'icon': 'fas fa-search'
        }
    ]
    
    created_count = 0
    for cat_data in categories:
        category, created = ProcessCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            created_count += 1
            print(f"+ Categoria creada: {category.name}")
        else:
            print(f"- Categoria ya existe: {category.name}")
    
    print(f"\nCategorias creadas: {created_count}/{len(categories)}")
    return ProcessCategory.objects.all()

def create_flowchart_templates():
    """Crear plantillas de fluogramas"""
    
    # Obtener usuario admin o crear uno temporal
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin_temp',
                email='admin@icasa.com',
                is_staff=True,
                is_superuser=True
            )
    except:
        admin_user = None
    
    templates = [
        {
            'name': 'Proceso de Compras',
            'description': 'Flujo estándar para adquisiciones y compras',
            'category': 'operational',
            'difficulty_level': 'medium',
            'template_data': {
                'mermaid_code': '''flowchart TD
    A[Solicitud de Compra] --> B{Presupuesto Aprobado?}
    B -->|Si| C[Cotización Proveedores]
    B -->|No| D[Solicitar Aprobación Presupuestal]
    D --> E{Aprobado?}
    E -->|Si| C
    E -->|No| F[Rechazado]
    C --> G[Evaluación de Propuestas]
    G --> H[Selección de Proveedor]
    H --> I[Orden de Compra]
    I --> J[Recepción de Mercancía]
    J --> K[Verificación de Calidad]
    K --> L{Conforme?}
    L -->|Si| M[Autorización de Pago]
    L -->|No| N[Devolución/Reclamo]
    M --> O[Fin del Proceso]
    N --> O'''
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
    E --> F{Candidatos Aptos?}
    F -->|No| G[Ampliar Búsqueda]
    G --> C
    F -->|Si| H[Entrevista Inicial RRHH]
    H --> I{Pasa Filtro?}
    I -->|No| J[Descartado]
    I -->|Si| K[Entrevista Técnica]
    K --> L{Aprobado?}
    L -->|No| J
    L -->|Si| M[Verificación de Referencias]
    M --> N[Oferta Laboral]
    N --> O{Acepta?}
    O -->|No| P[Fin - No Contratado]
    O -->|Si| Q[Contratación]
    Q --> R[Inducción]
    R --> S[Fin del Proceso]'''
            }
        },
        {
            'name': 'Auditoría Interna',
            'description': 'Proceso de auditoría y control interno',
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
    I --> J{Hay No Conformidades?}
    J -->|Si| K[Documentar No Conformidades]
    J -->|No| L[Documentar Observaciones]
    K --> M[Reunión de Cierre]
    L --> M
    M --> N[Elaboración de Informe]
    N --> O[Entrega de Informe]
    O --> P[Plan de Acciones Correctivas]
    P --> Q[Seguimiento]
    Q --> R[Cierre de Auditoría]'''
            }
        },
        {
            'name': 'Flujo de Aprobación',
            'description': 'Proceso genérico de aprobaciones',
            'category': 'operations',
            'difficulty_level': 'simple',
            'template_data': {
                'mermaid_code': '''flowchart TD
    A[Solicitud] --> B[Revisión Inicial]
    B --> C{Cumple Requisitos?}
    C -->|No| D[Solicitar Correcciones]
    D --> A
    C -->|Si| E[Evaluación Técnica]
    E --> F{Aprobado?}
    F -->|No| G[Rechazado]
    F -->|Si| H[Aprobación Final]
    H --> I[Notificación]
    I --> J[Implementación]
    J --> K[Fin del Proceso]
    G --> K'''
            }
        }
    ]
    
    created_count = 0
    for template_data in templates:
        template, created = FlowchartTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults={
                **template_data,
                'created_by': admin_user
            }
        )
        if created:
            created_count += 1
            print(f"+ Plantilla creada: {template.name}")
        else:
            print(f"- Plantilla ya existe: {template.name}")
    
    print(f"\nPlantillas creadas: {created_count}/{len(templates)}")
    return FlowchartTemplate.objects.all()

def main():
    print("Inicializando sistema de fluogramas ICASA-GEO...")
    print("=" * 50)
    
    print("\nCreando categorias de procesos...")
    categories = create_process_categories()
    
    print("\nCreando plantillas de fluogramas...")
    templates = create_flowchart_templates()
    
    print("\n" + "=" * 50)
    print("Inicializacion completada!")
    print(f"Resumen:")
    print(f"   - Categorias disponibles: {categories.count()}")
    print(f"   - Plantillas disponibles: {templates.count()}")
    print("\nEl sistema de fluogramas esta listo para usar!")

if __name__ == '__main__':
    main()