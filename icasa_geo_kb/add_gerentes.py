from apps.organizational.models import Position

print("=== AGREGANDO GERENTES ===")

# Obtener Director Comercial
director_comercial = Position.objects.get(title='Director Comercial')
print(f"Director Comercial encontrado: {director_comercial.title}")

# Crear los 4 gerentes
gerentes = [
    ('Gerente de Operaciones', 'Operaciones'),
    ('Gerente de Porteo', 'Porteo'), 
    ('Gerente de Estaciones', 'Estaciones'),
    ('Gerente de Mantenimiento', 'Mantenimiento')
]

for title, department in gerentes:
    gerente = Position.objects.create(
        title=title,
        department=department,
        level=3,
        reports_to=director_comercial,
        responsibilities=f'Gestion y supervision del area de {department.lower()}'
    )
    print(f"✓ Creado: {gerente.title}")

print("\n=== ESTRUCTURA FINAL ===")
positions = Position.objects.all().order_by('level', 'title')
for position in positions:
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    print(f"Nivel {position.level}: {position.title} -> Reporta a: {reports_to}")

print(f"\nTotal puestos: {positions.count()}")