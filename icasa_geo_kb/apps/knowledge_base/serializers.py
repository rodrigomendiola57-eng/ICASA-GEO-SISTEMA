from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Category, Document

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'is_active', 'children']
    
    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategorySerializer(children, many=True).data

class DocumentSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'category', 'content', 'summary', 'tags',
            'document_code', 'effective_date', 'version', 'status', 'status_display',
            'is_public', 'created_at', 'updated_at'
        ]