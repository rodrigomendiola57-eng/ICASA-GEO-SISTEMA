from apps.organizational.models import Position, PositionAssignment

print("=== ELIMINANDO GERENTE GENERAL DUPLICADO ===")

try:
    gerente = Position.objects.get(id=115, title='Gerente general ')
    
    # Eliminar asignaciones primero
    assignments = PositionAssignment.objects.filter(position=gerente)
    if assignments.exists():
        print(f"Eliminando {assignments.count()} asignaciones")
        assignments.delete()
    
    # Eliminar el puesto
    gerente.delete()
    print("✓ Gerente general eliminado exitosamente")
    
except Position.DoesNotExist:
    print("✗ Gerente general no encontrado")

print("\n=== ESTRUCTURA FINAL ===")
positions = Position.objects.all().order_by('level', 'title')
for position in positions:
    employee = position.get_current_employee()
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    print(f"Nivel {position.level}: {position.title} -> Reporta a: {reports_to}")
    print(f"  Empleado: {employee.first_name + ' ' + employee.last_name if employee else 'VACANTE'}")

print(f"\nTotal puestos: {positions.count()}")