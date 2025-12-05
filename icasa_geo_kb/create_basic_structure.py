from apps.organizational.models import Position

print("=== CREANDO ESTRUCTURA BASICA ===")

# 1. Director General (Nivel 1)
director_general = Position.objects.create(
    title='Director General',
    department='Direccion General',
    level=1,
    reports_to=None,
    x_position=1000,
    y_position=200,
    responsibilities='Direccion estrategica y liderazgo general de ICASA'
)
print(f"✓ Creado: {director_general.title}")

# 2. Director Comercial (Nivel 2, reporta al Director General)
director_comercial = Position.objects.create(
    title='Director Comercial',
    department='Direccion Comercial',
    level=2,
    reports_to=director_general,
    x_position=600,
    y_position=600,
    responsibilities='Supervision de operaciones comerciales y ventas'
)
print(f"✓ Creado: {director_comercial.title}")

# 3. Director Administrativo (Nivel 2, reporta al Director General)
director_administrativo = Position.objects.create(
    title='Director Administrativo',
    department='Direccion Administrativa',
    level=2,
    reports_to=director_general,
    x_position=1400,
    y_position=600,
    responsibilities='Gestion administrativa, financiera y recursos humanos'
)
print(f"✓ Creado: {director_administrativo.title}")

print("\n=== ESTRUCTURA CREADA ===")
positions = Position.objects.all().order_by('level', 'title')
for position in positions:
    reports_to = position.reports_to.title if position.reports_to else "NADIE"
    print(f"Nivel {position.level}: {position.title} -> Reporta a: {reports_to}")

print(f"\nTotal de puestos: {positions.count()}")
print("Estructura basica lista!")