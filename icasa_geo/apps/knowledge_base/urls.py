"""
URLs para Knowledge Base
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, DocumentTemplateViewSet, DocumentViewSet

app_name = 'knowledge_base'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'templates', DocumentTemplateViewSet)
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]