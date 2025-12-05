#!/usr/bin/env python
"""
Script para crear datos de ejemplo del organigrama ICASA
Ejecutar: python create_sample_org_data.py
"""

import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment

def create_sample_data():
    print("Creando estructura organizacional de ejemplo para ICASA...")
    
    # Limpiar datos existentes
    PositionAssignment.objects.all().delete()
    Employee.objects.all().delete()
    Position.objects.all().delete()
    
    # 1. CREAR PUESTOS (CAJAS)
    positions_data = [
        # Nivel 1 - Dirección
        {"title": "Director General", "department": "Dirección", "level": 1, "x": 500, "y": 50, "reports_to": None},
        
        # Nivel 2 - Gerencias
        {"title": "Gerente de Recursos Humanos", "department": "Recursos Humanos", "level": 2, "x": 200, "y": 200, "reports_to": 1},
        {"title": "Gerente de Finanzas", "department": "Finanzas", "level": 2, "x": 500, "y": 200, "reports_to": 1},
        {"title": "Gerente de Operaciones", "department": "Operaciones", "level": 2, "x": 800, "y": 200, "reports_to": 1},
        
        # Nivel 3 - Jefaturas
        {"title": "Jefe de Reclutamiento", "department": "Recursos Humanos", "level": 3, "x": 100, "y": 350, "reports_to": 2},
        {"title": "Jefe de Nóminas", "department": "Recursos Humanos", "level": 3, "x": 300, "y": 350, "reports_to": 2},
        {"title": "Jefe de Contabilidad", "department": "Finanzas", "level": 3, "x": 450, "y": 350, "reports_to": 3},
        {"title": "Jefe de Tesorería", "department": "Finanzas", "level": 3, "x": 550, "y": 350, "reports_to": 3},
        {"title": "Jefe de Producción", "department": "Operaciones", "level": 3, "x": 750, "y": 350, "reports_to": 4},
        {"title": "Jefe de Calidad", "department": "Operaciones", "level": 3, "x": 850, "y": 350, "reports_to": 4},
    ]
    
    positions = {}
    for i, pos_data in enumerate(positions_data, 1):
        reports_to = positions.get(pos_data["reports_to"]) if pos_data["reports_to"] else None
        
        position = Position.objects.create(
            title=pos_data["title"],
            department=pos_data["department"],
            level=pos_data["level"],
            x_position=pos_data["x"],
            y_position=pos_data["y"],
            reports_to=reports_to,
            responsibilities=f"Responsabilidades del {pos_data['title']}",
            kpis=["KPI 1", "KPI 2", "KPI 3"],
            required_processes=["Proceso A", "Proceso B"]
        )
        positions[i] = position
        print(f"Creado puesto: {position.title}")
    
    # 2. CREAR EMPLEADOS (PERSONAS)
    employees_data = [
        {"id": "EMP001", "first_name": "Carlos", "last_name": "Rodríguez", "email": "carlos.rodriguez@icasa.com", "phone": "555-0001"},
        {"id": "EMP002", "first_name": "María", "last_name": "González", "email": "maria.gonzalez@icasa.com", "phone": "555-0002"},
        {"id": "EMP003", "first_name": "Juan", "last_name": "Pérez", "email": "juan.perez@icasa.com", "phone": "555-0003"},
        {"id": "EMP004", "first_name": "Ana", "last_name": "López", "email": "ana.lopez@icasa.com", "phone": "555-0004"},
        {"id": "EMP005", "first_name": "Luis", "last_name": "Martínez", "email": "luis.martinez@icasa.com", "phone": "555-0005"},
        {"id": "EMP006", "first_name": "Carmen", "last_name": "Sánchez", "email": "carmen.sanchez@icasa.com", "phone": "555-0006"},
        {"id": "EMP007", "first_name": "Roberto", "last_name": "García", "email": "roberto.garcia@icasa.com", "phone": "555-0007"},
        {"id": "EMP008", "first_name": "Patricia", "last_name": "Hernández", "email": "patricia.hernandez@icasa.com", "phone": "555-0008"},
    ]
    
    employees = {}
    for i, emp_data in enumerate(employees_data, 1):
        employee = Employee.objects.create(
            employee_id=emp_data["id"],
            first_name=emp_data["first_name"],
            last_name=emp_data["last_name"],
            email=emp_data["email"],
            phone=emp_data["phone"],
            hire_date=date.today() - timedelta(days=365 * 2),  # Contratado hace 2 años
            is_active=True
        )
        employees[i] = employee
        print(f"Creado empleado: {employee.first_name} {employee.last_name}")
    
    # 3. CREAR ASIGNACIONES (PEGAMENTO)
    assignments_data = [
        {"position": 1, "employee": 1},  # Carlos → Director General
        {"position": 2, "employee": 2},  # María → Gerente RRHH
        {"position": 3, "employee": 3},  # Juan → Gerente Finanzas
        {"position": 4, "employee": 4},  # Ana → Gerente Operaciones
        {"position": 5, "employee": 5},  # Luis → Jefe Reclutamiento
        {"position": 6, "employee": 6},  # Carmen → Jefe Nóminas
        {"position": 7, "employee": 7},  # Roberto → Jefe Contabilidad
        {"position": 8, "employee": 8},  # Patricia → Jefe Tesorería
        # Posiciones 9 y 10 quedan VACANTES para mostrar alertas rojas
    ]
    
    for assign_data in assignments_data:
        assignment = PositionAssignment.objects.create(
            position=positions[assign_data["position"]],
            employee=employees[assign_data["employee"]],
            start_date=date.today() - timedelta(days=365),
            assignment_type='permanent'
        )
        print(f"Asignado: {assignment.employee} -> {assignment.position}")
    
    print(f"\nDatos de ejemplo creados exitosamente!")
    print(f"Resumen:")
    print(f"   - {Position.objects.count()} puestos creados")
    print(f"   - {Employee.objects.count()} empleados creados")
    print(f"   - {PositionAssignment.objects.count()} asignaciones activas")
    print(f"   - {Position.objects.count() - PositionAssignment.objects.count()} puestos vacantes")
    print(f"\nAhora puedes ver el organigrama en: http://127.0.0.1:8001/organizational/")

if __name__ == "__main__":
    create_sample_data()