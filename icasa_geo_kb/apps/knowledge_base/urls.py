from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, DocumentViewSet,
    knowledge_base_dashboard, category_detail, document_detail, document_create, document_edit,
    search_documents, search_suggestions, advanced_search, categories_management, category_create_ajax, category_templates
)

app_name = 'knowledge_base'

router = DefaultRouter()
router.register(r'api/categories', CategoryViewSet)
router.register(r'api/documents', DocumentViewSet)

urlpatterns = [
    # Web views
    path('', knowledge_base_dashboard, name='dashboard'),
    path('categorias/', knowledge_base_dashboard, name='categories'),
    path('documentos/', knowledge_base_dashboard, name='documents'),
    path('search/', search_documents, name='search'),
    path('search/advanced/', advanced_search, name='advanced_search'),
    path('search/suggestions/', search_suggestions, name='search_suggestions'),
    path('categories/manage/', categories_management, name='categories_management'),
    path('categories/create/', category_create_ajax, name='category_create_ajax'),
    path('category/<slug:slug>/', category_detail, name='category_detail'),
    path('category/<slug:slug>/templates/', category_templates, name='category_templates'),
    path('create/', document_create, name='document_create'),
    path('edit/<slug:slug>/', document_edit, name='document_edit'),
    path('document/<slug:slug>/', document_detail, name='document_detail'),
    
    # API endpoints
    path('', include(router.urls)),
]