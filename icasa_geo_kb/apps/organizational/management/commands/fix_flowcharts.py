from django.core.management.base import BaseCommand
from django.db import transaction
from apps.organizational.models import FlowchartProcess, ProcessCategory, FlowchartTemplate
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Arregla problemas comunes en los flujogramas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-orphaned',
            action='store_true',
            help='Elimina procesos huérfanos sin categoría o propietario',
        )
        parser.add_argument(
            '--fix-categories',
            action='store_true',
            help='Crea categorías faltantes',
        )
        parser.add_argument(
            '--reset-all',
            action='store_true',
            help='Elimina TODOS los flujogramas (usar con precaución)',
        )
        parser.add_argument(
            '--force-delete',
            action='store_true',
            help='Fuerza la eliminación de procesos problemáticos',
        )

    def handle(self, *args, **options):
        if options['reset_all']:
            if input("¿Estás seguro de que quieres eliminar TODOS los flujogramas? (escriba 'SI' para confirmar): ") == 'SI':
                with transaction.atomic():
                    count = FlowchartProcess.objects.count()
                    FlowchartProcess.objects.all().delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'Se eliminaron {count} flujogramas exitosamente')
                    )
            else:
                self.stdout.write(self.style.WARNING('Operación cancelada'))
            return

        if options['fix_categories']:
            self.fix_categories()

        if options['clean_orphaned']:
            self.clean_orphaned_processes()

        self.stdout.write(self.style.SUCCESS('Proceso de reparación completado'))

    def fix_categories(self):
        """Crea categorías faltantes y elimina duplicados"""
        categories = [
            ('operational', 'Procesos Operativos', '#059669'),
            ('strategic', 'Procesos Estratégicos', '#1e40af'),
            ('support', 'Procesos de Soporte', '#7c3aed'),
            ('audit', 'Procesos de Auditoría', '#dc2626'),
            ('quality', 'Procesos de Calidad', '#ea580c'),
            ('safety', 'Procesos de Seguridad', '#ca8a04'),
            ('finance', 'Procesos Financieros', '#16a34a'),
            ('hr', 'Procesos de RRHH', '#0891b2'),
            ('it', 'Procesos de TI', '#4338ca'),
            ('legal', 'Procesos Legales', '#be123c'),
        ]

        created_count = 0
        fixed_count = 0
        
        for category_type, name, color in categories:
            # Buscar duplicados
            existing_categories = ProcessCategory.objects.filter(category_type=category_type)
            
            if existing_categories.count() > 1:
                # Hay duplicados, mantener el primero y eliminar el resto
                main_category = existing_categories.first()
                duplicates = existing_categories.exclude(id=main_category.id)
                
                # Reasignar procesos de los duplicados al principal
                for duplicate in duplicates:
                    FlowchartProcess.objects.filter(category=duplicate).update(category=main_category)
                    duplicate.delete()
                    fixed_count += 1
                    self.stdout.write(f'Eliminado duplicado: {duplicate.name}')
                
                # Actualizar el principal con los datos correctos
                main_category.name = name
                main_category.color = color
                main_category.description = f'Categoría para {name.lower()}'
                main_category.icon = 'fas fa-sitemap'
                main_category.save()
                
            elif existing_categories.count() == 1:
                # Existe una, actualizarla
                category = existing_categories.first()
                category.name = name
                category.color = color
                category.description = f'Categoría para {name.lower()}'
                category.icon = 'fas fa-sitemap'
                category.save()
                
            else:
                # No existe, crearla
                ProcessCategory.objects.create(
                    category_type=category_type,
                    name=name,
                    description=f'Categoría para {name.lower()}',
                    color=color,
                    icon='fas fa-sitemap'
                )
                created_count += 1
                self.stdout.write(f'Creada categoría: {name}')

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {created_count} categorías y se eliminaron {fixed_count} duplicados')
        )

    def clean_orphaned_processes(self):
        """Limpia procesos huérfanos"""
        # Procesos sin categoría
        orphaned_no_category = FlowchartProcess.objects.filter(category__isnull=True)
        count_no_category = orphaned_no_category.count()
        
        if count_no_category > 0:
            # Asignar categoría por defecto
            default_category = ProcessCategory.objects.filter(category_type='operational').first()
            if not default_category:
                default_category = ProcessCategory.objects.create(
                    category_type='operational',
                    name='Procesos Operativos',
                    description='Categoría por defecto para procesos operativos',
                    color='#059669',
                    icon='fas fa-sitemap'
                )
            orphaned_no_category.update(category=default_category)
            self.stdout.write(f'Se asignó categoría por defecto a {count_no_category} procesos')

        # Procesos sin propietario
        orphaned_no_owner = FlowchartProcess.objects.filter(owner__isnull=True)
        count_no_owner = orphaned_no_owner.count()
        
        if count_no_owner > 0:
            # Buscar un superusuario para asignar
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                orphaned_no_owner.update(owner=admin_user)
                self.stdout.write(f'Se asignó propietario por defecto a {count_no_owner} procesos')
            else:
                self.stdout.write(
                    self.style.WARNING(f'No se pudo asignar propietario a {count_no_owner} procesos (no hay superusuarios)')
                )

        # Procesos con datos corruptos
        corrupted_processes = []
        for process in FlowchartProcess.objects.all():
            try:
                # Verificar que diagram_data sea válido
                if process.diagram_data is None:
                    process.diagram_data = {}
                    process.save()
                    corrupted_processes.append(process.id)
                elif not isinstance(process.diagram_data, dict):
                    process.diagram_data = {}
                    process.save()
                    corrupted_processes.append(process.id)
            except Exception as e:
                self.stdout.write(f'Error en proceso {process.id}: {e}')
                # Intentar reparar el proceso
                try:
                    process.diagram_data = {}
                    process.save()
                    corrupted_processes.append(process.id)
                except:
                    # Si no se puede reparar, eliminarlo
                    self.stdout.write(f'Eliminando proceso corrupto {process.id}')
                    process.delete()

        if corrupted_processes:
            self.stdout.write(f'Se repararon {len(corrupted_processes)} procesos con datos corruptos')

        self.stdout.write(
            self.style.SUCCESS('Limpieza de procesos huérfanos completada')
        )