from apps.organizational.models import Position

def fix_wider_spacing():
    """Espaciado más amplio para evitar amontonamiento"""
    
    print("=== ESPACIADO MÁS AMPLIO ===")
    
    # Director General (centrado)
    director_general = Position.objects.filter(level=1).first()
    if director_general:
        director_general.x_position = 1400
        director_general.y_position = 150
        director_general.save()
        print(f"✓ {director_general.title}: x=1400, y=150")
    
    # Directores (más separados)
    director_admin = Position.objects.filter(title__icontains='Administrativo').first()
    director_comercial = Position.objects.filter(title__icontains='Comercial').first()
    
    if director_admin:
        director_admin.x_position = 700   # Más alejado del centro
        director_admin.y_position = 400
        director_admin.save()
        print(f"✓ {director_admin.title}: x=700, y=400")
    
    if director_comercial:
        director_comercial.x_position = 2100  # Más alejado del centro
        director_comercial.y_position = 400
        director_comercial.save()
        print(f"✓ {director_comercial.title}: x=2100, y=400")
    
    # Gerencias administrativas (más espaciadas)
    admin_gerencias = ['Recursos Humanos', 'Finanzas', 'Nomina', 'Normatividad']
    admin_positions = [300, 600, 900, 1200]  # Más espaciado
    
    for i, gerencia_name in enumerate(admin_gerencias):
        gerencia = Position.objects.filter(title__icontains=gerencia_name).first()
        if gerencia and i < len(admin_positions):
            gerencia.x_position = admin_positions[i]
            gerencia.y_position = 650
            gerencia.save()
            print(f"✓ {gerencia.title}: x={admin_positions[i]}, y=650")
    
    # Gerencias comerciales (más espaciadas)
    comercial_gerencias = ['Operaciones', 'Porteo', 'Estaciones', 'Mantenimiento']
    comercial_positions = [1600, 1900, 2200, 2500]  # Más espaciado
    
    for i, gerencia_name in enumerate(comercial_gerencias):
        gerencia = Position.objects.filter(title__icontains=gerencia_name).first()
        if gerencia and i < len(comercial_positions):
            gerencia.x_position = comercial_positions[i]
            gerencia.y_position = 650
            gerencia.save()
            print(f"✓ {gerencia.title}: x={comercial_positions[i]}, y=650")
    
    print(f"\n✅ Espaciado ampliado:")
    print(f"   - Canvas: 3000px de ancho")
    print(f"   - Separación entre gerencias: 300px")
    print(f"   - Sin amontonamiento")

fix_wider_spacing()