from apps.organizational.models import Position, Employee, PositionAssignment
from datetime import date

print("=== REASIGNANDO EMPLEADOS A PUESTOS ===")

# Mapeo de puestos a empleados correctos
assignments_map = {
    'Director General': 'IC3000',  # Carlos García
    'Director Comercial': 'IC3001',  # María Rodríguez  
    'Director Administrativo': 'IC3002',  # José González
    'Gerente de Operaciones': 'IC3003',  # Ana Fernández
    'Gerente de Porteo': 'IC3004',  # Luis López
    'Gerente de Devoluciones': 'IC3005',  # Carmen Martínez
}

for position_title, employee_id in assignments_map.items():
    try:
        position = Position.objects.get(title=position_title)
        employee = Employee.objects.get(employee_id=employee_id)
        
        # Verificar si ya tiene asignación activa
        existing = PositionAssignment.objects.filter(
            position=position,
            end_date__isnull=True
        ).first()
        
        if existing:
            print(f"⚠️  {position_title} ya tiene asignación activa")
            continue
            
        # Crear nueva asignación
        assignment = PositionAssignment.objects.create(
            position=position,
            employee=employee,
            start_date=date(2024, 1, 1),
            assignment_type='permanent'
        )
        
        print(f"✓ Asignado: {employee.first_name} {employee.last_name} -> {position_title}")
        
    except Position.DoesNotExist:
        print(f"✗ Puesto no encontrado: {position_title}")
    except Employee.DoesNotExist:
        print(f"✗ Empleado no encontrado: {employee_id}")

print("\n=== VERIFICACIÓN FINAL ===")
positions = Position.objects.all().order_by('level', 'title')
for position in positions:
    employee = position.get_current_employee()
    if employee:
        print(f"✓ {position.title}: {employee.first_name} {employee.last_name}")
    else:
        print(f"✗ {position.title}: VACANTE")