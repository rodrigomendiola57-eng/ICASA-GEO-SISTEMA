from apps.organizational.models import Position

print("=== TODOS LOS PUESTOS ===")

positions = Position.objects.all().order_by('id')
for position in positions:
    employee = position.get_current_employee()
    subordinates = Position.objects.filter(reports_to=position).count()
    
    print(f"ID {position.id}: {position.title}")
    print(f"  Departamento: {position.department}")
    print(f"  Empleado: {employee.first_name + ' ' + employee.last_name if employee else 'VACANTE'}")
    print(f"  Subordinados: {subordinates}")
    print(f"  Reporta a: {position.reports_to.title if position.reports_to else 'NADIE'}")
    print("---")

print(f"\nTotal puestos: {positions.count()}")