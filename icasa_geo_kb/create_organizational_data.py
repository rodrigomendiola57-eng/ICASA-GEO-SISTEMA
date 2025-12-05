#!/usr/bin/env python
"""
Script para crear datos de prueba del organigrama ICASA
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment

def create_organizational_structure():
    """Crear estructura organizacional de ICASA"""
    
    print("Creando estructura organizacional de ICASA...")
    
    # 1. NIVEL 1 - DIRECCIÓN GENERAL
    director_general = Position.objects.create(
        title="Director General",
        department="Dirección",
        level=1,
        responsibilities="Dirección estratégica de la organización",
        x_position=500,
        y_position=100
    )
    
    # 2. NIVEL 2 - GERENCIAS
    gerente_admin = Position.objects.create(
        title="Gerente Administrativo",
        department="Administrativo",
        level=2,
        reports_to=director_general,
        responsibilities="Gestión administrativa y recursos humanos",
        x_position=200,
        y_position=300
    )
    
    gerente_comercial = Position.objects.create(
        title="Gerente Comercial",
        department="Comercial",
        level=2,
        reports_to=director_general,
        responsibilities="Desarrollo comercial y ventas",
        x_position=500,
        y_position=300
    )
    
    gerente_operaciones = Position.objects.create(
        title="Gerente de Operaciones",
        department="Operaciones",
        level=2,
        reports_to=director_general,
        responsibilities="Operaciones y producción",
        x_position=800,
        y_position=300
    )
    
    # 3. NIVEL 3 - JEFATURAS
    jefe_rrhh = Position.objects.create(
        title="Jefe de Recursos Humanos",
        department="RRHH",
        level=3,
        reports_to=gerente_admin,
        responsibilities="Gestión del talento humano",
        x_position=100,
        y_position=500
    )
    
    jefe_finanzas = Position.objects.create(
        title="Jefe de Finanzas",
        department="Finanzas",
        level=3,
        reports_to=gerente_admin,
        responsibilities="Control financiero y contable",
        x_position=300,
        y_position=500
    )
    
    jefe_ventas = Position.objects.create(
        title="Jefe de Ventas",
        department="Comercial",
        level=3,
        reports_to=gerente_comercial,
        responsibilities="Gestión del equipo de ventas",
        x_position=500,
        y_position=500
    )
    
    jefe_produccion = Position.objects.create(
        title="Jefe de Producción",
        department="Operaciones",
        level=3,
        reports_to=gerente_operaciones,
        responsibilities="Supervisión de la producción",
        x_position=700,
        y_position=500
    )
    
    jefe_mantenimiento = Position.objects.create(
        title="Jefe de Mantenimiento",
        department="Mantenimiento",
        level=3,
        reports_to=gerente_operaciones,
        responsibilities="Mantenimiento de equipos e instalaciones",
        x_position=900,
        y_position=500
    )
    
    # 4. NIVEL 4 - COORDINADORES Y ESPECIALISTAS
    coord_nominas = Position.objects.create(
        title="Coordinador de Nóminas",
        department="RRHH",
        level=4,
        reports_to=jefe_rrhh,
        responsibilities="Procesamiento de nóminas y beneficios",
        x_position=50,
        y_position=700
    )
    
    analista_contable = Position.objects.create(
        title="Analista Contable",
        department="Finanzas",
        level=4,
        reports_to=jefe_finanzas,
        responsibilities="Análisis contable y reportes financieros",
        x_position=300,
        y_position=700
    )
    
    supervisor_ventas = Position.objects.create(
        title="Supervisor de Ventas",
        department="Comercial",
        level=4,
        reports_to=jefe_ventas,
        responsibilities="Supervisión del equipo de vendedores",
        x_position=500,
        y_position=700
    )
    
    print(f"Creadas {Position.objects.count()} posiciones organizacionales")
    
    # 5. CREAR EMPLEADOS DE EJEMPLO
    print("\nCreando empleados de ejemplo...")
    
    # Director General
    emp_director = Employee.objects.create(
        employee_id="EMP001",
        first_name="Carlos",
        last_name="Rodríguez Mendoza",
        email="carlos.rodriguez@icasa.com",
        phone="555-0001",
        hire_date=date(2020, 1, 15)
    )
    
    # Gerentes
    emp_gerente_admin = Employee.objects.create(
        employee_id="EMP002",
        first_name="María",
        last_name="González López",
        email="maria.gonzalez@icasa.com",
        phone="555-0002",
        hire_date=date(2020, 3, 1)
    )
    
    emp_gerente_comercial = Employee.objects.create(
        employee_id="EMP003",
        first_name="José",
        last_name="Martínez Silva",
        email="jose.martinez@icasa.com",
        phone="555-0003",
        hire_date=date(2020, 6, 15)
    )
    
    print(f"Creados {Employee.objects.count()} empleados")
    
    # 6. CREAR ASIGNACIONES
    print("\nCreando asignaciones de puestos...")
    
    # Asignar Director General
    PositionAssignment.objects.create(
        position=director_general,
        employee=emp_director,
        start_date=date(2020, 1, 15),
        assignment_type='permanent'
    )
    
    # Asignar Gerente Administrativo
    PositionAssignment.objects.create(
        position=gerente_admin,
        employee=emp_gerente_admin,
        start_date=date(2020, 3, 1),
        assignment_type='permanent'
    )
    
    # Asignar Gerente Comercial
    PositionAssignment.objects.create(
        position=gerente_comercial,
        employee=emp_gerente_comercial,
        start_date=date(2020, 6, 15),
        assignment_type='permanent'
    )
    
    print(f"Creadas {PositionAssignment.objects.count()} asignaciones")
    
    # 7. ESTADÍSTICAS FINALES
    print("\nESTADISTICAS FINALES:")
    total_positions = Position.objects.count()
    filled_positions = Position.objects.filter(assignments__end_date__isnull=True).distinct().count()
    vacant_positions = total_positions - filled_positions
    fill_rate = (filled_positions / total_positions * 100) if total_positions > 0 else 0
    
    print(f"   Total de posiciones: {total_positions}")
    print(f"   Posiciones ocupadas: {filled_positions}")
    print(f"   Posiciones vacantes: {vacant_positions}")
    print(f"   Tasa de ocupacion: {fill_rate:.1f}%")
    
    print("\nEstructura organizacional creada exitosamente!")
    print("\nAccede a:")
    print("   - Organigrama: http://127.0.0.1:8000/organizational/")
    print("   - Admin: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    create_organizational_structure()