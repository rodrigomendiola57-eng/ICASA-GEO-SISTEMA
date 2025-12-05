#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
sys.path.append('c:\\Sistema GEO (Gestión Estratégica Organizacional)\\icasa_geo_kb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings')
django.setup()

from apps.organizational.models import Position, Employee, PositionAssignment

def clear_existing_data():
    """Limpiar datos existentes"""
    print("Limpiando datos existentes...")
    PositionAssignment.objects.all().delete()
    Employee.objects.all().delete()
    Position.objects.all().delete()

def create_icasa_structure():
    """Crear estructura organizacional de ICASA"""
    
    # NIVEL 1: DIRECTORES (3)
    print("Creando Nivel 1: Directores...")
    
    director_general = Position.objects.create(
        title="Director General",
        department="Dirección General",
        level=1,
        responsibilities="Dirección estratégica y liderazgo organizacional"
    )
    
    director_comercial = Position.objects.create(
        title="Director Comercial", 
        department="Dirección Comercial",
        level=1,
        reports_to=director_general,
        responsibilities="Supervisión de operaciones comerciales y departamentos operativos"
    )
    
    director_administrativo = Position.objects.create(
        title="Director Administrativo",
        department="Dirección Administrativa", 
        level=1,
        reports_to=director_general,
        responsibilities="Gestión administrativa y recursos corporativos"
    )
    
    # NIVEL 2: GERENTES (3 bajo Director Comercial)
    print("Creando Nivel 2: Gerentes...")
    
    gerente_operaciones = Position.objects.create(
        title="Gerente de Operaciones",
        department="Operaciones",
        level=2,
        reports_to=director_comercial,
        responsibilities="Supervisión de procesos operativos y productivos"
    )
    
    gerente_porteo = Position.objects.create(
        title="Gerente de Porteo",
        department="Porteo", 
        level=2,
        reports_to=director_comercial,
        responsibilities="Gestión de servicios de porteo y logística"
    )
    
    gerente_devoluciones = Position.objects.create(
        title="Gerente de Devoluciones",
        department="Devoluciones",
        level=2, 
        reports_to=director_comercial,
        responsibilities="Manejo de devoluciones y atención al cliente"
    )
    
    # NIVEL 3: JEFES (9 total - 3 por cada gerente)
    print("Creando Nivel 3: Jefes...")
    
    jefes_data = [
        # Operaciones
        ("Jefe de Producción", "Operaciones", gerente_operaciones),
        ("Jefe de Calidad", "Operaciones", gerente_operaciones), 
        ("Jefe de Mantenimiento", "Operaciones", gerente_operaciones),
        # Porteo
        ("Jefe de Logística", "Porteo", gerente_porteo),
        ("Jefe de Transporte", "Porteo", gerente_porteo),
        ("Jefe de Almacén", "Porteo", gerente_porteo),
        # Devoluciones
        ("Jefe de Atención al Cliente", "Devoluciones", gerente_devoluciones),
        ("Jefe de Procesamiento", "Devoluciones", gerente_devoluciones),
        ("Jefe de Control", "Devoluciones", gerente_devoluciones)
    ]
    
    jefes = []
    for title, dept, reports_to in jefes_data:
        jefe = Position.objects.create(
            title=title,
            department=dept,
            level=3,
            reports_to=reports_to,
            responsibilities=f"Supervisión directa de equipos en {dept}"
        )
        jefes.append(jefe)
    
    # NIVEL 4: OPERADORES (18 total - 2 por cada jefe)
    print("Creando Nivel 4: Operadores...")
    
    operadores = []
    for i, jefe in enumerate(jefes):
        for j in range(2):
            operador = Position.objects.create(
                title=f"Operador {j+1}",
                department=jefe.department,
                level=4,
                reports_to=jefe,
                responsibilities="Ejecución de tareas operativas y procesos"
            )
            operadores.append(operador)
    
    # NIVEL 5: AUXILIARES (18 total - 2 por cada jefe)
    print("Creando Nivel 5: Auxiliares...")
    
    auxiliares = []
    for i, jefe in enumerate(jefes):
        for j in range(2):
            auxiliar = Position.objects.create(
                title=f"Auxiliar {j+1}",
                department=jefe.department,
                level=5,
                reports_to=jefe,
                responsibilities="Apoyo en tareas operativas y asistencia general"
            )
            auxiliares.append(auxiliar)
    
    # CREAR EMPLEADOS Y ASIGNACIONES
    print("Creando empleados y asignaciones...")
    
    nombres = [
        "Carlos", "María", "José", "Ana", "Luis", "Carmen", "Pedro", "Laura",
        "Miguel", "Rosa", "Antonio", "Elena", "Francisco", "Isabel", "Manuel",
        "Patricia", "Ramón", "Silvia", "Alberto", "Mónica", "Fernando", "Lucía",
        "Ricardo", "Beatriz", "Sergio", "Cristina", "Alejandro", "Pilar", "Javier",
        "Dolores", "Ángel", "Teresa", "Rafael", "Amparo", "Gonzalo", "Remedios",
        "Emilio", "Concepción", "Víctor", "Esperanza", "Rubén", "Soledad", "Adrián",
        "Inmaculada", "Iván", "Rosario", "Óscar", "Encarnación", "Marcos", "Asunción"
    ]
    
    apellidos = [
        "García", "Rodríguez", "González", "Fernández", "López", "Martínez",
        "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández",
        "Díaz", "Moreno", "Álvarez", "Muñoz", "Romero", "Alonso", "Gutiérrez",
        "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez",
        "Serrano", "Blanco", "Suárez", "Molina", "Morales", "Ortega", "Delgado",
        "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias", "Medina", "Garrido",
        "Cortés", "Castillo", "Santos", "Lozano", "Guerrero", "Cano", "Prieto", "Méndez"
    ]
    
    # Asignar empleados (85% ocupación)
    all_positions = [director_general, director_comercial, director_administrativo] + \
                   [gerente_operaciones, gerente_porteo, gerente_devoluciones] + \
                   jefes + operadores + auxiliares
    
    total_positions = len(all_positions)
    positions_to_fill = int(total_positions * 0.85)  # 85% ocupación
    
    for i in range(positions_to_fill):
        position = all_positions[i]
        
        employee = Employee.objects.create(
            employee_id=f"IC{3000 + i:03d}",
            first_name=nombres[i % len(nombres)],
            last_name=apellidos[i % len(apellidos)],
            email=f"{nombres[i % len(nombres)].lower()}.{apellidos[i % len(apellidos)].lower()}@icasa.com",
            phone=f"555-{3000 + i}",
            hire_date=date(2023, 1 + (i % 12), 1 + (i % 28)),
            is_active=True
        )
        
        PositionAssignment.objects.create(
            position=position,
            employee=employee,
            start_date=employee.hire_date,
            assignment_type='permanent'
        )
        
        print(f"OK {position.title} - {employee.first_name} {employee.last_name}")
    
    # Mostrar estadísticas
    print(f"\nESTRUCTURA ICASA CREADA:")
    print(f"  Nivel 1 (Directores): 3")
    print(f"  Nivel 2 (Gerentes): 3") 
    print(f"  Nivel 3 (Jefes): 9")
    print(f"  Nivel 4 (Operadores): 18")
    print(f"  Nivel 5 (Auxiliares): 18")
    print(f"  TOTAL POSICIONES: {total_positions}")
    print(f"  EMPLEADOS ASIGNADOS: {positions_to_fill}")
    print(f"  POSICIONES VACANTES: {total_positions - positions_to_fill}")
    print(f"  TASA DE OCUPACION: {(positions_to_fill/total_positions*100):.1f}%")

if __name__ == '__main__':
    clear_existing_data()
    create_icasa_structure()