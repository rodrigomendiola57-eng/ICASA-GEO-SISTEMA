"""
Comando para configurar roles y permisos de ICASA-GEO
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from apps.knowledge_base.models import Category, Document

class Command(BaseCommand):
    help = 'Configura roles y permisos específicos para ICASA-GEO'
    
    def handle(self, *args, **options):
        self.stdout.write('Configurando roles y permisos de ICASA-GEO...')
        
        # Crear grupos de usuarios
        self.create_groups()
        
        # Asignar permisos a grupos
        self.assign_permissions()
        
        # Crear usuarios de ejemplo
        self.create_sample_users()
        
        self.stdout.write(
            self.style.SUCCESS('Roles y permisos configurados exitosamente')
        )
    
    def create_groups(self):
        """Crear grupos de usuarios específicos para ICASA"""
        groups_data = [
            {
                'name': 'Administradores ICASA',
                'description': 'Acceso completo al sistema'
            },
            {
                'name': 'Gerentes',
                'description': 'Pueden aprobar documentos y gestionar categorías'
            },
            {
                'name': 'Editores',
                'description': 'Pueden crear y editar documentos'
            },
            {
                'name': 'Revisores',
                'description': 'Pueden revisar y comentar documentos'
            },
            {
                'name': 'Lectores',
                'description': 'Solo pueden consultar documentos aprobados'
            }
        ]
        
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            if created:
                self.stdout.write(f'✅ Grupo creado: {group.name}')
            else:
                self.stdout.write(f'ℹ️  Grupo ya existe: {group.name}')
    
    def assign_permissions(self):
        """Asignar permisos específicos a cada grupo"""
        
        # Obtener content types
        category_ct = ContentType.objects.get_for_model(Category)
        document_ct = ContentType.objects.get_for_model(Document)
        user_ct = ContentType.objects.get_for_model(User)
        
        # Crear permisos personalizados si no existen
        custom_permissions = [
            ('can_approve_documents', 'Puede aprobar documentos', document_ct),
            ('can_reject_documents', 'Puede rechazar documentos', document_ct),
            ('can_manage_users', 'Puede gestionar usuarios', user_ct),
            ('can_view_analytics', 'Puede ver analytics', document_ct),
        ]
        
        for codename, name, content_type in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            if created:
                self.stdout.write(f'✅ Permiso creado: {name}')
        
        # Configurar permisos por grupo
        permissions_config = {
            'Administradores ICASA': [
                # Todos los permisos
                'add_category', 'change_category', 'delete_category', 'view_category',
                'add_document', 'change_document', 'delete_document', 'view_document',
                'add_user', 'change_user', 'delete_user', 'view_user',
                'can_approve_documents', 'can_reject_documents', 
                'can_manage_users', 'can_view_analytics'
            ],
            'Gerentes': [
                # Gestión completa de contenido
                'add_category', 'change_category', 'view_category',
                'add_document', 'change_document', 'view_document',
                'can_approve_documents', 'can_reject_documents',
                'can_view_analytics'
            ],
            'Editores': [
                # Crear y editar contenido
                'add_category', 'change_category', 'view_category',
                'add_document', 'change_document', 'view_document'
            ],
            'Revisores': [
                # Solo revisar y comentar
                'view_category', 'view_document', 'change_document'
            ],
            'Lectores': [
                # Solo lectura
                'view_category', 'view_document'
            ]
        }
        
        for group_name, permission_codenames in permissions_config.items():
            try:
                group = Group.objects.get(name=group_name)
                
                for codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(f'⚠️  Permiso no encontrado: {codename}')
                
                self.stdout.write(f'✅ Permisos asignados a: {group_name}')
                
            except Group.DoesNotExist:
                self.stdout.write(f'❌ Grupo no encontrado: {group_name}')
    
    def create_sample_users(self):
        """Crear usuarios de ejemplo para cada rol"""
        sample_users = [
            {
                'username': 'director.icasa',
                'email': 'director@icasa.com',
                'first_name': 'Director',
                'last_name': 'General',
                'group': 'Administradores ICASA',
                'is_staff': True
            },
            {
                'username': 'gerente.rh',
                'email': 'gerente.rh@icasa.com',
                'first_name': 'Gerente',
                'last_name': 'Recursos Humanos',
                'group': 'Gerentes'
            },
            {
                'username': 'editor.contenido',
                'email': 'editor@icasa.com',
                'first_name': 'Editor',
                'last_name': 'Contenido',
                'group': 'Editores'
            },
            {
                'username': 'revisor.calidad',
                'email': 'revisor@icasa.com',
                'first_name': 'Revisor',
                'last_name': 'Calidad',
                'group': 'Revisores'
            },
            {
                'username': 'empleado.general',
                'email': 'empleado@icasa.com',
                'first_name': 'Empleado',
                'last_name': 'General',
                'group': 'Lectores'
            }
        ]
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data.get('is_staff', False)
                }
            )
            
            if created:
                # Establecer contraseña por defecto
                user.set_password('icasa2024')
                user.save()
                
                # Asignar al grupo
                try:
                    group = Group.objects.get(name=user_data['group'])
                    user.groups.add(group)
                    self.stdout.write(f'✅ Usuario creado: {user.username} ({user_data["group"]})')
                except Group.DoesNotExist:
                    self.stdout.write(f'❌ Grupo no encontrado: {user_data["group"]}')
            else:
                self.stdout.write(f'ℹ️  Usuario ya existe: {user.username}')
        
        self.stdout.write('\n📋 CREDENCIALES DE USUARIOS:')
        self.stdout.write('Contraseña para todos: icasa2024')
        for user_data in sample_users:
            self.stdout.write(f'  • {user_data["username"]} - {user_data["group"]}')