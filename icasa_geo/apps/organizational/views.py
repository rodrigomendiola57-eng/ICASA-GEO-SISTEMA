from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

class OrganizationalViewSet(viewsets.ViewSet):
    """
    ViewSet temporal para el módulo Organizational
    """
    
    def list(self, request):
        return Response({
            'message': 'Módulo Organizational en desarrollo',
            'available_endpoints': [
                '/api/v1/organizational/',
                '/api/v1/organizational/status/'
            ]
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        return Response({
            'module': 'organizational',
            'status': 'in_development',
            'features': [
                'Organigramas',
                'Flujogramas BPMN',
                'Estructura organizacional'
            ]
        })