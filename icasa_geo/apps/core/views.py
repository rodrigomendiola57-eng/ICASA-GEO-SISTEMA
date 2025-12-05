"""
Vistas base para ICASA-GEO
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer

class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base con funcionalidades comunes
    """
    def perform_create(self, serializer):
        """Asignar usuario creador al crear objeto"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Asignar usuario actualizador al actualizar objeto"""
        serializer.save(updated_by=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para usuarios (solo lectura)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)