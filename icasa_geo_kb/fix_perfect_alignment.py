from apps.organizational.models import Position

def fix_perfect_alignment():
    """Alineación perfecta con Director General centrado y directores simétricos"""
    
    # Obtener posiciones por nivel
    director_general = Position.objects.filter(level=1).first()
    directores = Position.objects.filter(level=2).order_by('title')
    gerentes = Position.objects.filter(level=3).order_by('title')
    
    print("=== ALINEACIÓN PERFECTA ===")
    
    # NIVEL 1: Director General (centrado en canvas de 2800px)
    if director_general:
        director_general.x_position = 1400  # Centro perfecto
        director_general.y_position = 150
        director_general.save()
        print(f"✓ {director_general.title}: x=1400, y=150 (CENTRADO)")
    
    # NIVEL 2: Directores (simétricos al Director General)
    if directores.count() == 2:
        # Director Administrativo a la izquierda, Comercial a la derecha
        directores[0].x_position = 900   # 500px a la izquierda del centro
        directores[0].y_position = 400
        directores[0].save()
        print(f"✓ {directores[0].title}: x=900, y=400")
        
        directores[1].x_position = 1900  # 500px a la derecha del centro
        directores[1].y_position = 400
        directores[1].save()
        print(f"✓ {directores[1].title}: x=1900, y=400")
    
    # NIVEL 3: Gerentes (distribuidos uniformemente)
    gerentes_positions = [300, 600, 900, 1200, 1500, 1800, 2100, 2400]
    
    for i, gerente in enumerate(gerentes):
        if i < len(gerentes_positions):
            gerente.x_position = gerentes_positions[i]
            gerente.y_position = 650
            gerente.save()
            print(f"✓ {gerente.title}: x={gerentes_positions[i]}, y=650")
    
    print(f"\n✅ Alineación perfecta completada:")
    print(f"   - Canvas: 2800px de ancho")
    print(f"   - Director General: CENTRADO")
    print(f"   - Directores: SIMÉTRICOS")
    print(f"   - Gerentes: DISTRIBUIDOS UNIFORMEMENTE")

fix_perfect_alignment()