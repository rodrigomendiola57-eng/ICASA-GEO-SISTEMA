#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Sistema GEO (Gestión Estratégica Organizacional)\\icasa_geo_kb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment
from django.utils import timezone

def debug_vacant_issue():
    """Debug del problema de vacantes"""
    
    print("DEBUGGING PROBLEMA DE VACANTES...")
    
    view_date = timezone.now().date()
    print(f"Fecha actual: {view_date}")
    
    # Verificar las primeras 5 posiciones
    positions = Position.objects.all()[:5]
    
    for position in positions:
        print(f"\n=== {position.title} ===")
        
        # Método get_current_employee
        employee = position.get_current_employee(view_date)
        print(f"get_current_employee(): {employee}")
        
        # Método is_vacant
        is_vacant = position.is_vacant(view_date)
        print(f"is_vacant(): {is_vacant}")
        
        # Verificar asignaciones manualmente
        assignments = position.assignments.filter(
            start_date__lte=view_date,
            end_date__isnull=True
        )
        print(f"Asignaciones activas: {assignments.count()}")
        
        for assignment in assignments:
            print(f"  - {assignment.employee} desde {assignment.start_date}")
            print(f"    Activa: {assignment.is_active(view_date)}")
        
        # Verificar todas las asignaciones de esta posición
        all_assignments = position.assignments.all()
        print(f"Total asignaciones: {all_assignments.count()}")
        
        for assignment in all_assignments:
            print(f"  - {assignment.employee}: {assignment.start_date} - {assignment.end_date}")

if __name__ == '__main__':
    debug_vacant_issue()