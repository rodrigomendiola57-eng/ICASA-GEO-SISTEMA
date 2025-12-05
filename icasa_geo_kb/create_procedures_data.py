#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.procedures.models import ProcedureCategory, ProcedureTemplate
from django.contrib.auth.models import User

def create_procedure_categories():
    """Crear categorías de procedimientos"""
    categories = [
        {
            'name': 'Procedimientos Operativos',
            'category_type': 'operational',
            'description': 'Procedimientos relacionados con las operaciones diarias',
            'color': '#3498db',
            'icon': 'fas fa-cogs'
        },
        {
            'name': 'Procedimientos Administrativos',
            'category_type': 'administrative',
            'description': 'Procedimientos de gestión administrativa',
            'color': '#2ecc71',
            'icon': 'fas fa-file-alt'
        },
        {
            'name': 'Procedimientos de Calidad',
            'category_type': 'quality',
            'description': 'Procedimientos del sistema de gestión de calidad',
            'color': '#f39c12',
            'icon': 'fas fa-award'
        },
        {
            'name': 'Procedimientos de Seguridad',
            'category_type': 'safety',
            'description': 'Procedimientos de seguridad e higiene',
            'color': '#e74c3c',
            'icon': 'fas fa-shield-alt'
        },
        {
            'name': 'Procedimientos de Auditoría',
            'category_type': 'audit',
            'description': 'Procedimientos de auditoría interna',
            'color': '#9b59b6',
            'icon': 'fas fa-search'
        },
        {
            'name': 'Procedimientos de Transporte',
            'category_type': 'transport',
            'description': 'Procedimientos específicos de transporte y logística',
            'color': '#1abc9c',
            'icon': 'fas fa-truck'
        },
        {
            'name': 'Procedimientos de Mantenimiento',
            'category_type': 'maintenance',
            'description': 'Procedimientos de mantenimiento preventivo y correctivo',
            'color': '#34495e',
            'icon': 'fas fa-tools'
        },
        {
            'name': 'Procedimientos de RRHH',
            'category_type': 'hr',
            'description': 'Procedimientos de recursos humanos',
            'color': '#e67e22',
            'icon': 'fas fa-users'
        },
        {
            'name': 'Procedimientos Financieros',
            'category_type': 'finance',
            'description': 'Procedimientos financieros y contables',
            'color': '#27ae60',
            'icon': 'fas fa-dollar-sign'
        },
        {
            'name': 'Procedimientos Legales',
            'category_type': 'legal',
            'description': 'Procedimientos legales y normativos',
            'color': '#8e44ad',
            'icon': 'fas fa-gavel'
        }
    ]
    
    created_count = 0
    for cat_data in categories:
        category, created = ProcedureCategory.objects.get_or_create(
            category_type=cat_data['category_type'],
            defaults=cat_data
        )
        if created:
            created_count += 1
            print(f"Categoria creada: {category.name}")
        else:
            print(f"- Categoria existente: {category.name}")
    
    print(f"\n{created_count} categorias nuevas creadas de {len(categories)} totales")

def create_procedure_templates():
    """Crear plantillas de procedimientos"""
    
    # Obtener categorías
    operational = ProcedureCategory.objects.get(category_type='operational')
    administrative = ProcedureCategory.objects.get(category_type='administrative')
    quality = ProcedureCategory.objects.get(category_type='quality')
    safety = ProcedureCategory.objects.get(category_type='safety')
    audit = ProcedureCategory.objects.get(category_type='audit')
    transport = ProcedureCategory.objects.get(category_type='transport')
    hr = ProcedureCategory.objects.get(category_type='hr')
    
    templates = [
        {
            'name': 'Procedimiento de Facturación',
            'category': administrative,
            'description': 'Plantilla para procedimientos de facturación y cobranza',
            'template_content': {
                'objective': 'Establecer los pasos necesarios para la emisión y seguimiento de facturas de manera eficiente y precisa.',
                'scope': 'Aplica a todas las facturas emitidas por la empresa a clientes nacionales e internacionales.',
                'content': '''1. RECEPCIÓN DE SOLICITUD DE FACTURACIÓN
   - Verificar orden de compra o contrato
   - Validar datos del cliente
   - Confirmar productos/servicios entregados

2. PREPARACIÓN DE DOCUMENTOS
   - Recopilar documentación soporte
   - Verificar precios y condiciones
   - Calcular impuestos aplicables

3. EMISIÓN DE FACTURA
   - Generar factura en sistema
   - Revisar datos antes de envío
   - Obtener autorización si es necesario

4. ENVÍO Y SEGUIMIENTO
   - Enviar factura al cliente
   - Registrar en sistema de seguimiento
   - Programar recordatorios de pago

5. CONTROL DE COBRANZA
   - Monitorear fechas de vencimiento
   - Gestionar cobranza preventiva
   - Escalar casos de morosidad''',
                'criticality': 'high',
                'frequency': 'daily'
            }
        },
        {
            'name': 'Procedimiento de Reclutamiento',
            'category': hr,
            'description': 'Plantilla para procesos de selección de personal',
            'template_content': {
                'objective': 'Definir el proceso estándar para la selección y contratación de personal calificado.',
                'scope': 'Aplica a todas las posiciones de la empresa, desde operativas hasta ejecutivas.',
                'content': '''1. IDENTIFICACIÓN DE NECESIDAD
   - Solicitud de requisición de personal
   - Análisis del perfil del puesto
   - Aprobación presupuestal

2. BÚSQUEDA Y CONVOCATORIA
   - Publicación de vacante
   - Búsqueda en base de datos
   - Recepción de candidaturas

3. PRESELECCIÓN
   - Revisión de CVs
   - Filtro por requisitos mínimos
   - Contacto inicial con candidatos

4. PROCESO DE SELECCIÓN
   - Entrevista inicial de RRHH
   - Evaluaciones técnicas
   - Entrevista con jefe directo

5. CONTRATACIÓN
   - Verificación de referencias
   - Exámenes médicos
   - Elaboración de contrato
   - Proceso de inducción''',
                'criticality': 'medium',
                'frequency': 'on_demand'
            }
        },
        {
            'name': 'Procedimiento de Auditoría Interna',
            'category': audit,
            'description': 'Plantilla para auditorías internas de procesos',
            'template_content': {
                'objective': 'Establecer la metodología para realizar auditorías internas efectivas que aseguren el cumplimiento de estándares.',
                'scope': 'Aplica a todas las áreas y procesos sujetos a auditoría interna.',
                'content': '''1. PLANIFICACIÓN DE AUDITORÍA
   - Definir alcance y objetivos
   - Seleccionar equipo auditor
   - Programar fechas y recursos

2. PREPARACIÓN
   - Revisar documentación previa
   - Preparar listas de verificación
   - Comunicar a áreas involucradas

3. EJECUCIÓN DE AUDITORÍA
   - Reunión de apertura
   - Recopilación de evidencias
   - Entrevistas con personal
   - Observación de procesos

4. ANÁLISIS Y EVALUACIÓN
   - Análisis de hallazgos
   - Clasificación de no conformidades
   - Identificación de oportunidades

5. REPORTE Y SEGUIMIENTO
   - Elaboración de informe
   - Reunión de cierre
   - Plan de acciones correctivas
   - Seguimiento de implementación''',
                'criticality': 'high',
                'frequency': 'quarterly'
            }
        },
        {
            'name': 'Procedimiento de Mantenimiento Preventivo',
            'category': operational,
            'description': 'Plantilla para mantenimiento preventivo de equipos',
            'template_content': {
                'objective': 'Asegurar el funcionamiento óptimo de equipos mediante mantenimiento preventivo programado.',
                'scope': 'Aplica a todos los equipos críticos y de producción de la empresa.',
                'content': '''1. PROGRAMACIÓN DE MANTENIMIENTO
   - Consultar plan anual de mantenimiento
   - Verificar disponibilidad de recursos
   - Coordinar con operaciones

2. PREPARACIÓN
   - Revisar historial del equipo
   - Preparar herramientas y repuestos
   - Aplicar medidas de seguridad

3. EJECUCIÓN DEL MANTENIMIENTO
   - Inspección visual general
   - Limpieza y lubricación
   - Ajustes y calibraciones
   - Pruebas de funcionamiento

4. REGISTRO Y DOCUMENTACIÓN
   - Completar orden de trabajo
   - Registrar observaciones
   - Actualizar historial del equipo
   - Reportar anomalías

5. SEGUIMIENTO
   - Programar próximo mantenimiento
   - Actualizar inventario de repuestos
   - Evaluar efectividad del mantenimiento''',
                'criticality': 'high',
                'frequency': 'monthly'
            }
        },
        {
            'name': 'Procedimiento de Control de Calidad',
            'category': quality,
            'description': 'Plantilla para control de calidad de productos/servicios',
            'template_content': {
                'objective': 'Garantizar que todos los productos/servicios cumplan con los estándares de calidad establecidos.',
                'scope': 'Aplica a todos los productos y servicios entregados a clientes.',
                'content': '''1. RECEPCIÓN PARA INSPECCIÓN
   - Identificar lote o servicio a inspeccionar
   - Verificar documentación asociada
   - Preparar equipos de medición

2. INSPECCIÓN Y PRUEBAS
   - Aplicar plan de inspección
   - Realizar mediciones y pruebas
   - Documentar resultados
   - Comparar con especificaciones

3. EVALUACIÓN DE RESULTADOS
   - Analizar conformidad
   - Identificar no conformidades
   - Determinar acciones necesarias

4. DISPOSICIÓN
   - Aprobar productos conformes
   - Rechazar o reprocesar no conformes
   - Notificar a áreas involucradas
   - Actualizar registros

5. MEJORA CONTINUA
   - Analizar tendencias de calidad
   - Identificar oportunidades de mejora
   - Proponer acciones preventivas''',
                'criticality': 'critical',
                'frequency': 'daily'
            }
        },
        {
            'name': 'Procedimiento de Seguridad Industrial',
            'category': safety,
            'description': 'Plantilla para procedimientos de seguridad en el trabajo',
            'template_content': {
                'objective': 'Establecer medidas de seguridad para prevenir accidentes y proteger la integridad del personal.',
                'scope': 'Aplica a todas las actividades laborales que impliquen riesgos de seguridad.',
                'content': '''1. IDENTIFICACIÓN DE RIESGOS
   - Evaluar área de trabajo
   - Identificar peligros potenciales
   - Clasificar nivel de riesgo

2. MEDIDAS PREVENTIVAS
   - Implementar controles de ingeniería
   - Establecer procedimientos seguros
   - Proporcionar EPP adecuado
   - Capacitar al personal

3. EJECUCIÓN SEGURA
   - Verificar condiciones antes de iniciar
   - Seguir procedimientos establecidos
   - Usar EPP obligatorio
   - Mantener comunicación constante

4. MONITOREO Y CONTROL
   - Supervisar cumplimiento
   - Realizar inspecciones periódicas
   - Corregir desviaciones inmediatamente
   - Documentar observaciones

5. RESPUESTA A EMERGENCIAS
   - Activar plan de emergencia si es necesario
   - Reportar incidentes o accidentes
   - Investigar causas
   - Implementar acciones correctivas''',
                'criticality': 'critical',
                'frequency': 'daily'
            }
        },
        {
            'name': 'Procedimiento de Transporte de Carga',
            'category': transport,
            'description': 'Plantilla específica para operaciones de transporte',
            'template_content': {
                'objective': 'Asegurar el transporte seguro y eficiente de mercancías cumpliendo con todas las regulaciones.',
                'scope': 'Aplica a todas las operaciones de transporte terrestre de carga.',
                'content': '''1. PREPARACIÓN DEL VIAJE
   - Verificar documentación del vehículo
   - Inspeccionar condiciones mecánicas
   - Validar licencias y permisos del conductor
   - Revisar ruta y condiciones climáticas

2. CARGA DE MERCANCÍA
   - Verificar documentos de carga
   - Inspeccionar mercancía antes de cargar
   - Aplicar técnicas de estiba segura
   - Completar carta porte y documentos

3. DURANTE EL TRANSPORTE
   - Cumplir límites de velocidad
   - Realizar paradas de descanso programadas
   - Mantener comunicación con base
   - Reportar cualquier novedad

4. ENTREGA EN DESTINO
   - Verificar identidad del receptor
   - Inspeccionar mercancía antes de entregar
   - Obtener firma de recibido conforme
   - Documentar cualquier daño o faltante

5. RETORNO Y CIERRE
   - Entregar documentos en oficina
   - Reportar novedades del viaje
   - Programar mantenimiento si es necesario
   - Actualizar registros de operación''',
                'criticality': 'high',
                'frequency': 'daily'
            }
        }
    ]
    
    created_count = 0
    for template_data in templates:
        template, created = ProcedureTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            created_count += 1
            print(f"Plantilla creada: {template.name}")
        else:
            print(f"- Plantilla existente: {template.name}")
    
    print(f"\n{created_count} plantillas nuevas creadas de {len(templates)} totales")

def main():
    print("Creando datos iniciales para el modulo de Procedimientos...")
    print("=" * 60)
    
    print("\nCreando categorias de procedimientos...")
    create_procedure_categories()
    
    print("\nCreando plantillas de procedimientos...")
    create_procedure_templates()
    
    print("\n" + "=" * 60)
    print("Datos iniciales creados exitosamente!")
    print("\nPuedes acceder al modulo en: /procedimientos/")

if __name__ == '__main__':
    main()