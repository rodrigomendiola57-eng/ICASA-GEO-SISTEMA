"""
Permisos personalizados para ICASA-GEO
"""
from rest_framework import permissions

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

class CanApprovePermission(permissions.BasePermission):
    """
    Permiso para aprobar documentos
    """
    def has_permission(self, request, view):
        return request.user.has_perm('core.can_approve')

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite edición solo a usuarios con rol de manager
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.groups.filter(name='Managers').exists()