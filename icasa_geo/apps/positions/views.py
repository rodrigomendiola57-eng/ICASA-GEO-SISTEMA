from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

class PositionsViewSet(viewsets.ViewSet):
    """
    ViewSet temporal para el módulo Positions
    """
    
    def list(self, request):
        return Response({
            'message': 'Módulo Positions en desarrollo',
            'available_endpoints': [
                '/api/v1/positions/',
                '/api/v1/positions/status/'
            ]
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        return Response({
            'module': 'positions',
            'status': 'in_development',
            'features': [
                'Descripciones de puestos',
                'Perfiles y requisitos',
                'Relaciones organizacionales'
            ]
        })