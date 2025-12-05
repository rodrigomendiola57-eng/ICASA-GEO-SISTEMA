import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.development')
django.setup()

from apps.organizational.models import Position

def fix_gerencias_spacing():
    """Espaciar mejor las gerencias para evitar amontonamiento"""
    
    # Obtener todas las posiciones por nivel
    nivel_1 = Position.objects.filter(level=1).first()  # Director General
    nivel_2 = Position.objects.filter(level=2).order_by('title')  # Gerencias
    nivel_3 = Position.objects.filter(level=3).order_by('title')  # Jefaturas
    
    print("=== ESPACIADO MEJORADO DE GERENCIAS ===")
    
    # NIVEL 1: Director General (centrado)
    if nivel_1:
        nivel_1.x_position = 1000
        nivel_1.y_position = 150
        nivel_1.save()
        print(f"✓ {nivel_1.title}: x=1000, y=150")
    
    # NIVEL 2: Gerencias (más espaciadas horizontalmente)
    gerencias_x_positions = [200, 500, 800, 1100, 1400, 1700, 2000, 2300]  # 8 posiciones con 300px de separación
    
    for i, gerencia in enumerate(nivel_2):
        if i < len(gerencias_x_positions):
            gerencia.x_position = gerencias_x_positions[i]
            gerencia.y_position = 400  # Mismo Y para todas las gerencias
            gerencia.save()
            print(f"✓ {gerencia.title}: x={gerencias_x_positions[i]}, y=400")
    
    # NIVEL 3: Jefaturas (distribuidas bajo sus gerencias)
    jefaturas_x_positions = [150, 450, 750, 1050, 1350, 1650, 1950, 2250, 2550]  # Intercaladas
    
    for i, jefatura in enumerate(nivel_3):
        if i < len(jefaturas_x_positions):
            jefatura.x_position = jefaturas_x_positions[i]
            jefatura.y_position = 650  # Mismo Y para todas las jefaturas
            jefatura.save()
            print(f"✓ {jefatura.title}: x={jefaturas_x_positions[i]}, y=650")
    
    print(f"\n✅ Espaciado completado:")
    print(f"   - Nivel 1: 1 posición centrada")
    print(f"   - Nivel 2: {nivel_2.count()} gerencias con 300px de separación")
    print(f"   - Nivel 3: {nivel_3.count()} jefaturas intercaladas")
    print(f"   - Canvas recomendado: 2800px de ancho")

if __name__ == "__main__":
    fix_gerencias_spacing()