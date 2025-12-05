from apps.organizational.models import Employee

print("=== VERIFICANDO NOMBRES DE EMPLEADOS ===")

employees = Employee.objects.all()
for employee in employees:
    print(f"ID: {employee.employee_id}")
    print(f"Nombre: {repr(employee.first_name)} {repr(employee.last_name)}")
    print(f"Email: {repr(employee.email)}")
    print("---")

print(f"\nTotal empleados: {employees.count()}")