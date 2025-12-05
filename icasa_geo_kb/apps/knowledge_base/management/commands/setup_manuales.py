from django.core.management.base import BaseCommand
from apps.knowledge_base.models import Category

class Command(BaseCommand):
    help = 'Configura las subcategorías de Manuales'

    def handle(self, *args, **options):
        # Buscar la categoría padre "Manuales"
        try:
            manuales_parent = Category.objects.get(slug='manuales')
            self.stdout.write(f'Encontrada categoría padre: {manuales_parent.name}')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('No se encontró la categoría "Manuales"'))
            return

        # Subcategorías a crear
        subcategories = [
            {
                'name': 'Operativos',
                'slug': 'manuales-operativos',
                'description': 'Manuales de procesos core del negocio de seguros',
                'icon': 'fas fa-cogs',
                'color': '#10b981'
            },
            {
                'name': 'Gestión y Control',
                'slug': 'manuales-gestion-control',
                'description': 'Manuales de calidad, riesgos y cumplimiento',
                'icon': 'fas fa-shield-alt',
                'color': '#f59e0b'
            },
            {
                'name': 'Recursos Humanos',
                'slug': 'manuales-recursos-humanos',
                'description': 'Manuales de gestión del talento humano',
                'icon': 'fas fa-users',
                'color': '#3b82f6'
            },
            {
                'name': 'Tecnología',
                'slug': 'manuales-tecnologia',
                'description': 'Manuales de sistemas y seguridad informática',
                'icon': 'fas fa-laptop-code',
                'color': '#8b5cf6'
            }
        ]

        created_count = 0
        for subcat_data in subcategories:
            subcat, created = Category.objects.get_or_create(
                slug=subcat_data['slug'],
                parent=manuales_parent,
                defaults={
                    'name': subcat_data['name'],
                    'description': subcat_data['description'],
                    'icon': subcat_data['icon'],
                    'color': subcat_data['color'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Creada subcategoría: {subcat.name}')
                created_count += 1
            else:
                self.stdout.write(f'Ya existe: {subcat.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Proceso completado. {created_count} subcategorías creadas.')
        )