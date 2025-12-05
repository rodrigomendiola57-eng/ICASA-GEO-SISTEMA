#!/usr/bin/env python
"""
Script para crear la estructura organizacional completa de ICASA
30 empleados distribuidos jerárquicamente según especificaciones
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment

def clear_existing_data():
    """Limpiar datos existentes"""
    print("Limpiando datos existentes...")
    PositionAssignment.objects.all().delete()
    Employee.objects.all().delete()
    Position.objects.all().delete()
    print("Datos limpiados")

def create_icasa_positions():
    """Crear estructura de posiciones de ICASA"""
    print("Creando estructura organizacional de ICASA...")
    
    positions = []
    
    # NIVEL 1: Director General
    dg = Position.objects.create(
        title="Director General",
        department="Dirección",
        level=1,
        responsibilities="Dirección estratégica y liderazgo general de ICASA"
    )
    positions.append(dg)
    
    # NIVEL 2: Directores (2)
    dir_comercial = Position.objects.create(
        title="Director Comercial",
        department="Comercial", 
        level=2,
        reports_to=dg,
        responsibilities="Dirección de estrategias comerciales y ventas"
    )
    
    dir_administrativo = Position.objects.create(
        title="Director Administrativo",
        department="Administrativo",
        level=2, 
        reports_to=dg,
        responsibilities="Dirección de operaciones administrativas y recursos"
    )
    positions.extend([dir_comercial, dir_administrativo])
    
    # NIVEL 3: Gerentes (5)
    gerentes = [
        ("Gerente de Ventas", "Comercial", dir_comercial),
        ("Gerente de Marketing", "Comercial", dir_comercial),
        ("Gerente de Recursos Humanos", "Administrativo", dir_administrativo),
        ("Gerente de Finanzas", "Administrativo", dir_administrativo),
        ("Gerente de Operaciones", "Operaciones", dir_administrativo)
    ]
    
    gerente_objs = []
    for titulo, dept, jefe in gerentes:
        gerente = Position.objects.create(
            title=titulo,
            department=dept,
            level=3,
            reports_to=jefe,
            responsibilities=f"Gestión y supervisión del área de {titulo.split(' de ')[1]}"
        )
        gerente_objs.append(gerente)
        positions.append(gerente)
    
    # NIVEL 4: Jefes (10)
    jefes_data = [
        ("Jefe de Ventas Zona Norte", "Comercial", gerente_objs[0]),
        ("Jefe de Ventas Zona Sur", "Comercial", gerente_objs[0]),
        ("Jefe de Publicidad", "Comercial", gerente_objs[1]),
        ("Jefe de Comunicaciones", "Comercial", gerente_objs[1]),
        ("Jefe de Reclutamiento", "RRHH", gerente_objs[2]),
        ("Jefe de Capacitación", "RRHH", gerente_objs[2]),
        ("Jefe de Contabilidad", "Finanzas", gerente_objs[3]),
        ("Jefe de Tesorería", "Finanzas", gerente_objs[3]),
        ("Jefe de Producción", "Operaciones", gerente_objs[4]),
        ("Jefe de Calidad", "Operaciones", gerente_objs[4])
    ]
    
    jefe_objs = []
    for titulo, dept, jefe in jefes_data:
        jefe_obj = Position.objects.create(
            title=titulo,
            department=dept,
            level=4,
            reports_to=jefe,
            responsibilities=f"Supervisión directa del área de {titulo.split(' de ')[1] if ' de ' in titulo else titulo}"
        )
        jefe_objs.append(jefe_obj)
        positions.append(jefe_obj)
    
    # NIVELES 5 y 6: Operadores y Auxiliares (13 restantes)
    operadores_auxiliares = [
        ("Ejecutivo de Ventas Senior", "Comercial", 5, jefe_objs[0]),
        ("Ejecutivo de Ventas", "Comercial", 5, jefe_objs[0]),
        ("Ejecutivo de Ventas Junior", "Comercial", 5, jefe_objs[1]),
        ("Diseñador Gráfico", "Comercial", 5, jefe_objs[2]),
        ("Community Manager", "Comercial", 5, jefe_objs[3]),
        ("Analista de RRHH", "RRHH", 5, jefe_objs[4]),
        ("Especialista en Capacitación", "RRHH", 5, jefe_objs[5]),
        ("Contador Senior", "Finanzas", 5, jefe_objs[6]),
        ("Auxiliar Contable", "Finanzas", 6, jefe_objs[6]),
        ("Cajero", "Finanzas", 6, jefe_objs[7]),
        ("Operador de Producción", "Operaciones", 5, jefe_objs[8]),
        ("Inspector de Calidad", "Operaciones", 5, jefe_objs[9]),
        ("Auxiliar de Calidad", "Operaciones", 6, jefe_objs[9])
    ]
    
    for titulo, dept, nivel, jefe in operadores_auxiliares:
        pos = Position.objects.create(
            title=titulo,
            department=dept,
            level=nivel,
            reports_to=jefe,
            responsibilities=f"Ejecución de tareas específicas en {titulo}"
        )
        positions.append(pos)
    
    print(f"Creadas {len(positions)} posiciones organizacionales")
    return positions

def create_icasa_employees():
    """Crear empleados de ICASA con nombres reales"""
    print("Creando empleados de ICASA...")
    
    empleados_data = [
        # Director General
        ("Carlos", "Mendoza", "Rodríguez", "carlos.mendoza@icasa.com", "EMP001"),
        
        # Directores
        ("María", "González", "López", "maria.gonzalez@icasa.com", "EMP002"),
        ("Roberto", "Hernández", "Silva", "roberto.hernandez@icasa.com", "EMP003"),
        
        # Gerentes
        ("Ana", "Martínez", "Torres", "ana.martinez@icasa.com", "EMP004"),
        ("Luis", "García", "Morales", "luis.garcia@icasa.com", "EMP005"),
        ("Carmen", "Rodríguez", "Vega", "carmen.rodriguez@icasa.com", "EMP006"),
        ("Miguel", "López", "Castillo", "miguel.lopez@icasa.com", "EMP007"),
        ("Patricia", "Sánchez", "Ruiz", "patricia.sanchez@icasa.com", "EMP008"),
        
        # Jefes
        ("Fernando", "Jiménez", "Moreno", "fernando.jimenez@icasa.com", "EMP009"),
        ("Lucía", "Vargas", "Herrera", "lucia.vargas@icasa.com", "EMP010"),
        ("Diego", "Castro", "Peña", "diego.castro@icasa.com", "EMP011"),
        ("Sofía", "Ramírez", "Guerrero", "sofia.ramirez@icasa.com", "EMP012"),
        ("Andrés", "Flores", "Medina", "andres.flores@icasa.com", "EMP013"),
        ("Valeria", "Torres", "Ortega", "valeria.torres@icasa.com", "EMP014"),
        ("Javier", "Morales", "Delgado", "javier.morales@icasa.com", "EMP015"),
        ("Isabella", "Vega", "Romero", "isabella.vega@icasa.com", "EMP016"),
        ("Sebastián", "Herrera", "Aguilar", "sebastian.herrera@icasa.com", "EMP017"),
        ("Camila", "Peña", "Navarro", "camila.pena@icasa.com", "EMP018"),
        
        # Operadores y Auxiliares
        ("Alejandro", "Guerrero", "Ramos", "alejandro.guerrero@icasa.com", "EMP019"),
        ("Natalia", "Medina", "Cruz", "natalia.medina@icasa.com", "EMP020"),
        ("Gabriel", "Ortega", "Mendoza", "gabriel.ortega@icasa.com", "EMP021"),
        ("Daniela", "Delgado", "Jiménez", "daniela.delgado@icasa.com", "EMP022"),
        ("Mateo", "Romero", "Vargas", "mateo.romero@icasa.com", "EMP023"),
        ("Valentina", "Aguilar", "Castro", "valentina.aguilar@icasa.com", "EMP024"),
        ("Nicolás", "Navarro", "Ramírez", "nicolas.navarro@icasa.com", "EMP025"),
        ("Mariana", "Ramos", "Flores", "mariana.ramos@icasa.com", "EMP026"),
        ("Santiago", "Cruz", "Torres", "santiago.cruz@icasa.com", "EMP027"),
        ("Emilia", "Mendoza", "Morales", "emilia.mendoza@icasa.com", "EMP028"),
        ("Tomás", "Jiménez", "Vega", "tomas.jimenez@icasa.com", "EMP029"),
        ("Regina", "Vargas", "Herrera", "regina.vargas@icasa.com", "EMP030")
    ]
    
    employees = []
    base_date = date(2020, 1, 15)
    
    for i, (nombre, apellido1, apellido2, email, emp_id) in enumerate(empleados_data):
        # Fechas de contratación escalonadas
        hire_date = base_date + timedelta(days=i*30 + random.randint(0, 25))
        
        employee = Employee.objects.create(
            first_name=nombre,
            last_name=f"{apellido1} {apellido2}",
            email=email,
            employee_id=emp_id,
            hire_date=hire_date,
            phone=f"555-{1000 + i:04d}",
            is_active=True
        )
        employees.append(employee)
    
    print(f"Creados {len(employees)} empleados")
    return employees

def assign_employees_to_positions():
    """Asignar empleados a posiciones según jerarquía"""
    print("Asignando empleados a posiciones...")
    
    positions = Position.objects.all().order_by('level', 'id')
    employees = Employee.objects.all().order_by('id')
    
    assignments = []
    
    for i, position in enumerate(positions):
        if i < len(employees):
            employee = employees[i]
            
            assignment = PositionAssignment.objects.create(
                position=position,
                employee=employee,
                start_date=employee.hire_date,
                assignment_type='permanent'
            )
            assignments.append(assignment)
    
    print(f"Creadas {len(assignments)} asignaciones")
    return assignments

def print_organizational_summary():
    """Mostrar resumen de la estructura creada"""
    print("\n" + "="*60)
    print("RESUMEN DE ESTRUCTURA ORGANIZACIONAL ICASA")
    print("="*60)
    
    levels = {
        1: "Director General",
        2: "Directores", 
        3: "Gerentes",
        4: "Jefes",
        5: "Operadores",
        6: "Auxiliares"
    }
    
    for level, name in levels.items():
        count = Position.objects.filter(level=level).count()
        print(f"Nivel {level} - {name}: {count} posiciones")
    
    print(f"\nTotal Posiciones: {Position.objects.count()}")
    print(f"Total Empleados: {Employee.objects.count()}")
    print(f"Total Asignaciones: {PositionAssignment.objects.count()}")
    
    # Mostrar por departamento
    print("\nDISTRIBUCION POR DEPARTAMENTO:")
    departments = Position.objects.values_list('department', flat=True).distinct()
    for dept in departments:
        count = Position.objects.filter(department=dept).count()
        print(f"  {dept}: {count} posiciones")

def main():
    """Función principal"""
    print("Iniciando creacion de estructura organizacional ICASA")
    print("="*60)
    
    try:
        # Limpiar datos existentes
        clear_existing_data()
        
        # Crear posiciones
        positions = create_icasa_positions()
        
        # Crear empleados
        employees = create_icasa_employees()
        
        # Asignar empleados a posiciones
        assignments = assign_employees_to_positions()
        
        # Mostrar resumen
        print_organizational_summary()
        
        print("\nEstructura organizacional ICASA creada exitosamente!")
        print("El auto layout ahora respetara la jerarquia correcta")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()