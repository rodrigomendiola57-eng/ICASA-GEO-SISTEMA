"""
Tests para Knowledge Base
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, DocumentTemplate, Document

class CategoryModelTest(TestCase):
    """Tests para el modelo Category"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.root_category = Category.objects.create(
            name='Políticas',
            created_by=self.user
        )
        
        self.child_category = Category.objects.create(
            name='Recursos Humanos',
            parent=self.root_category,
            created_by=self.user
        )
    
    def test_category_creation(self):
        """Test creación de categoría"""
        self.assertEqual(self.root_category.name, 'Políticas')
        self.assertEqual(self.root_category.slug, 'politicas')
        self.assertTrue(self.root_category.is_active)
    
    def test_category_hierarchy(self):
        """Test jerarquía de categorías"""
        self.assertEqual(self.child_category.parent, self.root_category)
        self.assertIn(self.child_category, self.root_category.get_children())
    
    def test_breadcrumb_generation(self):
        """Test generación de breadcrumb"""
        breadcrumb = self.child_category.breadcrumb
        self.assertEqual(len(breadcrumb), 2)
        self.assertEqual(breadcrumb[0], self.root_category)
        self.assertEqual(breadcrumb[1], self.child_category)

class DocumentModelTest(TestCase):
    """Tests para el modelo Document"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Políticas',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Política de Vacaciones',
            document_code='POL-001',
            category=self.category,
            content='Contenido de la política...',
            created_by=self.user
        )
    
    def test_document_creation(self):
        """Test creación de documento"""
        self.assertEqual(self.document.title, 'Política de Vacaciones')
        self.assertEqual(self.document.document_code, 'POL-001')
        self.assertEqual(self.document.status, 'draft')
        self.assertEqual(self.document.version, 1)
        self.assertTrue(self.document.is_current)
    
    def test_document_approval_workflow(self):
        """Test flujo de aprobación"""
        # Inicialmente en borrador
        self.assertEqual(self.document.status, 'draft')
        
        # Aprobar documento
        self.document.approve(self.user)
        
        self.assertEqual(self.document.status, 'approved')
        self.assertEqual(self.document.approved_by, self.user)
        self.assertIsNotNone(self.document.approved_at)
    
    def test_document_rejection(self):
        """Test rechazo de documento"""
        self.document.status = 'review'
        self.document.save()
        
        self.document.reject(self.user, "Necesita más detalles")
        
        self.assertEqual(self.document.status, 'rejected')
        self.assertEqual(self.document.rejection_reason, "Necesita más detalles")
    
    def test_variable_rendering(self):
        """Test renderizado de variables"""
        self.document.content = "Documento de {{company_name}} versión {{version}}"
        self.document.save()
        
        rendered = self.document.render_content_with_variables()
        
        self.assertIn('ICASA', rendered)
        self.assertIn('v1', rendered)

class CategoryAPITest(APITestCase):
    """Tests para la API de categorías"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Políticas',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_category_list(self):
        """Test listado de categorías"""
        url = reverse('knowledge_base:category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_category_tree(self):
        """Test árbol de categorías"""
        url = reverse('knowledge_base:category-tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

class DocumentAPITest(APITestCase):
    """Tests para la API de documentos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Políticas',
            created_by=self.user
        )
        
        self.document = Document.objects.create(
            title='Política de Vacaciones',
            document_code='POL-001',
            category=self.category,
            content='Contenido de la política...',
            status='approved',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_document_list(self):
        """Test listado de documentos"""
        url = reverse('knowledge_base:document-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_document_detail(self):
        """Test detalle de documento"""
        url = reverse('knowledge_base:document-detail', kwargs={'slug': self.document.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Política de Vacaciones')
    
    def test_document_search(self):
        """Test búsqueda de documentos"""
        url = reverse('knowledge_base:document-list')
        response = self.client.get(url, {'search': 'vacaciones'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_document_creation(self):
        """Test creación de documento"""
        url = reverse('knowledge_base:document-list')
        data = {
            'title': 'Nueva Política',
            'document_code': 'POL-002',
            'category': self.category.id,
            'content': 'Contenido de la nueva política...',
            'summary': 'Resumen de la política'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 2)