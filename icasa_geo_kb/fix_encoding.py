from apps.organizational.models import Position

print("=== CORRIGIENDO CODIFICACIÓN DE CARACTERES ===")

# Mapeo de correcciones
corrections = {
    'Dirección General': 'Direccion General',
    'Dirección Comercial': 'Direccion Comercial', 
    'Dirección Administrativa': 'Direccion Administrativa',
    'Gestión': 'Gestion',
    'Supervisión': 'Supervision',
    'Operación': 'Operacion',
    'Atención': 'Atencion',
    'Logística': 'Logistica',
    'Estratégica': 'Estrategica'
}

# Corregir departamentos
positions = Position.objects.all()
updated_count = 0

for position in positions:
    original_dept = position.department
    original_resp = position.responsibilities
    
    # Corregir departamento
    for wrong, correct in corrections.items():
        if wrong in position.department:
            position.department = position.department.replace(wrong, correct)
    
    # Corregir responsabilidades
    if position.responsibilities:
        for wrong, correct in corrections.items():
            if wrong in position.responsibilities:
                position.responsibilities = position.responsibilities.replace(wrong, correct)
    
    # Guardar si hubo cambios
    if position.department != original_dept or position.responsibilities != original_resp:
        position.save()
        updated_count += 1
        print(f"Actualizado: {position.title}")
        print(f"  Departamento: {original_dept} -> {position.department}")
        if original_resp != position.responsibilities:
            print(f"  Responsabilidades actualizadas")

print(f"\nTotal de posiciones actualizadas: {updated_count}")

# Mostrar estructura final
print("\n=== ESTRUCTURA CORREGIDA ===")
for position in Position.objects.all().order_by('level', 'title'):
    print(f"{position.title} - {position.department}")