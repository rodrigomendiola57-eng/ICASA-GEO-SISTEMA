from apps.organizational.models import Position

print("=== ELIMINANDO DIRECTOR GENERAL DUPLICADO ===")

# Buscar todos los Director General
directors = Position.objects.filter(title='Director General')
print(f"Encontrados {directors.count()} Director General")

for director in directors:
    employee = director.get_current_employee()
    has_subordinates = Position.objects.filter(reports_to=director).exists()
    
    print(f"ID {director.id}: {director.title}")
    print(f"  Empleado: {employee.first_name + ' ' + employee.last_name if employee else 'VACANTE'}")
    print(f"  Subordinados: {'SI' if has_subordinates else 'NO'}")
    
    # Eliminar el que está vacante y no tiene subordinados
    if not employee and not has_subordinates:
        director.delete()
        print(f"  ✓ ELIMINADO (vacante sin subordinados)")
    else:
        print(f"  ✓ CONSERVADO")

print("\n=== VERIFICACION FINAL ===")
remaining = Position.objects.filter(title='Director General')
print(f"Director General restantes: {remaining.count()}")

for director in remaining:
    employee = director.get_current_employee()
    print(f"- {director.title}: {employee.first_name + ' ' + employee.last_name if employee else 'VACANTE'}")