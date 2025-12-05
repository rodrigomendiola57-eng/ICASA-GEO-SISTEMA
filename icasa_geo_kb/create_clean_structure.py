from apps.organizational.models import Position, Employee, PositionAssignment
from django.utils import timezone
from datetime import date

print("=== CREANDO ESTRUCTURA LIMPIA ===")

# 1. LIMPIAR TODO
print("1. Limpiando estructura existente...")
Position.objects.all().delete()
print("Todas las posiciones eliminadas")

# 2. CREAR EMPLEADOS SI NO EXISTEN
print("\n2. Verificando empleados...")

# Crear empleados clave si no existen
empleados_clave = [
    {'employee_id': 'IC1000', 'first_name': 'Carlos', 'last_name': 'García', 'email': 'carlos.garcia@icasa.com'},
    {'employee_id': 'IC1001', 'first_name': 'María', 'last_name': 'Rodríguez', 'email': 'maria.rodriguez@icasa.com'},
    {'employee_id': 'IC1002', 'first_name': 'José', 'last_name': 'González', 'email': 'jose.gonzalez@icasa.com'},
    {'employee_id': 'IC2001', 'first_name': 'Ana', 'last_name': 'Fernández', 'email': 'ana.fernandez@icasa.com'},
    {'employee_id': 'IC2002', 'first_name': 'Luis', 'last_name': 'López', 'email': 'luis.lopez@icasa.com'},
    {'employee_id': 'IC2003', 'first_name': 'Carmen', 'last_name': 'Martínez', 'email': 'carmen.martinez@icasa.com'},
]

for emp_data in empleados_clave:
    employee, created = Employee.objects.get_or_create(
        employee_id=emp_data['employee_id'],
        defaults={
            'first_name': emp_data['first_name'],
            'last_name': emp_data['last_name'],
            'email': emp_data['email'],
            'hire_date': date(2020, 1, 1),
            'is_active': True
        }
    )
    if created:
        print(f"Empleado creado: {employee.first_name} {employee.last_name}")
    else:
        print(f"Empleado existente: {employee.first_name} {employee.last_name}")

# 3. CREAR ESTRUCTURA ORGANIZACIONAL LIMPIA
print("\n3. Creando estructura organizacional...")

# NIVEL 1: DIRECTOR GENERAL
director_general = Position.objects.create(
    title='Director General',
    department='Direccion General',
    level=1,
    reports_to=None,
    x_position=1000,
    y_position=200,
    responsibilities='Direccion estrategica y liderazgo general de ICASA'
)
print(f"Creado: {director_general.title}")

# NIVEL 2: DIRECTORES
director_comercial = Position.objects.create(
    title='Director Comercial',
    department='Direccion Comercial',
    level=2,
    reports_to=director_general,
    x_position=600,
    y_position=600,
    responsibilities='Supervision de operaciones comerciales y gerencias operativas'
)
print(f"Creado: {director_comercial.title}")

director_administrativo = Position.objects.create(
    title='Director Administrativo',
    department='Direccion Administrativa',
    level=2,
    reports_to=director_general,
    x_position=1400,
    y_position=600,
    responsibilities='Gestion administrativa, financiera y recursos humanos'
)
print(f"Creado: {director_administrativo.title}")

# NIVEL 3: GERENTES (reportan al Director Comercial)
gerente_operaciones = Position.objects.create(
    title='Gerente de Operaciones',
    department='Operaciones',
    level=3,
    reports_to=director_comercial,
    x_position=200,
    y_position=1000,
    responsibilities='Gestion de operaciones diarias y procesos operativos'
)
print(f"Creado: {gerente_operaciones.title}")

gerente_porteo = Position.objects.create(
    title='Gerente de Porteo',
    department='Porteo',
    level=3,
    reports_to=director_comercial,
    x_position=600,
    y_position=1000,
    responsibilities='Supervision de servicios de porteo y logistica'
)
print(f"Creado: {gerente_porteo.title}")

gerente_devoluciones = Position.objects.create(
    title='Gerente de Devoluciones',
    department='Devoluciones',
    level=3,
    reports_to=director_comercial,
    x_position=1000,
    y_position=1000,
    responsibilities='Gestion de procesos de devoluciones y atencion al cliente'
)
print(f"Creado: {gerente_devoluciones.title}")

# 4. ASIGNAR EMPLEADOS A POSICIONES
print("\n4. Asignando empleados a posiciones...")

asignaciones = [
    (director_general, 'IC1000'),  # Carlos García
    (director_comercial, 'IC1001'),  # María Rodríguez
    (director_administrativo, 'IC1002'),  # José González
    (gerente_operaciones, 'IC2001'),  # Ana Fernández
    (gerente_porteo, 'IC2002'),  # Luis López
    (gerente_devoluciones, 'IC2003'),  # Carmen Martínez
]

for position, emp_id in asignaciones:
    try:
        employee = Employee.objects.get(employee_id=emp_id)
        assignment = PositionAssignment.objects.create(
            position=position,
            employee=employee,
            start_date=date(2024, 1, 1),
            assignment_type='permanent'
        )
        print(f"Asignado: {employee.first_name} {employee.last_name} -> {position.title}")
    except Employee.DoesNotExist:
        print(f"ERROR: Empleado {emp_id} no encontrado")

# 5. MOSTRAR ESTRUCTURA FINAL
print("\n=== ESTRUCTURA FINAL ===")
positions = Position.objects.all().order_by('level', 'title')

for position in positions:
    employee = position.get_current_employee()
    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "VACANTE"
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    
    print(f"Nivel {position.level}: {position.title} ({position.department})")
    print(f"  Empleado: {employee_name}")
    print(f"  Reporta a: {reports_to}")
    print(f"  Posición: ({position.x_position}, {position.y_position})")
    print()

print(f"Total de posiciones: {positions.count()}")
print("Estructura limpia creada ✅")