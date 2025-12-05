"""
Permisos personalizados para ICASA-GEO
"""
from rest_framework import permissions
from django.contrib.auth.models import Group

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los propietarios editar sus objetos
    """
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario
        return obj.created_by == request.user

class CanApproveDocuments(permissions.BasePermission):
    """
    Permiso para aprobar documentos (Gerentes y Administradores)
    """
    def has_permission(self, request, view):
        return request.user.has_perm('knowledge_base.can_approve_documents')

class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios (Solo Administradores)
    """
    def has_permission(self, request, view):
        return request.user.has_perm('auth.can_manage_users')

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite edición solo a Gerentes y Administradores
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si es Gerente o Administrador
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['Gerentes', 'Administradores ICASA']
        
        return any(group in allowed_groups for group in user_groups)

class IsEditorOrAbove(permissions.BasePermission):
    """
    Permiso para Editores, Gerentes y Administradores
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['Editores', 'Gerentes', 'Administradores ICASA']
        
        return any(group in allowed_groups for group in user_groups)

class CanViewAnalytics(permissions.BasePermission):
    """
    Permiso para ver analytics (Gerentes y Administradores)
    """
    def has_permission(self, request, view):
        return request.user.has_perm('knowledge_base.can_view_analytics')

def user_has_role(user, role_name):
    """
    Función helper para verificar si un usuario tiene un rol específico
    """
    return user.groups.filter(name=role_name).exists()

def get_user_role(user):
    """
    Obtener el rol principal del usuario
    """
    roles_priority = [
        'Administradores ICASA',
        'Gerentes', 
        'Editores',
        'Revisores',
        'Lectores'
    ]
    
    user_groups = user.groups.values_list('name', flat=True)
    
    for role in roles_priority:
        if role in user_groups:
            return role
    
    return 'Sin Rol'

def get_role_permissions(role_name):
    """
    Obtener descripción de permisos por rol
    """
    role_permissions = {
        'Administradores ICASA': {
            'description': 'Acceso completo al sistema',
            'permissions': [
                'Gestionar usuarios y roles',
                'Crear, editar y eliminar categorías',
                'Crear, editar y eliminar documentos',
                'Aprobar y rechazar documentos',
                'Ver analytics y reportes',
                'Configurar sistema'
            ]
        },
        'Gerentes': {
            'description': 'Gestión de contenido y aprobaciones',
            'permissions': [
                'Crear y editar categorías',
                'Crear, editar documentos',
                'Aprobar y rechazar documentos',
                'Ver analytics y reportes'
            ]
        },
        'Editores': {
            'description': 'Creación y edición de contenido',
            'permissions': [
                'Crear y editar categorías',
                'Crear y editar documentos',
                'Enviar documentos para revisión'
            ]
        },
        'Revisores': {
            'description': 'Revisión y comentarios',
            'permissions': [
                'Ver todas las categorías',
                'Ver y comentar documentos',
                'Sugerir cambios'
            ]
        },
        'Lectores': {
            'description': 'Solo lectura de contenido aprobado',
            'permissions': [
                'Ver categorías públicas',
                'Ver documentos aprobados',
                'Descargar documentos'
            ]
        }
    }
    
    return role_permissions.get(role_name, {
        'description': 'Rol no definido',
        'permissions': []
    })