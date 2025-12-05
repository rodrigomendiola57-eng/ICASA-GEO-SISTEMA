from apps.organizational.models import Position

print("=== REORGANIZANDO JERARQUIA VISUAL ===")

# Layout jerárquico con mucho más espacio
positions_coords = {
    # Nivel 1 - Director General (Centro superior)
    'Director General': (2000, 200),
    
    # Nivel 2 - Directores (Muy separados horizontalmente)
    'Director Administrativo': (800, 800),    # Izquierda
    'Director Comercial': (3200, 800),       # Derecha
    
    # Nivel 3 - Gerencias Administrativas (Columna izquierda)
    'Gerente de Normatividad': (200, 1400),
    'Gerente de Recursos Humanos': (600, 1400),
    'Gerente de Finanzas': (1000, 1400),
    'Gerente de Nomina': (1400, 1400),
    
    # Nivel 3 - Gerencias Comerciales (Columna derecha)
    'Gerente de Operaciones': (2600, 1400),
    'Gerente de Porteo': (3000, 1400),
    'Gerente de Estaciones': (3400, 1400),
    'Gerente de Mantenimiento': (3800, 1400)
}

# Actualizar todas las posiciones
updated = 0
for title, (x, y) in positions_coords.items():
    try:
        position = Position.objects.get(title=title)
        position.x_position = x
        position.y_position = y
        position.save()
        print(f"✓ {title}: ({x}, {y})")
        updated += 1
    except Position.DoesNotExist:
        print(f"✗ No encontrado: {title}")

print(f"\n=== LAYOUT JERARQUICO APLICADO ===")
print("Estructura visual:")
print("                    Director General")
print("                         (2000)")
print("                           |")
print("        ___________________|___________________")
print("       |                                     |")
print("Dir. Administrativo                   Dir. Comercial")
print("      (800)                              (3200)")
print("       |                                     |")
print("   ____|____                           ______|______")
print("  |  |  |  |                         |  |  |  |  |")
print(" Nor RH Fin Nom                    Oper Por Est Man")
print("200 600 1K 1.4K                   2.6K 3K 3.4K 3.8K")

print(f"\nPosiciones actualizadas: {updated}/{len(positions_coords)}")