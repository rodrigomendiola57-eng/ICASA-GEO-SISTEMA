import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.knowledge_base.models import Category

# Crear categorías básicas
categories = [
    {'name': 'Políticas', 'slug': 'politicas', 'description': 'Políticas organizacionales de ICASA'},
    {'name': 'Procedimientos', 'slug': 'procedimientos', 'description': 'Procedimientos operativos estándar'},
    {'name': 'Manuales', 'slug': 'manuales', 'description': 'Manuales de usuario y guías'},
]

for cat_data in categories:
    category, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )
    if created:
        print(f"✓ Categoría creada: {category.name}")
    else:
        print(f"- Categoría ya existe: {category.name}")

print("¡Categorías creadas exitosamente!")