from apps.organizational.models import Position

print("=== ARREGLANDO LAYOUT FINAL ===")

# Layout correcto: gerencias separadas por rama
positions_coords = {
    # Nivel 1 - Centro
    'Director General': (1000, 200),
    
    # Nivel 2 - Separados
    'Director Administrativo': (500, 500),   # Izquierda
    'Director Comercial': (1500, 500),      # Derecha
    
    # SOLO gerencias administrativas bajo Director Administrativo (izquierda)
    'Gerente de Normatividad': (100, 800),
    'Gerente de Recursos Humanos': (300, 800),
    'Gerente de Finanzas': (500, 800),
    'Gerente de Nomina': (700, 800),
    
    # SOLO gerencias comerciales bajo Director Comercial (derecha)
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
        print(f"✗ {title} no encontrado")

print("\n=== LAYOUT ORGANIZADO ===")
print("IZQUIERDA (Administrativo):")
print("- Dir. Administrativo (500)")
print("- Sus 4 gerentes (100-700)")
print("\nDERECHA (Comercial):")
print("- Dir. Comercial (1500)")
print("- Sus 4 gerentes (1300-1900)")
print("\nCENTRO:")
print("- Director General (1000)")

print(f"\nPosiciones actualizadas: 11")