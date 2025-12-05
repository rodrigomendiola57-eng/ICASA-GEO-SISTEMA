from apps.organizational.models import Position

print("=== MEJORANDO ESPACIADO ===")

# Posiciones con mejor espaciado
positions_coords = {
    'Director General': (1000, 200),
    
    'Director Administrativo': (500, 500),
    'Director Comercial': (1500, 500),
    
    # Gerencias administrativas con más espacio
    'Gerente de Normatividad': (50, 850),
    'Gerente de Recursos Humanos': (350, 850),
    'Gerente de Finanzas': (650, 850),
    'Gerente de Nomina': (950, 850),
    
    # Gerencias comerciales con más espacio
    'Gerente de Operaciones': (1050, 850),
    'Gerente de Porteo': (1350, 850),
    'Gerente de Estaciones': (1650, 850),
    'Gerente de Mantenimiento': (1950, 850)
}

for title, (x, y) in positions_coords.items():
    try:
        position = Position.objects.get(title=title)
        position.x_position = x
        position.y_position = y
        position.save()
        print(f"✓ {title}: ({x}, {y})")
    except Position.DoesNotExist:
        print(f"✗ {title}")

print("\nEspaciado mejorado: 300px entre gerencias")