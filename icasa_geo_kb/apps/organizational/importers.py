"""
Importadores universales para organigramas
Soporta Excel, CSV, JSON y futuros conectores API
"""
import pandas as pd
import json
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from .models import DepartmentalChart, ImportLog
from typing import Dict, List, Tuple, Any

class OrganizationalImporter:
    """Clase base para importadores de organigramas"""
    
    def __init__(self, user: User):
        self.user = user
        self.errors = []
        self.warnings = []
        self.processed_records = 0
        self.success_records = 0
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> bool:
        """Validar que existan los campos requeridos"""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            self.errors.append(f"Campos faltantes: {', '.join(missing_fields)}")
            return False
        return True
    
    def create_import_log(self, chart: DepartmentalChart, import_type: str, file_name: str = "") -> ImportLog:
        """Crear registro de importación"""
        return ImportLog.objects.create(
            chart=chart,
            import_type=import_type,
            file_name=file_name,
            records_processed=self.processed_records,
            records_success=self.success_records,
            records_errors=len(self.errors),
            error_log=self.errors,
            imported_by=self.user
        )

class ExcelImporter(OrganizationalImporter):
    """Importador para archivos Excel/CSV con estructura organizacional"""
    
    REQUIRED_COLUMNS = ['id_puesto', 'nombre_puesto', 'departamento']
    OPTIONAL_COLUMNS = ['id_jefe', 'nivel', 'responsabilidades', 'empleado_actual']
    
    def import_from_file(self, file: UploadedFile, chart_name: str, department: str) -> Tuple[bool, DepartmentalChart]:
        """Importar organigrama desde archivo Excel/CSV"""
        
        try:
            # Leer archivo
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validar columnas requeridas
            missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                self.errors.append(f"Columnas faltantes en el archivo: {', '.join(missing_cols)}")
                return False, None
            
            # Crear organigrama
            chart = DepartmentalChart.objects.create(
                name=chart_name,
                department=department,
                description=f"Importado desde {file.name}",
                created_by=self.user,
                status='draft',
                import_source='excel' if file.name.endswith('.xlsx') else 'csv',
                import_metadata={
                    'file_name': file.name,
                    'total_rows': len(df),
                    'columns': list(df.columns)
                }
            )
            
            # Procesar datos
            positions_data = []
            self.processed_records = len(df)
            
            for index, row in df.iterrows():
                try:
                    position_data = self._process_row(row, index)
                    if position_data:
                        positions_data.append(position_data)
                        self.success_records += 1
                except Exception as e:
                    self.errors.append(f"Error en fila {index + 2}: {str(e)}")
            
            # Construir estructura jerárquica
            org_structure = self._build_hierarchy(positions_data)
            
            # Guardar en el organigrama
            chart.chart_data = {
                'positions': positions_data,
                'hierarchy': org_structure,
                'import_stats': {
                    'total_processed': self.processed_records,
                    'successful': self.success_records,
                    'errors': len(self.errors)
                }
            }
            chart.save()
            
            # Crear log de importación
            self.create_import_log(chart, 'excel', file.name)
            
            return True, chart
            
        except Exception as e:
            self.errors.append(f"Error general de importación: {str(e)}")
            return False, None
    
    def _process_row(self, row: pd.Series, index: int) -> Dict:
        """Procesar una fila del archivo"""
        
        # Validar datos requeridos
        required_data = {
            'id_puesto': str(row['id_puesto']).strip(),
            'nombre_puesto': str(row['nombre_puesto']).strip(),
            'departamento': str(row['departamento']).strip()
        }
        
        if not self.validate_required_fields(required_data, ['id_puesto', 'nombre_puesto', 'departamento']):
            raise ValueError(f"Datos requeridos faltantes en fila {index + 2}")
        
        # Construir datos del puesto
        position_data = {
            'id': required_data['id_puesto'],
            'title': required_data['nombre_puesto'],
            'department': required_data['departamento'],
            'level': int(row.get('nivel', 1)) if pd.notna(row.get('nivel')) else 1,
            'reports_to': str(row.get('id_jefe', '')).strip() if pd.notna(row.get('id_jefe')) else None,
            'responsibilities': str(row.get('responsabilidades', '')).strip() if pd.notna(row.get('responsabilidades')) else '',
            'current_employee': str(row.get('empleado_actual', '')).strip() if pd.notna(row.get('empleado_actual')) else None,
            'x_position': 0,  # Se calculará automáticamente
            'y_position': 0   # Se calculará automáticamente
        }
        
        return position_data
    
    def _build_hierarchy(self, positions: List[Dict]) -> Dict:
        """Construir estructura jerárquica a partir de las posiciones"""
        
        # Crear mapa de posiciones
        position_map = {pos['id']: pos for pos in positions}
        
        # Encontrar raíces (sin jefe)
        roots = [pos for pos in positions if not pos['reports_to']]
        
        # Construir árbol
        hierarchy = {
            'roots': [pos['id'] for pos in roots],
            'children': {},
            'levels': {}
        }
        
        # Mapear hijos
        for pos in positions:
            if pos['reports_to'] and pos['reports_to'] in position_map:
                parent_id = pos['reports_to']
                if parent_id not in hierarchy['children']:
                    hierarchy['children'][parent_id] = []
                hierarchy['children'][parent_id].append(pos['id'])
        
        # Calcular niveles
        self._calculate_levels(hierarchy, position_map)
        
        return hierarchy
    
    def _calculate_levels(self, hierarchy: Dict, position_map: Dict):
        """Calcular niveles jerárquicos y posiciones"""
        
        def assign_level(pos_id: str, level: int):
            if pos_id in position_map:
                position_map[pos_id]['level'] = level
                hierarchy['levels'][pos_id] = level
                
                # Asignar nivel a hijos
                if pos_id in hierarchy['children']:
                    for child_id in hierarchy['children'][pos_id]:
                        assign_level(child_id, level + 1)
        
        # Asignar niveles desde las raíces
        for root_id in hierarchy['roots']:
            assign_level(root_id, 1)
    
    def generate_template(self) -> pd.DataFrame:
        """Generar plantilla Excel para importación"""
        
        template_data = {
            'id_puesto': ['DIR001', 'GER001', 'GER002', 'SUP001', 'EMP001'],
            'nombre_puesto': ['Director General', 'Gerente Administrativo', 'Gerente Comercial', 'Supervisor Ventas', 'Ejecutivo Ventas'],
            'departamento': ['Dirección', 'Administrativo', 'Comercial', 'Comercial', 'Comercial'],
            'id_jefe': ['', 'DIR001', 'DIR001', 'GER002', 'SUP001'],
            'nivel': [1, 2, 2, 3, 4],
            'responsabilidades': [
                'Dirección estratégica general',
                'Gestión administrativa y RRHH',
                'Desarrollo comercial y ventas',
                'Supervisión equipo de ventas',
                'Ejecución de ventas'
            ],
            'empleado_actual': ['Carlos Mendoza', 'Ana García', 'Roberto Silva', '', '']
        }
        
        return pd.DataFrame(template_data)

class JSONImporter(OrganizationalImporter):
    """Importador para archivos JSON con estructura organizacional"""
    
    def import_from_json(self, json_data: Dict, chart_name: str, department: str) -> Tuple[bool, DepartmentalChart]:
        """Importar organigrama desde datos JSON"""
        
        try:
            # Validar estructura JSON
            if 'positions' not in json_data:
                self.errors.append("El JSON debe contener un array 'positions'")
                return False, None
            
            positions = json_data['positions']
            if not isinstance(positions, list):
                self.errors.append("'positions' debe ser un array")
                return False, None
            
            # Crear organigrama
            chart = DepartmentalChart.objects.create(
                name=chart_name,
                department=department,
                description="Importado desde JSON",
                created_by=self.user,
                status='draft',
                import_source='json',
                import_metadata={
                    'total_positions': len(positions),
                    'json_structure': list(json_data.keys())
                }
            )
            
            # Procesar posiciones
            processed_positions = []
            self.processed_records = len(positions)
            
            for i, pos_data in enumerate(positions):
                try:
                    processed_pos = self._process_json_position(pos_data, i)
                    if processed_pos:
                        processed_positions.append(processed_pos)
                        self.success_records += 1
                except Exception as e:
                    self.errors.append(f"Error en posición {i + 1}: {str(e)}")
            
            # Guardar datos
            chart.chart_data = {
                'positions': processed_positions,
                'metadata': json_data.get('metadata', {}),
                'import_stats': {
                    'total_processed': self.processed_records,
                    'successful': self.success_records,
                    'errors': len(self.errors)
                }
            }
            chart.save()
            
            # Crear log
            self.create_import_log(chart, 'json')
            
            return True, chart
            
        except Exception as e:
            self.errors.append(f"Error de importación JSON: {str(e)}")
            return False, None
    
    def _process_json_position(self, pos_data: Dict, index: int) -> Dict:
        """Procesar una posición del JSON"""
        
        required_fields = ['id', 'title', 'department']
        if not self.validate_required_fields(pos_data, required_fields):
            raise ValueError(f"Campos requeridos faltantes en posición {index + 1}")
        
        return {
            'id': str(pos_data['id']),
            'title': str(pos_data['title']),
            'department': str(pos_data['department']),
            'level': pos_data.get('level', 1),
            'reports_to': pos_data.get('reports_to'),
            'responsibilities': pos_data.get('responsibilities', ''),
            'current_employee': pos_data.get('current_employee'),
            'x_position': pos_data.get('x_position', 0),
            'y_position': pos_data.get('y_position', 0),
            'metadata': pos_data.get('metadata', {})
        }

class APIConnector(OrganizationalImporter):
    """Conector para APIs externas (futuro)"""
    
    def __init__(self, user: User, api_config: Dict):
        super().__init__(user)
        self.api_config = api_config
    
    def import_from_api(self, chart_name: str, department: str) -> Tuple[bool, DepartmentalChart]:
        """Importar desde API externa (placeholder para futuro desarrollo)"""
        
        # Placeholder para conectores futuros como:
        # - Workday API
        # - SAP SuccessFactors
        # - BambooHR
        # - Otros sistemas de RRHH
        
        self.errors.append("Conectores API en desarrollo")
        return False, None

# Funciones de utilidad

def get_importer(import_type: str, user: User, **kwargs) -> OrganizationalImporter:
    """Factory para obtener el importador apropiado"""
    
    importers = {
        'excel': ExcelImporter,
        'csv': ExcelImporter,
        'json': JSONImporter,
        'api': APIConnector
    }
    
    if import_type not in importers:
        raise ValueError(f"Tipo de importador no soportado: {import_type}")
    
    return importers[import_type](user, **kwargs)

def generate_excel_template() -> pd.DataFrame:
    """Generar plantilla Excel para descarga"""
    importer = ExcelImporter(None)
    return importer.generate_template()

def validate_import_file(file: UploadedFile) -> Tuple[bool, List[str]]:
    """Validar archivo antes de importar"""
    
    errors = []
    
    # Validar extensión
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_ext = '.' + file.name.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        errors.append(f"Extensión no permitida: {file_ext}. Permitidas: {', '.join(allowed_extensions)}")
    
    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        errors.append(f"Archivo muy grande: {file.size / 1024 / 1024:.1f}MB. Máximo: 10MB")
    
    return len(errors) == 0, errors