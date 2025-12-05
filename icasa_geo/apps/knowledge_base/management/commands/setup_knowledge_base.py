"""
Comando para configurar datos iniciales del Knowledge Base
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.knowledge_base.models import Category, DocumentTemplate

class Command(BaseCommand):
    help = 'Configura datos iniciales para Knowledge Base'
    
    def handle(self, *args, **options):
        self.stdout.write('Configurando Knowledge Base...')
        
        # Crear categorías iniciales
        self.create_initial_categories()
        
        # Crear templates iniciales
        self.create_initial_templates()
        
        self.stdout.write(
            self.style.SUCCESS('Knowledge Base configurado exitosamente')
        )
    
    def create_initial_categories(self):
        """Crear estructura inicial de categorías"""
        categories_data = [
            {
                'name': 'Manual de Organización',
                'description': 'Documentos del manual organizacional',
                'icon': 'fas fa-building',
                'color': '#007bff',
                'children': [
                    {'name': 'Misión y Visión', 'icon': 'fas fa-eye'},
                    {'name': 'Base Legal', 'icon': 'fas fa-gavel'},
                    {'name': 'Estructura Organizacional', 'icon': 'fas fa-sitemap'},
                ]
            },
            {
                'name': 'Políticas',
                'description': 'Políticas organizacionales',
                'icon': 'fas fa-clipboard-list',
                'color': '#28a745',
                'children': [
                    {'name': 'Recursos Humanos', 'icon': 'fas fa-users'},
                    {'name': 'Tecnología', 'icon': 'fas fa-laptop'},
                    {'name': 'Seguridad', 'icon': 'fas fa-shield-alt'},
                ]
            },
            {
                'name': 'Procedimientos',
                'description': 'Procedimientos operativos',
                'icon': 'fas fa-cogs',
                'color': '#ffc107',
                'children': [
                    {'name': 'Administrativos', 'icon': 'fas fa-file-alt'},
                    {'name': 'Operativos', 'icon': 'fas fa-tasks'},
                    {'name': 'Técnicos', 'icon': 'fas fa-wrench'},
                ]
            }
        ]
        
        for cat_data in categories_data:
            parent, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            
            if created:
                self.stdout.write(f'Categoría creada: {parent.name}')
            
            # Crear subcategorías
            for child_data in cat_data.get('children', []):
                child, created = Category.objects.get_or_create(
                    name=child_data['name'],
                    parent=parent,
                    defaults={
                        'icon': child_data['icon']
                    }
                )
                
                if created:
                    self.stdout.write(f'  Subcategoría creada: {child.name}')
    
    def create_initial_templates(self):
        """Crear templates iniciales"""
        templates_data = [
            {
                'name': 'Política Estándar',
                'template_type': 'policy',
                'content': '''
                <h1>{{document_code}} - {{document_title}}</h1>
                
                <h2>1. Objetivo</h2>
                <p>[Describir el objetivo de la política]</p>
                
                <h2>2. Alcance</h2>
                <p>[Definir el alcance de aplicación]</p>
                
                <h2>3. Responsabilidades</h2>
                <p>[Definir responsabilidades por rol]</p>
                
                <h2>4. Política</h2>
                <p>[Contenido principal de la política]</p>
                
                <h2>5. Procedimientos Relacionados</h2>
                <p>[Referencias a procedimientos]</p>
                
                <hr>
                <p><strong>Fecha de vigencia:</strong> {{effective_date}}</p>
                <p><strong>Versión:</strong> {{version}}</p>
                <p><strong>Empresa:</strong> {{company_name}}</p>
                ''',
                'variables': {
                    'document_code': 'Código del documento',
                    'document_title': 'Título del documento',
                    'effective_date': 'Fecha de vigencia',
                    'version': 'Versión del documento',
                    'company_name': 'Nombre de la empresa'
                }
            },
            {
                'name': 'Procedimiento Estándar',
                'template_type': 'procedure',
                'content': '''
                <h1>{{document_code}} - {{document_title}}</h1>
                
                <h2>1. Propósito</h2>
                <p>[Describir el propósito del procedimiento]</p>
                
                <h2>2. Alcance</h2>
                <p>[Definir el alcance del procedimiento]</p>
                
                <h2>3. Responsables</h2>
                <p>[Definir roles y responsabilidades]</p>
                
                <h2>4. Procedimiento</h2>
                <ol>
                    <li>[Paso 1]</li>
                    <li>[Paso 2]</li>
                    <li>[Paso 3]</li>
                </ol>
                
                <h2>5. Documentos de Referencia</h2>
                <p>[Documentos relacionados]</p>
                
                <h2>6. Registros</h2>
                <p>[Registros generados]</p>
                
                <hr>
                <p><strong>Fecha de vigencia:</strong> {{effective_date}}</p>
                <p><strong>Versión:</strong> {{version}}</p>
                <p><strong>Empresa:</strong> {{company_name}}</p>
                ''',
                'variables': {
                    'document_code': 'Código del documento',
                    'document_title': 'Título del documento',
                    'effective_date': 'Fecha de vigencia',
                    'version': 'Versión del documento',
                    'company_name': 'Nombre de la empresa'
                }
            }
        ]
        
        for template_data in templates_data:
            template, created = DocumentTemplate.objects.get_or_create(
                name=template_data['name'],
                template_type=template_data['template_type'],
                defaults={
                    'content': template_data['content'],
                    'variables': template_data['variables']
                }
            )
            
            if created:
                self.stdout.write(f'Template creado: {template.name}')