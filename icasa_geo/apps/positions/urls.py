from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionsViewSet

app_name = 'positions'

router = DefaultRouter()
router.register(r'', PositionsViewSet, basename='positions')

urlpatterns = [
    path('', include(router.urls)),
]