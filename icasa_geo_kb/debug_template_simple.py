from apps.organizational.models import Position, Employee, PositionAssignment
from django.utils import timezone

print("=== DEBUG: Verificando datos del template ===")

# Obtener todas las posiciones
positions = Position.objects.all().order_by('level', 'department')

print(f"\nTotal de posiciones: {positions.count()}")

for position in positions[:10]:  # Solo las primeras 10 para no saturar
    employee = position.get_current_employee()
    is_vacant = position.is_vacant()
    
    print(f"\n--- {position.title} ---")
    print(f"ID: {position.id}")
    print(f"get_current_employee(): {employee}")
    print(f"is_vacant(): {is_vacant}")
    
    if employee:
        print(f"Empleado: {employee.first_name} {employee.last_name}")
    else:
        print("Sin empleado asignado")

print("\n=== RESUMEN ===")
vacant_count = sum(1 for pos in positions if pos.is_vacant())
filled_count = positions.count() - vacant_count
print(f"Posiciones ocupadas: {filled_count}")
print(f"Posiciones vacantes: {vacant_count}")