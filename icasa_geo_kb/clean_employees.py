from apps.organizational.models import Employee, PositionAssignment

print("=== LIMPIANDO EMPLEADOS DUPLICADOS ===")

# Identificar empleados con codificación incorrecta
bad_employees = []
for employee in Employee.objects.all():
    if 'Ã' in employee.first_name or 'Ã' in employee.last_name:
        bad_employees.append(employee)
        print(f"Empleado con codificación incorrecta: {employee.employee_id} - {employee.first_name} {employee.last_name}")

print(f"\nEncontrados {len(bad_employees)} empleados con codificación incorrecta")

# Eliminar empleados con codificación incorrecta
for employee in bad_employees:
    # Primero eliminar sus asignaciones
    assignments = PositionAssignment.objects.filter(employee=employee)
    print(f"Eliminando {assignments.count()} asignaciones de {employee.employee_id}")
    assignments.delete()
    
    # Luego eliminar el empleado
    employee.delete()
    print(f"Eliminado empleado: {employee.employee_id}")

print(f"\nLimpieza completada. Empleados restantes: {Employee.objects.count()}")

# Mostrar empleados finales
print("\n=== EMPLEADOS LIMPIOS ===")
for employee in Employee.objects.all().order_by('employee_id'):
    print(f"{employee.employee_id}: {employee.first_name} {employee.last_name}")