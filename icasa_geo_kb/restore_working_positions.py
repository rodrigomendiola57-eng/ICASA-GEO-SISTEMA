from apps.organizational.models import Position

print("=== RESTAURANDO POSICIONES QUE FUNCIONABAN ===")

# Posiciones originales que funcionaban bien
positions_coords = {
    'Director General': (1000, 200),
    
    'Director Administrativo': (500, 500),
    'Director Comercial': (1500, 500),
    
    'Gerente de Normatividad': (100, 800),
    'Gerente de Recursos Humanos': (300, 800),
    'Gerente de Finanzas': (500, 800),
    'Gerente de Nomina': (700, 800),
    
    'Gerente de Operaciones': (1300, 800),
    'Gerente de Porteo': (1500, 800),
    'Gerente de Estaciones': (1700, 800),
    'Gerente de Mantenimiento': (1900, 800)
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

print("\nPosiciones restauradas. El organigrama debería funcionar correctamente.")