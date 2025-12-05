from apps.organizational.models import Position

def fix_gerencias_by_sides():
    """Organizar gerencias: administrativas a la izquierda, comerciales a la derecha"""
    
    # Gerencias administrativas (bajo Director Administrativo)
    admin_gerencias = [
        'Gerente de Recursos Humanos',
        'Gerente de Finanzas', 
        'Gerente de Nomina',
        'Gerente de Normatividad'
    ]
    
    # Gerencias comerciales (bajo Director Comercial)
    comercial_gerencias = [
        'Gerente de Operaciones',
        'Gerente de Porteo',
        'Gerente de Estaciones', 
        'Gerente de Mantenimiento'
    ]
    
    print("=== ORGANIZANDO GERENCIAS POR LADOS ===")
    
    # LADO IZQUIERDO: Gerencias Administrativas
    admin_positions = [500, 700, 900, 1100]  # Posiciones X para lado izquierdo
    
    for i, gerencia_name in enumerate(admin_gerencias):
        gerencia = Position.objects.filter(title__icontains=gerencia_name.replace('Gerente de ', '')).first()
        if gerencia and i < len(admin_positions):
            gerencia.x_position = admin_positions[i]
            gerencia.y_position = 650
            gerencia.save()
            print(f"✓ {gerencia.title}: x={admin_positions[i]}, y=650 (IZQUIERDA)")
    
    # LADO DERECHO: Gerencias Comerciales  
    comercial_positions = [1700, 1900, 2100, 2300]  # Posiciones X para lado derecho
    
    for i, gerencia_name in enumerate(comercial_gerencias):
        gerencia = Position.objects.filter(title__icontains=gerencia_name.replace('Gerente de ', '')).first()
        if gerencia and i < len(comercial_positions):
            gerencia.x_position = comercial_positions[i]
            gerencia.y_position = 650
            gerencia.save()
            print(f"✓ {gerencia.title}: x={comercial_positions[i]}, y=650 (DERECHA)")
    
    print(f"\n✅ Gerencias organizadas por lados:")
    print(f"   - IZQUIERDA: Administrativas (500-1100)")
    print(f"   - DERECHA: Comerciales (1700-2300)")

fix_gerencias_by_sides()