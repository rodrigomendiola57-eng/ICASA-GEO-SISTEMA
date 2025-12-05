#!/usr/bin/env python
"""
Script de inicialización rápida para ICASA-GEO
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth.models import User, Group

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.sqlite')
    django.setup()

def create_migrations():
    """Crear y aplicar migraciones"""
    print("📦 Creando migraciones...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("🔄 Aplicando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Crear superusuario si no existe"""
    print("👤 Configurando superusuario...")
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@icasa.com',
            password='admin123',
            first_name='Administrador',
            last_name='ICASA'
        )
        print("✅ Superusuario creado: admin/admin123")
    else:
        print("ℹ️  Superusuario ya existe")

def create_groups():
    """Crear grupos de usuarios"""
    print("👥 Creando grupos de usuarios...")
    
    groups = ['Administradores', 'Editores', 'Revisores', 'Lectores']
    
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✅ Grupo creado: {group_name}")

def setup_knowledge_base():
    """Configurar datos iniciales del Knowledge Base"""
    print("📚 Configurando Knowledge Base...")
    
    try:
        execute_from_command_line(['manage.py', 'setup_knowledge_base'])
        print("✅ Knowledge Base configurado")
    except Exception as e:
        print(f"⚠️  Error configurando Knowledge Base: {e}")

def main():
    """Función principal"""
    print("🚀 INICIALIZANDO ICASA-GEO")
    print("=" * 50)
    
    setup_django()
    create_migrations()
    create_superuser()
    create_groups()
    setup_knowledge_base()
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("\n📋 INFORMACIÓN DE ACCESO:")
    print("   URL: http://127.0.0.1:8000/admin/")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n🔗 ENDPOINTS API:")
    print("   Knowledge Base: http://127.0.0.1:8000/api/v1/knowledge/")
    print("   Categorías: http://127.0.0.1:8000/api/v1/knowledge/categories/")
    print("   Documentos: http://127.0.0.1:8000/api/v1/knowledge/documents/")
    print("\n🚀 Para iniciar el servidor:")
    print("   python manage.py runserver")

if __name__ == '__main__':
    main()