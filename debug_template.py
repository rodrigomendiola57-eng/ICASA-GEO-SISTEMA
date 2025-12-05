import os
import django
import sys

# Configurar Django
sys.path.append('c:\\Sistema GEO (Gestión Estratégica Organizacional)\\icasa_geo_kb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.development')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment
from django.utils import timezone

print("=== DEBUG: Verificando datos del template ===")

# Obtener todas las posiciones
positions = Position.objects.all().order_by('level', 'department')

print(f"\nTotal de posiciones: {positions.count()}")

for position in positions:
    employee = position.get_current_employee()
    is_vacant = position.is_vacant()
    
    print(f"\n--- {position.title} ---")
    print(f"ID: {position.id}")
    print(f"Departamento: {position.department}")
    print(f"Nivel: {position.level}")
    print(f"get_current_employee(): {employee}")
    print(f"is_vacant(): {is_vacant}")
    
    if employee:
        print(f"Empleado: {employee.first_name} {employee.last_name}")
        print(f"Employee ID: {employee.employee_id}")
    else:
        print("Sin empleado asignado")
    
    # Verificar asignaciones activas
    active_assignments = position.assignments.filter(
        start_date__lte=timezone.now().date(),
        end_date__isnull=True
    )
    print(f"Asignaciones activas: {active_assignments.count()}")
    for assignment in active_assignments:
        print(f"  - {assignment.employee.first_name} {assignment.employee.last_name} desde {assignment.start_date}")

print("\n=== RESUMEN ===")
vacant_count = sum(1 for pos in positions if pos.is_vacant())
filled_count = positions.count() - vacant_count
print(f"Posiciones ocupadas: {filled_count}")
print(f"Posiciones vacantes: {vacant_count}")
print(f"Tasa de ocupación: {(filled_count / positions.count() * 100):.1f}%")