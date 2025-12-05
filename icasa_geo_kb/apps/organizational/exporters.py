"""
Exportadores corporativos para organigramas
Soporta PDF, Excel, PowerPoint, Visio y formatos corporativos
"""
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4, A3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .models import DepartmentalChart

class BaseExporter:
    """Clase base para exportadores"""
    
    def __init__(self, chart: DepartmentalChart):
        self.chart = chart
        self.export_date = datetime.now()
    
    def get_chart_metadata(self) -> Dict:
        """Obtener metadatos del organigrama"""
        return {
            'name': self.chart.name,
            'department': self.chart.department,
            'version': self.chart.version,
            'created_by': self.chart.created_by.get_full_name() if self.chart.created_by else 'Sistema',
            'created_at': self.chart.created_at,
            'updated_at': self.chart.updated_at,
            'status': self.chart.get_status_display(),
            'export_date': self.export_date,
            'is_sandbox': self.chart.is_sandbox
        }

class PDFExporter(BaseExporter):
    """Exportador a PDF corporativo con branding ICASA"""
    
    def export_organizational_book(self) -> HttpResponse:
        """Exportar 'Libro de Organización' completo en PDF"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#4CAF50'),  # Verde ICASA
            alignment=1  # Centrado
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#388E3C')
        )
        
        # Contenido del documento
        story = []
        
        # Portada
        story.extend(self._create_cover_page(title_style, styles))
        story.append(PageBreak())
        
        # Índice
        story.extend(self._create_index(heading_style, styles))
        story.append(PageBreak())
        
        # Información general
        story.extend(self._create_general_info(heading_style, styles))
        story.append(PageBreak())
        
        # Organigrama visual
        story.extend(self._create_visual_chart(heading_style, styles))
        story.append(PageBreak())
        
        # Descripciones de puestos
        story.extend(self._create_position_descriptions(heading_style, styles))
        story.append(PageBreak())
        
        # Matriz de responsabilidades
        story.extend(self._create_responsibility_matrix(heading_style, styles))
        story.append(PageBreak())
        
        # Anexos
        story.extend(self._create_appendices(heading_style, styles))
        
        # Generar PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"Libro_Organizacion_{self.chart.department}_{self.export_date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _create_cover_page(self, title_style, styles) -> List:
        """Crear portada del documento"""
        
        metadata = self.get_chart_metadata()
        
        cover = [
            Spacer(1, 2*inch),
            Paragraph("ICASA", title_style),
            Paragraph("Instituto de Capacitación y Servicios Administrativos", styles['Normal']),
            Spacer(1, 1*inch),
            Paragraph(f"LIBRO DE ORGANIZACIÓN", title_style),
            Paragraph(f"Departamento: {metadata['department']}", styles['Heading2']),
            Spacer(1, 1*inch),
            Paragraph(f"Versión: {metadata['version']}", styles['Normal']),
            Paragraph(f"Fecha de generación: {metadata['export_date'].strftime('%d de %B de %Y')}", styles['Normal']),
            Paragraph(f"Generado por: {metadata['created_by']}", styles['Normal']),
            Spacer(1, 2*inch),
            Paragraph("Documento confidencial - Uso interno", styles['Normal'])
        ]
        
        return cover
    
    def _create_index(self, heading_style, styles) -> List:
        """Crear índice del documento"""
        
        index_content = [
            Paragraph("ÍNDICE", heading_style),
            Spacer(1, 0.2*inch),
            Paragraph("1. Información General ........................... 3", styles['Normal']),
            Paragraph("2. Organigrama Visual ........................... 4", styles['Normal']),
            Paragraph("3. Descripciones de Puestos ..................... 5", styles['Normal']),
            Paragraph("4. Matriz de Responsabilidades .................. 8", styles['Normal']),
            Paragraph("5. Anexos ....................................... 10", styles['Normal']),
            Spacer(1, 0.3*inch),
            Paragraph("CONTROL DE VERSIONES", heading_style),
            Spacer(1, 0.1*inch)
        ]
        
        # Tabla de control de versiones
        version_data = [
            ['Versión', 'Fecha', 'Autor', 'Descripción'],
            [self.chart.version, self.chart.updated_at.strftime('%d/%m/%Y'), 
             self.chart.created_by.get_full_name() if self.chart.created_by else 'Sistema',
             self.chart.change_justification or 'Versión inicial']
        ]
        
        version_table = Table(version_data, colWidths=[1*inch, 1.5*inch, 2*inch, 2.5*inch])
        version_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        index_content.append(version_table)
        
        return index_content
    
    def _create_general_info(self, heading_style, styles) -> List:
        """Crear sección de información general"""
        
        metadata = self.get_chart_metadata()
        
        general_info = [
            Paragraph("1. INFORMACIÓN GENERAL", heading_style),
            Spacer(1, 0.2*inch),
            Paragraph(f"<b>Nombre del Organigrama:</b> {metadata['name']}", styles['Normal']),
            Paragraph(f"<b>Departamento:</b> {metadata['department']}", styles['Normal']),
            Paragraph(f"<b>Versión:</b> {metadata['version']}", styles['Normal']),
            Paragraph(f"<b>Estado:</b> {metadata['status']}", styles['Normal']),
            Paragraph(f"<b>Fecha de creación:</b> {metadata['created_at'].strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"<b>Última actualización:</b> {metadata['updated_at'].strftime('%d/%m/%Y')}", styles['Normal']),
            Spacer(1, 0.3*inch),
            
            Paragraph("OBJETIVO", ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#388E3C'))),
            Paragraph(self.chart.description or "Definir la estructura organizacional y las relaciones jerárquicas del departamento.", styles['Normal']),
            Spacer(1, 0.2*inch),
            
            Paragraph("ALCANCE", ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#388E3C'))),
            Paragraph(f"Este documento aplica a todo el personal del departamento de {metadata['department']} de ICASA.", styles['Normal']),
        ]
        
        return general_info
    
    def _create_visual_chart(self, heading_style, styles) -> List:
        """Crear representación visual del organigrama"""
        
        visual_content = [
            Paragraph("2. ORGANIGRAMA VISUAL", heading_style),
            Spacer(1, 0.2*inch),
            Paragraph("A continuación se presenta la estructura organizacional del departamento:", styles['Normal']),
            Spacer(1, 0.3*inch)
        ]
        
        # Aquí iría la lógica para generar el diagrama visual
        # Por simplicidad, creamos una tabla jerárquica
        if self.chart.chart_data and 'positions' in self.chart.chart_data:
            positions = self.chart.chart_data['positions']
            
            # Agrupar por nivel
            levels = {}
            for pos in positions:
                level = pos.get('level', 1)
                if level not in levels:
                    levels[level] = []
                levels[level].append(pos)
            
            # Crear tabla por niveles
            for level in sorted(levels.keys()):
                level_positions = levels[level]
                
                visual_content.append(Paragraph(f"Nivel {level}:", styles['Heading4']))
                
                # Crear tabla para este nivel
                pos_data = [['Puesto', 'Empleado Actual', 'Reporta a']]
                
                for pos in level_positions:
                    reports_to = ""
                    if pos.get('reports_to'):
                        # Buscar el nombre del jefe
                        for p in positions:
                            if p['id'] == pos['reports_to']:
                                reports_to = p['title']
                                break
                    
                    pos_data.append([
                        pos['title'],
                        pos.get('current_employee', 'VACANTE'),
                        reports_to
                    ])
                
                pos_table = Table(pos_data, colWidths=[2.5*inch, 2*inch, 2*inch])
                pos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8BC34A')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                
                visual_content.extend([pos_table, Spacer(1, 0.2*inch)])
        
        return visual_content
    
    def _create_position_descriptions(self, heading_style, styles) -> List:
        """Crear descripciones detalladas de puestos"""
        
        descriptions = [
            Paragraph("3. DESCRIPCIONES DE PUESTOS", heading_style),
            Spacer(1, 0.2*inch)
        ]
        
        if self.chart.chart_data and 'positions' in self.chart.chart_data:
            positions = self.chart.chart_data['positions']
            
            for i, pos in enumerate(positions):
                descriptions.extend([
                    Paragraph(f"3.{i+1} {pos['title']}", styles['Heading3']),
                    Spacer(1, 0.1*inch),
                    Paragraph(f"<b>Departamento:</b> {pos['department']}", styles['Normal']),
                    Paragraph(f"<b>Nivel jerárquico:</b> {pos.get('level', 1)}", styles['Normal']),
                    Paragraph(f"<b>Empleado actual:</b> {pos.get('current_employee', 'VACANTE')}", styles['Normal']),
                    Spacer(1, 0.1*inch),
                    Paragraph("<b>Responsabilidades:</b>", styles['Normal']),
                    Paragraph(pos.get('responsibilities', 'No definidas'), styles['Normal']),
                    Spacer(1, 0.2*inch)
                ])
        
        return descriptions
    
    def _create_responsibility_matrix(self, heading_style, styles) -> List:
        """Crear matriz de responsabilidades"""
        
        matrix_content = [
            Paragraph("4. MATRIZ DE RESPONSABILIDADES", heading_style),
            Spacer(1, 0.2*inch),
            Paragraph("La siguiente matriz muestra la distribución de responsabilidades por puesto:", styles['Normal']),
            Spacer(1, 0.3*inch)
        ]
        
        # Crear matriz RACI (Responsible, Accountable, Consulted, Informed)
        if self.chart.chart_data and 'positions' in self.chart.chart_data:
            positions = self.chart.chart_data['positions']
            
            # Procesos típicos (esto podría venir de la base de datos)
            processes = [
                'Planificación Estratégica',
                'Gestión de Personal',
                'Control de Calidad',
                'Atención al Cliente',
                'Gestión Financiera'
            ]
            
            # Crear tabla RACI
            raci_data = [['Proceso'] + [pos['title'][:15] + '...' if len(pos['title']) > 15 else pos['title'] for pos in positions[:5]]]  # Limitar a 5 posiciones
            
            for process in processes:
                row = [process]
                for pos in positions[:5]:
                    # Asignar responsabilidad basada en el nivel y departamento
                    if pos.get('level', 1) == 1:
                        row.append('A')  # Accountable
                    elif pos.get('level', 1) == 2:
                        row.append('R')  # Responsible
                    else:
                        row.append('C')  # Consulted
                raci_data.append(row)
            
            raci_table = Table(raci_data)
            raci_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            matrix_content.append(raci_table)
            
            # Leyenda
            matrix_content.extend([
                Spacer(1, 0.3*inch),
                Paragraph("<b>Leyenda:</b>", styles['Normal']),
                Paragraph("R = Responsible (Responsable de ejecutar)", styles['Normal']),
                Paragraph("A = Accountable (Responsable de rendir cuentas)", styles['Normal']),
                Paragraph("C = Consulted (Consultado)", styles['Normal']),
                Paragraph("I = Informed (Informado)", styles['Normal'])
            ])
        
        return matrix_content
    
    def _create_appendices(self, heading_style, styles) -> List:
        """Crear anexos del documento"""
        
        appendices = [
            Paragraph("5. ANEXOS", heading_style),
            Spacer(1, 0.2*inch),
            
            Paragraph("5.1 Historial de Cambios", styles['Heading3']),
            Paragraph("Este organigrama ha sido actualizado según las necesidades organizacionales de ICASA.", styles['Normal']),
            Spacer(1, 0.2*inch),
            
            Paragraph("5.2 Referencias Normativas", styles['Heading3']),
            Paragraph("• ISO 9001:2015 - Sistemas de gestión de la calidad", styles['Normal']),
            Paragraph("• Ley Federal del Trabajo", styles['Normal']),
            Paragraph("• Reglamento Interno de ICASA", styles['Normal']),
            Spacer(1, 0.2*inch),
            
            Paragraph("5.3 Contacto", styles['Heading3']),
            Paragraph("Para consultas sobre este documento contactar a:", styles['Normal']),
            Paragraph("Departamento de Recursos Humanos", styles['Normal']),
            Paragraph("Email: rrhh@icasa.com", styles['Normal']),
            Paragraph("Teléfono: (55) 1234-5678", styles['Normal'])
        ]
        
        return appendices

class ExcelExporter(BaseExporter):
    """Exportador a Excel para análisis y nómina"""
    
    def export_flat_structure(self) -> HttpResponse:
        """Exportar estructura plana para análisis"""
        
        # Crear DataFrame
        data = []
        
        if self.chart.chart_data and 'positions' in self.chart.chart_data:
            positions = self.chart.chart_data['positions']
            
            for pos in positions:
                # Buscar nombre del jefe
                reports_to_name = ""
                if pos.get('reports_to'):
                    for p in positions:
                        if p['id'] == pos['reports_to']:
                            reports_to_name = p['title']
                            break
                
                data.append({
                    'ID_Puesto': pos['id'],
                    'Nombre_Puesto': pos['title'],
                    'Departamento': pos['department'],
                    'Nivel': pos.get('level', 1),
                    'ID_Jefe': pos.get('reports_to', ''),
                    'Nombre_Jefe': reports_to_name,
                    'Empleado_Actual': pos.get('current_employee', 'VACANTE'),
                    'Responsabilidades': pos.get('responsibilities', ''),
                    'Estado': 'Ocupado' if pos.get('current_employee') else 'Vacante',
                    'Fecha_Actualizacion': self.export_date.strftime('%d/%m/%Y')
                })
        
        df = pd.DataFrame(data)
        
        # Crear archivo Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Hoja principal
            df.to_excel(writer, sheet_name='Estructura_Organizacional', index=False)
            
            # Hoja de estadísticas
            stats_data = {
                'Métrica': [
                    'Total de Puestos',
                    'Puestos Ocupados',
                    'Puestos Vacantes',
                    'Porcentaje de Ocupación',
                    'Niveles Jerárquicos'
                ],
                'Valor': [
                    len(data),
                    len([d for d in data if d['Estado'] == 'Ocupado']),
                    len([d for d in data if d['Estado'] == 'Vacante']),
                    f"{(len([d for d in data if d['Estado'] == 'Ocupado']) / len(data) * 100):.1f}%" if data else "0%",
                    len(set(d['Nivel'] for d in data)) if data else 0
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estadisticas', index=False)
        
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"Estructura_Organizacional_{self.chart.department}_{self.export_date.strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

class PowerPointExporter(BaseExporter):
    """Exportador a PowerPoint para presentaciones"""
    
    def export_presentation(self) -> HttpResponse:
        """Exportar presentación de PowerPoint (placeholder)"""
        
        # Nota: Para implementación completa se necesitaría python-pptx
        # Por ahora, exportamos como JSON que puede ser importado
        
        presentation_data = {
            'title': f"Organigrama {self.chart.department}",
            'metadata': self.get_chart_metadata(),
            'slides': [
                {
                    'title': 'Portada',
                    'content': f"Organigrama del Departamento de {self.chart.department}"
                },
                {
                    'title': 'Estructura Organizacional',
                    'content': self.chart.chart_data
                }
            ]
        }
        
        # Convertir a JSON
        json_data = json.dumps(presentation_data, indent=2, default=str)
        
        response = HttpResponse(json_data, content_type='application/json')
        filename = f"Presentacion_{self.chart.department}_{self.export_date.strftime('%Y%m%d')}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

# Funciones de utilidad

def get_exporter(export_type: str, chart: DepartmentalChart):
    """Factory para obtener el exportador apropiado"""
    
    exporters = {
        'pdf': PDFExporter,
        'excel': ExcelExporter,
        'powerpoint': PowerPointExporter
    }
    
    if export_type not in exporters:
        raise ValueError(f"Tipo de exportador no soportado: {export_type}")
    
    return exporters[export_type](chart)

def export_chart(chart: DepartmentalChart, export_type: str) -> HttpResponse:
    """Función principal para exportar organigrama"""
    
    exporter = get_exporter(export_type, chart)
    
    if export_type == 'pdf':
        return exporter.export_organizational_book()
    elif export_type == 'excel':
        return exporter.export_flat_structure()
    elif export_type == 'powerpoint':
        return exporter.export_presentation()
    else:
        raise ValueError(f"Método de exportación no definido para: {export_type}")