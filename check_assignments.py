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

def check_assignments():
    """Verificar las asignaciones creadas"""
    
    print("VERIFICANDO ASIGNACIONES...")
    
    # Contar totales
    total_positions = Position.objects.count()
    total_employees = Employee.objects.count()
    total_assignments = PositionAssignment.objects.count()
    
    print(f"Total Posiciones: {total_positions}")
    print(f"Total Empleados: {total_employees}")
    print(f"Total Asignaciones: {total_assignments}")
    
    # Verificar algunas asignaciones específicas
    print("\nPRIMERAS 10 ASIGNACIONES:")
    assignments = PositionAssignment.objects.all()[:10]
    for assignment in assignments:
        print(f"  {assignment.employee.first_name} {assignment.employee.last_name} -> {assignment.position.title}")
        print(f"    Inicio: {assignment.start_date}, Fin: {assignment.end_date}")
        print(f"    Activa: {assignment.is_active()}")
    
    # Verificar posiciones vacantes
    print("\nVERIFICANDO VACANTES:")
    today = timezone.now().date()
    
    for position in Position.objects.all()[:10]:
        current_employee = position.get_current_employee(today)
        is_vacant = position.is_vacant(today)
        
        print(f"  {position.title}:")
        print(f"    Empleado actual: {current_employee}")
        print(f"    Es vacante: {is_vacant}")
        
        # Verificar asignaciones de esta posición
        assignments = position.assignments.filter(end_date__isnull=True)
        print(f"    Asignaciones activas: {assignments.count()}")
        for assignment in assignments:
            print(f"      - {assignment.employee.first_name} {assignment.employee.last_name} desde {assignment.start_date}")

if __name__ == '__main__':
    check_assignments()