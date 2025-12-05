"""
Sistema de Plantillas por Categoría para Knowledge Base
Plantillas específicas para cada tipo de documento de ICASA
"""

class DocumentTemplates:
    """Plantillas de documentos por categoría"""
    
    TEMPLATES = {
        'informacion-corporativa': {
            'mision-vision': {
                'name': 'Misión y Visión',
                'description': 'Plantilla para documentar la misión, visión y valores corporativos',
                'icon': 'fas fa-bullseye',
                'content': '''
                    <h1>MISIÓN, VISIÓN Y VALORES - ICASA</h1>
                    
                    <h2>MISIÓN</h2>
                    <p><strong>¿Cuál es nuestro propósito fundamental?</strong></p>
                    <p>[Describir la razón de ser de ICASA, qué hacemos y para quién]</p>
                    
                    <h2>VISIÓN</h2>
                    <p><strong>¿Hacia dónde nos dirigimos?</strong></p>
                    <p>[Describir el futuro deseado de ICASA, dónde queremos estar]</p>
                    
                    <h2>VALORES CORPORATIVOS</h2>
                    <ul>
                        <li><strong>Integridad:</strong> [Descripción del valor]</li>
                        <li><strong>Excelencia:</strong> [Descripción del valor]</li>
                        <li><strong>Compromiso:</strong> [Descripción del valor]</li>
                        <li><strong>Innovación:</strong> [Descripción del valor]</li>
                        <li><strong>Responsabilidad Social:</strong> [Descripción del valor]</li>
                    </ul>
                    
                    <h2>PRINCIPIOS ORGANIZACIONALES</h2>
                    <p>[Principios que guían nuestras decisiones y acciones]</p>
                '''
            },
            'estructura-organizacional': {
                'name': 'Estructura Organizacional',
                'description': 'Plantilla para documentar la estructura y jerarquía organizacional',
                'icon': 'fas fa-sitemap',
                'content': '''
                    <h1>ESTRUCTURA ORGANIZACIONAL - ICASA</h1>
                    
                    <h2>ORGANIGRAMA GENERAL</h2>
                    <p>[Insertar organigrama principal de ICASA]</p>
                    
                    <h2>NIVELES JERÁRQUICOS</h2>
                    <h3>Nivel Ejecutivo</h3>
                    <ul>
                        <li><strong>Junta Directiva:</strong> [Descripción y responsabilidades]</li>
                        <li><strong>Gerencia General:</strong> [Descripción y responsabilidades]</li>
                    </ul>
                    
                    <h3>Nivel Gerencial</h3>
                    <ul>
                        <li><strong>Gerencia de [Área]:</strong> [Descripción]</li>
                        <li><strong>Gerencia de [Área]:</strong> [Descripción]</li>
                    </ul>
                    
                    <h3>Nivel Operativo</h3>
                    <ul>
                        <li><strong>Jefaturas:</strong> [Descripción]</li>
                        <li><strong>Coordinaciones:</strong> [Descripción]</li>
                        <li><strong>Personal Operativo:</strong> [Descripción]</li>
                    </ul>
                    
                    <h2>LÍNEAS DE REPORTE</h2>
                    <p>[Describir las líneas de reporte y comunicación]</p>
                '''
            }
        },
        
        'marco-legal': {
            'normativa-sugese': {
                'name': 'Normativa SUGESE',
                'description': 'Plantilla para documentar normativas de la Superintendencia',
                'icon': 'fas fa-gavel',
                'content': '''
                    <h1>NORMATIVA SUGESE - [NÚMERO Y TÍTULO]</h1>
                    
                    <h2>INFORMACIÓN GENERAL</h2>
                    <table border="1" style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td><strong>Normativa:</strong></td>
                            <td>[Número de normativa]</td>
                        </tr>
                        <tr>
                            <td><strong>Fecha de Emisión:</strong></td>
                            <td>[Fecha]</td>
                        </tr>
                        <tr>
                            <td><strong>Fecha de Vigencia:</strong></td>
                            <td>[Fecha]</td>
                        </tr>
                        <tr>
                            <td><strong>Aplica a:</strong></td>
                            <td>[Áreas/Procesos afectados]</td>
                        </tr>
                    </table>
                    
                    <h2>RESUMEN EJECUTIVO</h2>
                    <p>[Resumen de los puntos principales de la normativa]</p>
                    
                    <h2>IMPACTO EN ICASA</h2>
                    <h3>Cambios Requeridos</h3>
                    <ul>
                        <li>[Cambio 1]</li>
                        <li>[Cambio 2]</li>
                    </ul>
                    
                    <h3>Áreas Afectadas</h3>
                    <ul>
                        <li>[Área 1]: [Descripción del impacto]</li>
                        <li>[Área 2]: [Descripción del impacto]</li>
                    </ul>
                    
                    <h2>PLAN DE IMPLEMENTACIÓN</h2>
                    <p>[Pasos para implementar los cambios requeridos]</p>
                    
                    <h2>RESPONSABLES</h2>
                    <ul>
                        <li><strong>Responsable Principal:</strong> [Nombre y cargo]</li>
                        <li><strong>Equipo de Implementación:</strong> [Nombres]</li>
                    </ul>
                '''
            },
            'codigo-etica': {
                'name': 'Código de Ética',
                'description': 'Plantilla para políticas éticas y de conducta',
                'icon': 'fas fa-handshake',
                'content': '''
                    <h1>CÓDIGO DE ÉTICA - ICASA</h1>
                    
                    <h2>INTRODUCCIÓN</h2>
                    <p>Este código establece los principios éticos que rigen el comportamiento de todos los colaboradores de ICASA.</p>
                    
                    <h2>PRINCIPIOS FUNDAMENTALES</h2>
                    <h3>1. Integridad</h3>
                    <p>[Descripción del principio y ejemplos de aplicación]</p>
                    
                    <h3>2. Honestidad</h3>
                    <p>[Descripción del principio y ejemplos de aplicación]</p>
                    
                    <h3>3. Transparencia</h3>
                    <p>[Descripción del principio y ejemplos de aplicación]</p>
                    
                    <h2>NORMAS DE CONDUCTA</h2>
                    <h3>Relaciones con Clientes</h3>
                    <ul>
                        <li>[Norma 1]</li>
                        <li>[Norma 2]</li>
                    </ul>
                    
                    <h3>Relaciones entre Colaboradores</h3>
                    <ul>
                        <li>[Norma 1]</li>
                        <li>[Norma 2]</li>
                    </ul>
                    
                    <h2>CONFLICTOS DE INTERÉS</h2>
                    <p>[Definición y procedimientos para manejar conflictos]</p>
                    
                    <h2>PROCEDIMIENTO DE DENUNCIA</h2>
                    <p>[Pasos para reportar violaciones al código]</p>
                '''
            }
        },
        
        'politicas-organizacionales': {
            'politica-rrhh': {
                'name': 'Política de Recursos Humanos',
                'description': 'Plantilla para políticas de gestión del talento humano',
                'icon': 'fas fa-users',
                'content': '''
                    <h1>POLÍTICA DE RECURSOS HUMANOS</h1>
                    
                    <h2>1. OBJETIVO</h2>
                    <p>Establecer las directrices para la gestión integral del talento humano en ICASA.</p>
                    
                    <h2>2. ALCANCE</h2>
                    <p>Esta política aplica a todos los colaboradores de ICASA, sin excepción.</p>
                    
                    <h2>3. PRINCIPIOS</h2>
                    <ul>
                        <li><strong>Equidad:</strong> [Descripción]</li>
                        <li><strong>Mérito:</strong> [Descripción]</li>
                        <li><strong>Desarrollo:</strong> [Descripción]</li>
                    </ul>
                    
                    <h2>4. POLÍTICAS ESPECÍFICAS</h2>
                    <h3>4.1 Reclutamiento y Selección</h3>
                    <p>[Directrices para contratación]</p>
                    
                    <h3>4.2 Evaluación del Desempeño</h3>
                    <p>[Proceso de evaluación]</p>
                    
                    <h3>4.3 Capacitación y Desarrollo</h3>
                    <p>[Programas de formación]</p>
                    
                    <h3>4.4 Compensación y Beneficios</h3>
                    <p>[Estructura salarial y beneficios]</p>
                    
                    <h2>5. RESPONSABILIDADES</h2>
                    <ul>
                        <li><strong>Gerencia de RRHH:</strong> [Responsabilidades]</li>
                        <li><strong>Jefaturas:</strong> [Responsabilidades]</li>
                        <li><strong>Colaboradores:</strong> [Responsabilidades]</li>
                    </ul>
                '''
            }
        },
        
        'manuales-operativos': {
            'manual-suscripcion': {
                'name': 'Manual de Suscripción',
                'description': 'Plantilla para procesos de evaluación y suscripción de riesgos',
                'icon': 'fas fa-clipboard-check',
                'content': '''
                    <h1>MANUAL DE SUSCRIPCIÓN DE SEGUROS</h1>
                    
                    <h2>1. INTRODUCCIÓN</h2>
                    <p>Este manual establece los procedimientos para la evaluación y suscripción de riesgos en ICASA.</p>
                    
                    <h2>2. PROCESO DE SUSCRIPCIÓN</h2>
                    <h3>2.1 Recepción de Solicitud</h3>
                    <ol>
                        <li>[Paso 1]</li>
                        <li>[Paso 2]</li>
                        <li>[Paso 3]</li>
                    </ol>
                    
                    <h3>2.2 Evaluación de Riesgo</h3>
                    <p><strong>Criterios de Evaluación:</strong></p>
                    <ul>
                        <li>[Criterio 1]</li>
                        <li>[Criterio 2]</li>
                    </ul>
                    
                    <h3>2.3 Decisión de Suscripción</h3>
                    <table border="1" style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <th>Nivel de Riesgo</th>
                            <th>Autoridad</th>
                            <th>Límites</th>
                        </tr>
                        <tr>
                            <td>Bajo</td>
                            <td>[Cargo]</td>
                            <td>[Monto]</td>
                        </tr>
                        <tr>
                            <td>Medio</td>
                            <td>[Cargo]</td>
                            <td>[Monto]</td>
                        </tr>
                        <tr>
                            <td>Alto</td>
                            <td>[Cargo]</td>
                            <td>[Monto]</td>
                        </tr>
                    </table>
                    
                    <h2>3. DOCUMENTACIÓN REQUERIDA</h2>
                    <ul>
                        <li>[Documento 1]</li>
                        <li>[Documento 2]</li>
                    </ul>
                    
                    <h2>4. CONTROLES Y SEGUIMIENTO</h2>
                    <p>[Procedimientos de control y monitoreo]</p>
                '''
            }
        },
        
        'objetivos-estrategicos': {
            'plan-estrategico': {
                'name': 'Plan Estratégico',
                'description': 'Plantilla para documentar objetivos y estrategias corporativas',
                'icon': 'fas fa-bullseye',
                'content': '''
                    <h1>PLAN ESTRATÉGICO ICASA 2024-2026</h1>
                    
                    <h2>1. ANÁLISIS SITUACIONAL</h2>
                    <h3>1.1 Análisis Interno</h3>
                    <p><strong>Fortalezas:</strong></p>
                    <ul>
                        <li>[Fortaleza 1]</li>
                        <li>[Fortaleza 2]</li>
                    </ul>
                    
                    <p><strong>Debilidades:</strong></p>
                    <ul>
                        <li>[Debilidad 1]</li>
                        <li>[Debilidad 2]</li>
                    </ul>
                    
                    <h3>1.2 Análisis Externo</h3>
                    <p><strong>Oportunidades:</strong></p>
                    <ul>
                        <li>[Oportunidad 1]</li>
                        <li>[Oportunidad 2]</li>
                    </ul>
                    
                    <p><strong>Amenazas:</strong></p>
                    <ul>
                        <li>[Amenaza 1]</li>
                        <li>[Amenaza 2]</li>
                    </ul>
                    
                    <h2>2. OBJETIVOS ESTRATÉGICOS</h2>
                    <h3>Objetivo 1: [Título]</h3>
                    <ul>
                        <li><strong>Descripción:</strong> [Detalle del objetivo]</li>
                        <li><strong>Indicador:</strong> [KPI]</li>
                        <li><strong>Meta:</strong> [Valor objetivo]</li>
                        <li><strong>Responsable:</strong> [Cargo]</li>
                    </ul>
                    
                    <h2>3. ESTRATEGIAS</h2>
                    <p>[Estrategias para alcanzar los objetivos]</p>
                    
                    <h2>4. PLAN DE ACCIÓN</h2>
                    <table border="1" style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <th>Acción</th>
                            <th>Responsable</th>
                            <th>Fecha</th>
                            <th>Recursos</th>
                        </tr>
                        <tr>
                            <td>[Acción 1]</td>
                            <td>[Responsable]</td>
                            <td>[Fecha]</td>
                            <td>[Recursos]</td>
                        </tr>
                    </table>
                '''
            }
        }
    }
    
    @classmethod
    def get_templates_by_category(cls, category_slug):
        """Obtener plantillas disponibles para una categoría"""
        return cls.TEMPLATES.get(category_slug, {})
    
    @classmethod
    def get_template(cls, category_slug, template_key):
        """Obtener una plantilla específica"""
        category_templates = cls.get_templates_by_category(category_slug)
        return category_templates.get(template_key)
    
    @classmethod
    def get_all_templates(cls):
        """Obtener todas las plantillas disponibles"""
        all_templates = {}
        for category, templates in cls.TEMPLATES.items():
            all_templates[category] = templates
        return all_templates

def get_template_choices():
    """Obtener opciones de plantillas para formularios"""
    choices = [('', 'Sin plantilla')]
    for category_slug, templates in DocumentTemplates.TEMPLATES.items():
        for template_key, template in templates.items():
            choices.append((f"{category_slug}:{template_key}", template['name']))
    return choices

def get_template_content(template_id):
    """Obtener contenido de una plantilla específica"""
    if ':' not in template_id:
        return ''
    
    category_slug, template_key = template_id.split(':', 1)
    template = DocumentTemplates.get_template(category_slug, template_key)
    return template['content'] if template else ''