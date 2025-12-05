from apps.organizational.models import Employee, PositionAssignment

print("=== CORRIGIENDO EMPLEADOS DIRECTAMENTE ===")

# Buscar empleados específicos con IDs problemáticos
problem_ids = ['IC1000', 'IC1001', 'IC1002', 'IC2001', 'IC2002', 'IC2003']

for emp_id in problem_ids:
    try:
        employee = Employee.objects.get(employee_id=emp_id)
        print(f"Encontrado empleado problemático: {emp_id} - {repr(employee.first_name)} {repr(employee.last_name)}")
        
        # Eliminar asignaciones primero
        assignments = PositionAssignment.objects.filter(employee=employee)
        if assignments.exists():
            print(f"  Eliminando {assignments.count()} asignaciones")
            assignments.delete()
        
        # Eliminar empleado
        employee.delete()
        print(f"  Empleado {emp_id} eliminado")
        
    except Employee.DoesNotExist:
        print(f"Empleado {emp_id} no encontrado")

print(f"\nEmpleados restantes: {Employee.objects.count()}")

# Verificar que los empleados correctos siguen existiendo
correct_employees = [
    ('IC3000', 'Carlos', 'García'),
    ('IC3001', 'María', 'Rodríguez'), 
    ('IC3002', 'José', 'González'),
    ('IC3003', 'Ana', 'Fernández'),
    ('IC3004', 'Luis', 'López'),
    ('IC3005', 'Carmen', 'Martínez')
]

print("\n=== VERIFICANDO EMPLEADOS CORRECTOS ===")
for emp_id, first, last in correct_employees:
    try:
        employee = Employee.objects.get(employee_id=emp_id)
        print(f"✓ {emp_id}: {employee.first_name} {employee.last_name}")
    except Employee.DoesNotExist:
        print(f"✗ {emp_id}: NO ENCONTRADO")