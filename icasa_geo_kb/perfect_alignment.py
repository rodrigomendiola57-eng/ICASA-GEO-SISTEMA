from apps.organizational.models import Position

print("=== ALINEACION PERFECTA POR JERARQUIA ===")

# Posiciones perfectamente alineadas por nivel jerárquico
positions_coords = {
    # Nivel 1 - Centro exacto
    'Director General': (1000, 150),
    
    # Nivel 2 - Misma altura, equidistantes del centro
    'Director Administrativo': (600, 400),
    'Director Comercial': (1400, 400),
    
    # Nivel 3 - Misma altura exacta, espaciado uniforme
    # Gerencias administrativas (izquierda)
    'Gerente de Normatividad': (200, 650),
    'Gerente de Recursos Humanos': (400, 650),
    'Gerente de Finanzas': (600, 650),
    'Gerente de Nomina': (800, 650),
    
    # Gerencias comerciales (derecha)  
    'Gerente de Operaciones': (1200, 650),
    'Gerente de Porteo': (1400, 650),
    'Gerente de Estaciones': (1600, 650),
    'Gerente de Mantenimiento': (1800, 650)
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

print("\n=== ALINEACION COMPLETADA ===")
print("Nivel 1: y=150 (Director General)")
print("Nivel 2: y=400 (Directores)")  
print("Nivel 3: y=650 (Gerentes)")
print("Espaciado horizontal: 200px entre gerencias")
print("Líneas más cortas: 250px verticales entre niveles")