#!/usr/bin/env python
"""
Script para crear organigramas de prueba
"""
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import DepartmentalChart
from django.contrib.auth.models import User

def create_sample_charts():
    """Crear organigramas de prueba"""
    
    print("Creando organigramas de prueba...")
    
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
        print(f"Usuario admin creado: admin/admin123")
    
    # Crear organigramas de ejemplo
    charts_data = [
        {
            'name': 'Organigrama Dirección General',
            'department': 'Dirección',
            'description': 'Estructura organizacional de la Dirección General de ICASA',
            'status': 'active'
        },
        {
            'name': 'Organigrama Administrativo 2024',
            'department': 'Administrativo', 
            'description': 'Estructura del área administrativa actualizada',
            'status': 'active'
        },
        {
            'name': 'Organigrama Comercial',
            'department': 'Comercial',
            'description': 'Estructura del equipo comercial y ventas',
            'status': 'active'
        },
        {
            'name': 'Organigrama Operaciones',
            'department': 'Operaciones',
            'description': 'Estructura operativa y de producción',
            'status': 'draft'
        },
        {
            'name': 'Organigrama RRHH',
            'department': 'RRHH',
            'description': 'Estructura de Recursos Humanos',
            'status': 'active'
        },
        {
            'name': 'Organigrama Finanzas',
            'department': 'Finanzas',
            'description': 'Estructura del área financiera y contable',
            'status': 'active'
        },
        {
            'name': 'Organigrama Mantenimiento',
            'department': 'Mantenimiento',
            'description': 'Estructura del área de mantenimiento',
            'status': 'draft'
        }
    ]
    
    created_count = 0
    for chart_data in charts_data:
        chart, created = DepartmentalChart.objects.get_or_create(
            name=chart_data['name'],
            defaults={
                'department': chart_data['department'],
                'description': chart_data['description'],
                'status': chart_data['status'],
                'created_by': admin_user,
                'is_external': False,
                'version': '1.0'
            }
        )
        
        if created:
            created_count += 1
            print(f"Creado: {chart.name}")
        else:
            print(f"Ya existe: {chart.name}")
    
    print(f"\nResumen:")
    print(f"- Organigramas creados: {created_count}")
    print(f"- Total en sistema: {DepartmentalChart.objects.count()}")
    print(f"- Activos: {DepartmentalChart.objects.filter(status='active').count()}")
    print(f"- Borradores: {DepartmentalChart.objects.filter(status='draft').count()}")
    
    print(f"\nAccede a: http://127.0.0.1:8000/organizational/")

if __name__ == "__main__":
    create_sample_charts()