from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.organizational.models import Position, Employee, PositionAssignment, DepartmentalChart
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el módulo organizacional'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando datos de ejemplo para ICASA...'))
        
        # Crear usuarios de ejemplo
        admin_user, created = User.objects.get_or_create(
            username='admin_icasa',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'ICASA',
                'email': 'admin@icasa.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Crear estructura organizacional de ICASA
        self.create_icasa_structure()
        
        # Crear empleados
        self.create_employees()
        
        # Asignar empleados a puestos
        self.assign_employees()
        
        # Crear organigramas departamentales de ejemplo
        self.create_departmental_charts(admin_user)
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de ejemplo creados exitosamente'))

    def create_icasa_structure(self):
        """Crear la estructura organizacional de ICASA"""
        
        # 1. Director General
        director_general = Position.objects.get_or_create(
            title='Director General',
            defaults={
                'department': 'Dirección General',
                'level': 1,
                'responsibilities': 'Dirección estratégica y liderazgo general de ICASA',
                'x_position': 1000,
                'y_position': 200
            }
        )[0]
        
        # 2. Directores (Nivel 2)
        director_admin = Position.objects.get_or_create(
            title='Director Administrativo',
            defaults={
                'department': 'Administrativo',
                'level': 2,
                'reports_to': director_general,
                'responsibilities': 'Supervisión de operaciones administrativas y recursos humanos',
                'x_position': 600,
                'y_position': 500
            }
        )[0]
        
        director_comercial = Position.objects.get_or_create(
            title='Director Comercial',
            defaults={
                'department': 'Comercial',
                'level': 2,
                'reports_to': director_general,
                'responsibilities': 'Desarrollo comercial y relaciones con clientes',
                'x_position': 1400,
                'y_position': 500
            }
        )[0]
        
        # 3. Gerentes Administrativos (Nivel 3)
        gerentes_admin = [
            ('Gerente de Recursos Humanos', 'RRHH'),
            ('Gerente de Finanzas', 'Finanzas'),
            ('Gerente de Sistemas', 'Sistemas'),
            ('Gerente de Mantenimiento', 'Mantenimiento')
        ]
        
        x_positions_admin = [200, 400, 600, 800]
        for i, (titulo, dept) in enumerate(gerentes_admin):
            Position.objects.get_or_create(
                title=titulo,
                defaults={
                    'department': dept,
                    'level': 3,
                    'reports_to': director_admin,
                    'responsibilities': f'Gestión y supervisión del área de {dept}',
                    'x_position': x_positions_admin[i],
                    'y_position': 800
                }
            )
        
        # 4. Gerentes Comerciales (Nivel 3)
        gerentes_comerciales = [
            ('Gerente de Ventas', 'Comercial'),
            ('Gerente de Marketing', 'Comercial'),
            ('Gerente de Operaciones', 'Operaciones'),
            ('Gerente de Calidad', 'Calidad')
        ]
        
        x_positions_comercial = [1200, 1400, 1600, 1800]
        for i, (titulo, dept) in enumerate(gerentes_comerciales):
            Position.objects.get_or_create(
                title=titulo,
                defaults={
                    'department': dept,
                    'level': 3,
                    'reports_to': director_comercial,
                    'responsibilities': f'Gestión y supervisión del área de {dept}',
                    'x_position': x_positions_comercial[i],
                    'y_position': 800
                }
            )

    def create_employees(self):
        """Crear empleados de ejemplo"""
        
        empleados_data = [
            # Directivos
            ('Carlos', 'Mendoza', 'E001', 'carlos.mendoza@icasa.com', '2015-01-15'),
            ('Ana', 'García', 'E002', 'ana.garcia@icasa.com', '2016-03-20'),
            ('Roberto', 'Silva', 'E003', 'roberto.silva@icasa.com', '2017-05-10'),
            
            # Gerentes
            ('María', 'López', 'E004', 'maria.lopez@icasa.com', '2018-02-14'),
            ('Juan', 'Pérez', 'E005', 'juan.perez@icasa.com', '2018-06-01'),
            ('Laura', 'Martínez', 'E006', 'laura.martinez@icasa.com', '2019-01-20'),
            ('Diego', 'Rodríguez', 'E007', 'diego.rodriguez@icasa.com', '2019-04-15'),
            ('Carmen', 'Hernández', 'E008', 'carmen.hernandez@icasa.com', '2020-01-10'),
            ('Miguel', 'Torres', 'E009', 'miguel.torres@icasa.com', '2020-03-25'),
            ('Patricia', 'Ramírez', 'E010', 'patricia.ramirez@icasa.com', '2020-07-12'),
            ('Fernando', 'Jiménez', 'E011', 'fernando.jimenez@icasa.com', '2021-02-08'),
        ]
        
        for first_name, last_name, emp_id, email, hire_date in empleados_data:
            Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'hire_date': hire_date,
                    'phone': f'555-{random.randint(1000, 9999)}',
                    'is_active': True
                }
            )

    def assign_employees(self):
        """Asignar empleados a puestos"""
        
        # Obtener puestos y empleados
        positions = list(Position.objects.all().order_by('level', 'title'))
        employees = list(Employee.objects.all())
        
        # Asignar empleados a puestos (algunos puestos quedarán vacantes)
        assignments = [
            ('Director General', 'E001'),
            ('Director Administrativo', 'E002'),
            ('Director Comercial', 'E003'),
            ('Gerente de Recursos Humanos', 'E004'),
            ('Gerente de Finanzas', 'E005'),
            ('Gerente de Sistemas', 'E006'),
            ('Gerente de Ventas', 'E008'),
            ('Gerente de Marketing', 'E009'),
            ('Gerente de Operaciones', 'E010'),
            # Dejar algunos puestos vacantes intencionalmente
        ]
        
        for position_title, employee_id in assignments:
            try:
                position = Position.objects.get(title=position_title)
                employee = Employee.objects.get(employee_id=employee_id)
                
                # Verificar si ya existe una asignación activa
                existing = PositionAssignment.objects.filter(
                    position=position,
                    end_date__isnull=True
                ).first()
                
                if not existing:
                    PositionAssignment.objects.create(
                        position=position,
                        employee=employee,
                        start_date=employee.hire_date,
                        assignment_type='permanent'
                    )
                    
            except (Position.DoesNotExist, Employee.DoesNotExist):
                continue

    def create_departmental_charts(self, admin_user):
        """Crear organigramas departamentales de ejemplo"""
        
        departamentos = [
            ('Organigrama Administrativo', 'Administrativo', 'Estructura organizacional del área administrativa'),
            ('Organigrama Comercial', 'Comercial', 'Estructura organizacional del área comercial'),
            ('Organigrama de Operaciones', 'Operaciones', 'Estructura organizacional del área de operaciones'),
        ]
        
        for name, department, description in departamentos:
            DepartmentalChart.objects.get_or_create(
                name=name,
                department=department,
                defaults={
                    'description': description,
                    'created_by': admin_user,
                    'status': 'active',
                    'is_external': False,
                    'chart_data': {
                        'positions': [],
                        'connections': [],
                        'metadata': {
                            'created_date': date.today().isoformat(),
                            'version': '1.0'
                        }
                    }
                }
            )
        
        self.stdout.write(f'✅ Creados {len(departamentos)} organigramas departamentales')