#!/usr/bin/env python
"""
Script de prueba para el módulo de organigramas
Ejecutar con: python test_organigramas.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

def test_organizational_views():
    """Probar las vistas del módulo organizacional"""
    from django.test import Client
    from django.contrib.auth.models import User
    
    print("🧪 Iniciando pruebas del módulo de organigramas...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@icasa.com',
            'first_name': 'Usuario',
            'last_name': 'Prueba'
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print("✅ Usuario de prueba creado")
    
    # Login
    login_success = client.login(username='test_user', password='test123')
    if login_success:
        print("✅ Login exitoso")
    else:
        print("❌ Error en login")
        return
    
    # Probar dashboard
    try:
        response = client.get('/organizational/')
        if response.status_code == 200:
            print("✅ Dashboard carga correctamente")
        else:
            print(f"❌ Error en dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al cargar dashboard: {e}")
    
    # Probar API de creación
    try:
        response = client.post('/organizational/api/departmental/create/', {
            'name': 'Organigrama de Prueba',
            'department': 'Administrativo',
            'description': 'Organigrama creado para pruebas'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API de creación funciona correctamente")
            else:
                print(f"❌ Error en API: {data.get('error')}")
        else:
            print(f"❌ Error HTTP en API: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al probar API: {e}")
    
    print("🏁 Pruebas completadas")

def create_sample_data():
    """Crear datos de ejemplo básicos"""
    from apps.organizational.models import DepartmentalChart
    from django.contrib.auth.models import User
    
    print("📊 Creando datos de ejemplo...")
    
    # Obtener o crear usuario admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@icasa.com',
            'first_name': 'Administrador',
            'last_name': 'ICASA',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Usuario admin creado")
    
    # Crear organigramas de ejemplo
    sample_charts = [
        {
            'name': 'Organigrama Administrativo',
            'department': 'Administrativo',
            'description': 'Estructura organizacional del área administrativa',
            'status': 'active'
        },
        {
            'name': 'Organigrama Comercial',
            'department': 'Comercial', 
            'description': 'Estructura organizacional del área comercial',
            'status': 'active'
        },
        {
            'name': 'Organigrama de Operaciones',
            'department': 'Operaciones',
            'description': 'Estructura organizacional del área de operaciones',
            'status': 'draft'
        }
    ]
    
    for chart_data in sample_charts:
        chart, created = DepartmentalChart.objects.get_or_create(
            name=chart_data['name'],
            defaults={
                'department': chart_data['department'],
                'description': chart_data['description'],
                'status': chart_data['status'],
                'created_by': admin_user,
                'is_external': False
            }
        )
        
        if created:
            print(f"✅ Creado: {chart.name}")
        else:
            print(f"ℹ️  Ya existe: {chart.name}")
    
    print("📊 Datos de ejemplo creados")

if __name__ == '__main__':
    print("🚀 ICASA-GEO - Prueba del Módulo de Organigramas")
    print("=" * 50)
    
    try:
        # Crear datos de ejemplo
        create_sample_data()
        print()
        
        # Ejecutar pruebas
        test_organizational_views()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Para probar manualmente:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Ve a: http://localhost:8000/organizational/")
    print("3. Login con: admin / admin123")