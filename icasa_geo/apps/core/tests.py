"""
Tests para la aplicación Core
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import TimeStampedModel, ApprovalWorkflowModel

class TestTimeStampedModel(TestCase):
    """Tests para el modelo TimeStampedModel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_timestamps_are_set(self):
        """Test que los timestamps se establecen correctamente"""
        # Este test se implementará cuando tengamos un modelo concreto
        pass

class TestApprovalWorkflowModel(TestCase):
    """Tests para el modelo ApprovalWorkflowModel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_approval_workflow(self):
        """Test del flujo de aprobación"""
        # Este test se implementará cuando tengamos un modelo concreto
        pass