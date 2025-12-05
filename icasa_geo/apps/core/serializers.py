"""
Serializers base para ICASA-GEO
"""
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuarios"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class BaseModelSerializer(serializers.ModelSerializer):
    """Serializer base con campos de auditoría"""
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta:
        fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']