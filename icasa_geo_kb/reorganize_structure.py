from apps.organizational.models import Position, Employee, PositionAssignment
from django.utils import timezone

print("=== REORGANIZANDO ESTRUCTURA ORGANIZACIONAL ===")

# 1. ELIMINAR POSICIONES QUE NO NECESITAMOS
print("\n1. Eliminando posiciones innecesarias...")

# Eliminar todos los niveles 4 y 5 (Operadores y Auxiliares)
positions_to_delete = Position.objects.filter(level__in=[4, 5])
print(f"Eliminando {positions_to_delete.count()} posiciones de niveles 4 y 5")
positions_to_delete.delete()

# Eliminar todos los Jefes (nivel 3)
jefes_to_delete = Position.objects.filter(level=3)
print(f"Eliminando {jefes_to_delete.count()} jefes (nivel 3)")
jefes_to_delete.delete()

# 2. MANTENER SOLO LOS DEPARTAMENTOS ESPECIFICADOS
print("\n2. Limpiando departamentos...")

# Departamentos a mantener
departamentos_mantener = ['Devoluciones', 'Operaciones', 'Porteo', 'Dirección General']

# Eliminar posiciones de otros departamentos
other_depts = Position.objects.exclude(department__in=departamentos_mantener)
print(f"Eliminando {other_depts.count()} posiciones de otros departamentos")
other_depts.delete()

# 3. REORGANIZAR LA JERARQUÍA
print("\n3. Reorganizando jerarquía...")

# Obtener el Director General
director_general = Position.objects.filter(title__icontains='Director General').first()
if director_general:
    print(f"Director General encontrado: {director_general.title}")
    director_general.level = 1
    director_general.department = 'Dirección General'
    director_general.reports_to = None
    director_general.save()

# Obtener los otros directores y hacerlos reportar al Director General
directores = Position.objects.filter(title__icontains='Director').exclude(id=director_general.id if director_general else 0)
for director in directores:
    print(f"Configurando director: {director.title}")
    director.level = 2
    director.reports_to = director_general
    director.save()

# Obtener los gerentes y hacerlos reportar al Director Comercial
director_comercial = Position.objects.filter(title__icontains='Director Comercial').first()
gerentes = Position.objects.filter(title__icontains='Gerente')

if director_comercial:
    for gerente in gerentes:
        print(f"Configurando gerente: {gerente.title} -> reporta a {director_comercial.title}")
        gerente.level = 3
        gerente.reports_to = director_comercial
        gerente.save()

# 4. MOSTRAR ESTRUCTURA FINAL
print("\n=== ESTRUCTURA FINAL ===")
positions = Position.objects.all().order_by('level', 'department', 'title')

for position in positions:
    employee = position.get_current_employee()
    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "VACANTE"
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    
    print(f"Nivel {position.level}: {position.title} ({position.department})")
    print(f"  Empleado: {employee_name}")
    print(f"  Reporta a: {reports_to}")
    print()

print(f"\nTotal de posiciones restantes: {positions.count()}")
print("Reorganización completada ✅")