from apps.organizational.models import Position

print("=== ORGANIZANDO POSICIONES CORRECTAS ===")

# Coordenadas corregidas
positions_coords = {
    # Nivel 1 - Centro superior
    'Director General': (1000, 100),
    
    # Nivel 2 - Separados horizontalmente
    'Director Administrativo': (500, 400),   # Izquierda
    'Director Comercial': (1500, 400),      # Derecha
    
    # Nivel 3 - Gerencias Administrativas (Izquierda)
    'Gerente de Normatividad': (100, 700),
    'Gerente de Recursos Humanos': (300, 700),
    'Gerente de Finanzas': (500, 700),
    'Gerente de Nomina': (700, 700),
    
    # Nivel 3 - Gerencias Comerciales (Derecha)
    'Gerente de Operaciones': (1100, 700),
    'Gerente de Porteo': (1300, 700),
    'Gerente de Estaciones': (1500, 700),
    'Gerente de Mantenimiento': (1700, 700)
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

print("\n=== LAYOUT CORREGIDO ===")
print("Lado IZQUIERDO (Administrativo):")
print("- Director Administrativo y sus 4 gerentes")
print("\nLado DERECHO (Comercial):")
print("- Director Comercial y sus 4 gerentes")
print("\nCENTRO:")
print("- Director General")

print(f"\nTotal puestos organizados: {len(positions_coords)}")