from apps.organizational.models import Position

def fix_directores():
    """Corregir posición de los directores para que se vean bien"""
    
    # Obtener directores específicamente
    director_admin = Position.objects.filter(title__icontains='Administrativo').first()
    director_comercial = Position.objects.filter(title__icontains='Comercial').first()
    
    print("=== CORRIGIENDO DIRECTORES ===")
    
    if director_admin:
        director_admin.x_position = 800   # Más cerca del centro
        director_admin.y_position = 400
        director_admin.save()
        print(f"✓ {director_admin.title}: x=800, y=400")
    
    if director_comercial:
        director_comercial.x_position = 2000  # Más cerca del centro
        director_comercial.y_position = 400
        director_comercial.save()
        print(f"✓ {director_comercial.title}: x=2000, y=400")
    
    print("✅ Directores corregidos")

fix_directores()