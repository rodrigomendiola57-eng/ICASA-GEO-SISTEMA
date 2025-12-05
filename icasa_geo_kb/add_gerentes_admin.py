from apps.organizational.models import Position

print("=== AGREGANDO GERENTES ADMINISTRATIVOS ===")

# Obtener Director Administrativo
director_admin = Position.objects.get(title='Director Administrativo')
print(f"Director Administrativo encontrado: {director_admin.title}")

# Crear los 4 gerentes administrativos
gerentes_admin = [
    ('Gerente de Normatividad', 'Normatividad'),
    ('Gerente de Recursos Humanos', 'Recursos Humanos'), 
    ('Gerente de Finanzas', 'Finanzas'),
    ('Gerente de Nomina', 'Nomina')
]

for title, department in gerentes_admin:
    gerente = Position.objects.create(
        title=title,
        department=department,
        level=3,
        reports_to=director_admin,
        responsibilities=f'Gestion y supervision del area de {department.lower()}'
    )
    print(f"✓ Creado: {gerente.title}")

print("\n=== ESTRUCTURA COMPLETA ===")
positions = Position.objects.all().order_by('level', 'title')
for position in positions:
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    print(f"Nivel {position.level}: {position.title} -> Reporta a: {reports_to}")

print(f"\nTotal puestos: {positions.count()}")