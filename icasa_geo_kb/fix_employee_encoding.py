from apps.organizational.models import Employee

print("=== CORRIGIENDO CODIFICACIÓN DE NOMBRES DE EMPLEADOS ===")

# Mapeo de correcciones para caracteres especiales
corrections = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'ñ': 'n', 'Ñ': 'N',
    'ü': 'u', 'Ü': 'U'
}

def fix_text(text):
    """Corrige caracteres especiales en un texto"""
    if not text:
        return text
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    return text

# Corregir nombres de empleados
employees = Employee.objects.all()
updated_count = 0

for employee in employees:
    original_first = employee.first_name
    original_last = employee.last_name
    original_email = employee.email
    
    # Corregir nombres
    employee.first_name = fix_text(employee.first_name)
    employee.last_name = fix_text(employee.last_name)
    employee.email = fix_text(employee.email)
    
    # Guardar si hubo cambios
    if (employee.first_name != original_first or 
        employee.last_name != original_last or 
        employee.email != original_email):
        
        employee.save()
        updated_count += 1
        print(f"Actualizado: {original_first} {original_last} -> {employee.first_name} {employee.last_name}")
        if original_email != employee.email:
            print(f"  Email: {original_email} -> {employee.email}")

print(f"\nTotal de empleados actualizados: {updated_count}")

# Mostrar empleados finales
print("\n=== EMPLEADOS CORREGIDOS ===")
for employee in Employee.objects.all().order_by('first_name'):
    print(f"{employee.first_name} {employee.last_name} ({employee.employee_id}) - {employee.email}")