"""
Script de configuración inicial para ICASA-GEO
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_initial_data():
    """Configurar datos iniciales del sistema"""
    
    # Crear grupos de usuarios
    groups_data = [
        {
            'name': 'Administradores',
            'permissions': ['add', 'change', 'delete', 'view']
        },
        {
            'name': 'Editores',
            'permissions': ['add', 'change', 'view']
        },
        {
            'name': 'Revisores',
            'permissions': ['change', 'view']
        },
        {
            'name': 'Lectores',
            'permissions': ['view']
        }
    ]
    
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(name=group_data['name'])
        if created:
            print(f"Grupo '{group.name}' creado exitosamente")
        else:
            print(f"Grupo '{group.name}' ya existe")

def main():
    """Función principal de configuración"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.development')
    
    try:
        django.setup()
        
        print("=== CONFIGURACIÓN INICIAL DE ICASA-GEO ===")
        print("1. Creando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("2. Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("3. Configurando datos iniciales...")
        setup_initial_data()
        
        print("4. Recopilando archivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("\n=== CONFIGURACIÓN COMPLETADA ===")
        print("Para crear un superusuario, ejecuta:")
        print("python manage.py createsuperuser")
        print("\nPara iniciar el servidor de desarrollo:")
        print("python manage.py runserver")
        
    except Exception as e:
        print(f"Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()