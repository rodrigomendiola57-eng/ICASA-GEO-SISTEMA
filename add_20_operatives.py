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

def create_20_operatives():
    """Crear 20 posiciones operativas (nivel 4) con empleados"""
    
    # Departamentos operativos
    departments = [
        'Producción', 'Logística', 'Almacén', 'Mantenimiento', 
        'Calidad', 'Seguridad', 'Limpieza', 'Transporte'
    ]
    
    # Nombres para empleados
    nombres = [
        'Carlos', 'María', 'José', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura',
        'Miguel', 'Rosa', 'Antonio', 'Elena', 'Francisco', 'Isabel', 'Manuel',
        'Patricia', 'Ramón', 'Silvia', 'Alberto', 'Mónica'
    ]
    
    apellidos = [
        'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez',
        'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández',
        'Díaz', 'Moreno', 'Álvarez', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez'
    ]
    
    # Puestos operativos
    job_titles = [
        'Operario de Producción', 'Técnico de Mantenimiento', 'Auxiliar de Almacén',
        'Conductor', 'Inspector de Calidad', 'Vigilante de Seguridad', 
        'Operario de Limpieza', 'Auxiliar Logístico', 'Técnico de Laboratorio',
        'Operario de Máquinas', 'Auxiliar Administrativo', 'Montacarguista',
        'Empacador', 'Recepcionista', 'Auxiliar de Mantenimiento', 'Operario CNC',
        'Técnico Electrónico', 'Auxiliar de Producción', 'Operario de Soldadura',
        'Técnico de Sistemas'
    ]
    
    print("Creando 20 posiciones operativas (Nivel 4)...")
    
    for i in range(20):
        # Crear posición
        position = Position.objects.create(
            title=job_titles[i],
            department=departments[i % len(departments)],
            level=4,  # Nivel operativo
            responsibilities=f"Ejecutar tareas operativas en {departments[i % len(departments)]}. Cumplir con procedimientos establecidos y reportar novedades.",
            kpis=[
                "Productividad diaria",
                "Cumplimiento de horarios", 
                "Calidad del trabajo",
                "Seguridad laboral"
            ],
            required_processes=[
                "Procedimiento de seguridad",
                "Control de calidad",
                "Reporte de incidencias"
            ]
        )
        
        # Crear empleado (80% ocupados, 20% vacantes)
        if i < 16:  # 16 de 20 posiciones ocupadas
            employee = Employee.objects.create(
                employee_id=f"OP{2000 + i}",
                first_name=nombres[i],
                last_name=apellidos[i],
                email=f"{nombres[i].lower()}.{apellidos[i].lower()}@icasa.com",
                phone=f"555-{2000 + i}",
                hire_date=date(2023, 1 + (i % 12), 1 + (i % 28)),
                is_active=True
            )
            
            # Asignar empleado a posición
            PositionAssignment.objects.create(
                position=position,
                employee=employee,
                start_date=employee.hire_date,
                assignment_type='permanent'
            )
            
            print(f"OK {position.title} - {employee.first_name} {employee.last_name} ({employee.employee_id})")
        else:
            print(f"VACANTE {position.title}")
    
    # Estadísticas finales
    total_positions = Position.objects.count()
    total_employees = Employee.objects.count()
    vacant_positions = Position.objects.filter(
        assignments__isnull=True
    ).count()
    
    print(f"\nESTADISTICAS FINALES:")
    print(f"   Total Posiciones: {total_positions}")
    print(f"   Total Empleados: {total_employees}")
    print(f"   Posiciones Vacantes: {vacant_positions}")
    print(f"   Tasa de Ocupación: {((total_positions - vacant_positions) / total_positions * 100):.1f}%")
    
    print(f"\nBase de datos expandida exitosamente!")
    print(f"   Ahora tienes {total_positions} posiciones para probar el organigrama escalable")

if __name__ == '__main__':
    create_20_operatives()