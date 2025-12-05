from apps.organizational.models import Position

print("=== POSICIONES VISIBLES ===")

# Posiciones centradas en el área visible (0-2000px)
positions_coords = {
    'Director General': (1000, 300),
    
    'Director Administrativo': (600, 600),
    'Director Comercial': (1400, 600),
    
    'Gerente de Normatividad': (200, 900),
    'Gerente de Recursos Humanos': (400, 900),
    'Gerente de Finanzas': (600, 900),
    'Gerente de Nomina': (800, 900),
    
    'Gerente de Operaciones': (1200, 900),
    'Gerente de Porteo': (1400, 900),
    'Gerente de Estaciones': (1600, 900),
    'Gerente de Mantenimiento': (1800, 900)
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

print(f"\nPosiciones en área visible: {len(positions_coords)}")