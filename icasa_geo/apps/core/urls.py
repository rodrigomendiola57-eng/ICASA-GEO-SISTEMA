"""
URLs para la aplicación Core
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]