from apps.organizational.models import Position

print("=== ORGANIZANDO POSICIONES VISUALES ===")

# Coordenadas organizadas para evitar entrecruzamiento
positions_coords = {
    # Nivel 1 - Centro superior
    'Director General': (1000, 100),
    
    # Nivel 2 - Separados horizontalmente
    'Director Comercial': (500, 400),      # Izquierda
    'Director Administrativo': (1500, 400), # Derecha
    
    # Nivel 3 - Gerencias Comerciales (Izquierda)
    'Gerente de Operaciones': (100, 700),
    'Gerente de Porteo': (300, 700),
    'Gerente de Estaciones': (500, 700),
    'Gerente de Mantenimiento': (700, 700),
    
    # Nivel 3 - Gerencias Administrativas (Derecha)
    'Gerente de Normatividad': (1100, 700),
    'Gerente de Recursos Humanos': (1300, 700),
    'Gerente de Finanzas': (1500, 700),
    'Gerente de Nomina': (1700, 700)
}

# Actualizar posiciones
for title, (x, y) in positions_coords.items():
    try:
        position = Position.objects.get(title=title)
        position.x_position = x
        position.y_position = y
        position.save()
        print(f"✓ {title}: ({x}, {y})")
    except Position.DoesNotExist:
        print(f"✗ No encontrado: {title}")

print("\n=== POSICIONES ORGANIZADAS ===")
print("Lado IZQUIERDO (Comercial):")
print("- Director Comercial y sus 4 gerentes")
print("\nLado DERECHO (Administrativo):")
print("- Director Administrativo y sus 4 gerentes")
print("\nCENTRO:")
print("- Director General")

print(f"\nTotal puestos actualizados: {len(positions_coords)}")