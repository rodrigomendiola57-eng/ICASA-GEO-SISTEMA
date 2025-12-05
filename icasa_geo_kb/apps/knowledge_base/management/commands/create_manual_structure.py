from django.core.management.base import BaseCommand
from apps.knowledge_base.models import Category, Document
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea la estructura inicial del Manual de Organización ICASA'

    def handle(self, *args, **options):
        self.stdout.write('Creando estructura del Manual de Organizacion ICASA...')
        
        # Crear categorías principales
        categories_data = [
            {
                'name': 'Información Corporativa',
                'description': 'Misión, visión, valores y historia de ICASA',
                'icon': 'fas fa-building',
                'color': '#4CAF50',
                'subcategories': [
                    'Misión y Visión',
                    'Historia de la Empresa', 
                    'Valores Corporativos',
                    'Política de Calidad'
                ]
            },
            {
                'name': 'Marco Legal',
                'description': 'Constitución, normativas y certificaciones',
                'icon': 'fas fa-gavel',
                'color': '#2196F3',
                'subcategories': [
                    'Constitución de la Empresa',
                    'Normativas Aplicables',
                    'Certificaciones ISO',
                    'Reglamentos Internos'
                ]
            },
            {
                'name': 'Objetivos Estratégicos',
                'description': 'Metas y objetivos por departamento',
                'icon': 'fas fa-bullseye',
                'color': '#FF9800',
                'subcategories': [
                    'Objetivos Corporativos',
                    'Metas por Departamento',
                    'KPIs Organizacionales',
                    'Planes de Acción'
                ]
            },
            {
                'name': 'Políticas y Procedimientos',
                'description': 'Procedimientos operativos y políticas internas',
                'icon': 'fas fa-clipboard-list',
                'color': '#9C27B0',
                'subcategories': [
                    'Recursos Humanos',
                    'Operaciones',
                    'Finanzas y Contabilidad',
                    'Calidad y Mejora Continua'
                ]
            },
            {
                'name': 'Manuales Operativos',
                'description': 'Guías técnicas y manuales de usuario',
                'icon': 'fas fa-tools',
                'color': '#607D8B',
                'subcategories': [
                    'Manual de Usuario',
                    'Procedimientos Técnicos',
                    'Guías de Trabajo',
                    'Protocolos de Seguridad'
                ]
            }
        ]
        
        created_categories = 0
        created_subcategories = 0
        
        for cat_data in categories_data:
            # Crear categoría principal
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'is_active': True
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(f'  [OK] Categoria creada: {category.name}')
            
            # Crear subcategorías
            for subcat_name in cat_data['subcategories']:
                subcategory, sub_created = Category.objects.get_or_create(
                    name=subcat_name,
                    parent=category,
                    defaults={
                        'description': f'Documentos relacionados con {subcat_name.lower()}',
                        'icon': 'fas fa-folder',
                        'color': cat_data['color'],
                        'is_active': True
                    }
                )
                
                if sub_created:
                    created_subcategories += 1
                    self.stdout.write(f'    [+] Subcategoria creada: {subcategory.name}')
        
        # Crear algunos documentos de ejemplo
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
            
            if admin_user:
                sample_docs = [
                    {
                        'title': 'Misión y Visión Corporativa ICASA',
                        'category': 'Misión y Visión',
                        'content': '''
                        <h2>Misión</h2>
                        <p>Proporcionar soluciones integrales de alta calidad que superen las expectativas de nuestros clientes, 
                        contribuyendo al desarrollo sostenible de Guatemala.</p>
                        
                        <h2>Visión</h2>
                        <p>Ser la empresa líder en nuestro sector, reconocida por la excelencia en el servicio, 
                        la innovación constante y el compromiso con la responsabilidad social.</p>
                        
                        <h2>Valores</h2>
                        <ul>
                            <li><strong>Integridad:</strong> Actuamos con honestidad y transparencia</li>
                            <li><strong>Calidad:</strong> Buscamos la excelencia en todo lo que hacemos</li>
                            <li><strong>Innovación:</strong> Mejoramos continuamente nuestros procesos</li>
                            <li><strong>Compromiso:</strong> Cumplimos nuestras promesas</li>
                        </ul>
                        ''',
                        'summary': 'Documento oficial que establece la misión, visión y valores corporativos de ICASA.'
                    },
                    {
                        'title': 'Política de Calidad ISO 9001',
                        'category': 'Política de Calidad',
                        'content': '''
                        <h2>Política de Calidad</h2>
                        <p>ICASA se compromete a:</p>
                        <ul>
                            <li>Satisfacer los requisitos del cliente y las partes interesadas</li>
                            <li>Cumplir con los requisitos legales y reglamentarios aplicables</li>
                            <li>Mejorar continuamente la eficacia del sistema de gestión de calidad</li>
                            <li>Proporcionar los recursos necesarios para el logro de los objetivos</li>
                        </ul>
                        
                        <h3>Objetivos de Calidad</h3>
                        <ol>
                            <li>Mantener un índice de satisfacción del cliente superior al 95%</li>
                            <li>Reducir los tiempos de entrega en un 10% anual</li>
                            <li>Implementar al menos 2 mejoras de proceso por trimestre</li>
                        </ol>
                        ''',
                        'summary': 'Política de calidad alineada con los estándares ISO 9001:2015.'
                    }
                ]
                
                created_docs = 0
                for doc_data in sample_docs:
                    try:
                        category = Category.objects.get(name=doc_data['category'])
                        doc, doc_created = Document.objects.get_or_create(
                            title=doc_data['title'],
                            defaults={
                                'category': category,
                                'content': doc_data['content'],
                                'summary': doc_data['summary'],
                                'created_by': admin_user,
                                'status': 'approved',
                                'is_public': True
                            }
                        )
                        
                        if doc_created:
                            created_docs += 1
                            self.stdout.write(f'  [DOC] Documento creado: {doc.title}')
                    
                    except Category.DoesNotExist:
                        self.stdout.write(f'  [WARN] Categoria no encontrada: {doc_data["category"]}')
                
                self.stdout.write(f'\nResumen:')
                self.stdout.write(f'  • {created_categories} categorías principales creadas')
                self.stdout.write(f'  • {created_subcategories} subcategorías creadas')
                self.stdout.write(f'  • {created_docs} documentos de ejemplo creados')
            
            else:
                self.stdout.write('[WARN] No se encontro usuario administrador para crear documentos')
        
        except Exception as e:
            self.stdout.write(f'[ERROR] Error al crear documentos: {str(e)}')
        
        self.stdout.write('\n[SUCCESS] Estructura del Manual de Organizacion creada exitosamente!')
        self.stdout.write('[INFO] Accede a /manual/ para ver el resultado')