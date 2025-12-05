from apps.organizational.models import Position, Employee, PositionAssignment

print("=== LIMPIANDO TODA LA ESTRUCTURA ===")

# Eliminar todas las asignaciones
assignments_count = PositionAssignment.objects.count()
PositionAssignment.objects.all().delete()
print(f"Eliminadas {assignments_count} asignaciones")

# Eliminar todas las posiciones
positions_count = Position.objects.count()
Position.objects.all().delete()
print(f"Eliminadas {positions_count} posiciones")

# Mantener solo empleados con nombres limpios (IC3000 en adelante)
bad_employees = Employee.objects.filter(employee_id__startswith='IC1') | Employee.objects.filter(employee_id__startswith='IC2')
bad_count = bad_employees.count()
bad_employees.delete()
print(f"Eliminados {bad_count} empleados con codificacion incorrecta")

print(f"Empleados restantes: {Employee.objects.count()}")
print("Sistema limpio. Ahora puedes crear puestos manualmente desde la interfaz.")