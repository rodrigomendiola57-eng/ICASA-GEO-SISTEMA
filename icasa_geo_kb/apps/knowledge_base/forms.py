from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Document, Category
from .templates import get_template_choices, get_template_content

class DocumentForm(forms.ModelForm):
    template_choice = forms.ChoiceField(
        choices=[('', 'Documento en blanco')] + get_template_choices(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'template-selector'}),
        label='Plantilla'
    )
    
    class Meta:
        model = Document
        fields = ['title', 'category', 'template_choice', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': CKEditorUploadingWidget(config_name='icasa_document'),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Separar con comas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template_choice'].widget.attrs.update({
            'onchange': 'loadTemplate(this.value)'
        })

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }