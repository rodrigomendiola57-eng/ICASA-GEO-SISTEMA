from django.contrib import admin
from .models import (
    OrganizationalChart, Position, ProcessFlow, Employee, PositionAssignment,
    JobProfile, Skill, EmployeeSkill, Committee, CommitteeMembership, DepartmentalChart,
    ProcessCategory, FlowchartProcess, FlowchartTemplate
)


@admin.register(OrganizationalChart)
class OrganizationalChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_main', 'status', 'created_at']
    list_filter = ['status', 'is_main', 'created_at']
    search_fields = ['name', 'description']

@admin.register(DepartmentalChart)
class DepartmentalChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'status', 'is_external', 'created_by', 'created_at']
    list_filter = ['department', 'status', 'is_external', 'created_at']
    search_fields = ['name', 'description', 'department']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'level', 'reports_to', 'get_current_employee']
    list_filter = ['department', 'level']
    search_fields = ['title', 'department', 'responsibilities']
    
    def get_current_employee(self, obj):
        employee = obj.get_current_employee()
        return f"{employee.first_name} {employee.last_name}" if employee else "VACANTE"
    get_current_employee.short_description = 'Empleado Actual'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'hire_date', 'is_active']
    list_filter = ['is_active', 'hire_date']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    date_hierarchy = 'hire_date'

@admin.register(PositionAssignment)
class PositionAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'position', 'start_date', 'end_date', 'assignment_type']
    list_filter = ['assignment_type', 'start_date', 'end_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'position__title']
    date_hierarchy = 'start_date'

@admin.register(JobProfile)
class JobProfileAdmin(admin.ModelAdmin):
    list_display = ['position', 'education_required', 'experience_required']
    search_fields = ['position__title', 'objective', 'education_required']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_certification']
    list_filter = ['category', 'is_certification']
    search_fields = ['name', 'description']

@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ['employee', 'skill', 'level', 'status', 'certification_date']
    list_filter = ['level', 'status', 'skill__category']
    search_fields = ['employee__first_name', 'employee__last_name', 'skill__name']

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'meeting_frequency']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'purpose']

@admin.register(CommitteeMembership)
class CommitteeMembershipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'committee', 'role', 'start_date', 'end_date']
    list_filter = ['role', 'committee__type']
    search_fields = ['employee__first_name', 'employee__last_name', 'committee__name']

@admin.register(ProcessFlow)
class ProcessFlowAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']

# Flowchart Models Admin
@admin.register(ProcessCategory)
class ProcessCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'color']
    list_filter = ['category_type']
    search_fields = ['name', 'description']

@admin.register(FlowchartProcess)
class FlowchartProcessAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'complexity_level', 'owner', 'created_at']
    list_filter = ['status', 'complexity_level', 'category__category_type']
    search_fields = ['title', 'description', 'responsible_department']
    readonly_fields = ['view_count', 'created_at', 'updated_at']

@admin.register(FlowchartTemplate)
class FlowchartTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty_level', 'usage_count', 'is_active']
    list_filter = ['category', 'difficulty_level', 'is_active']
    search_fields = ['name', 'description']