"""
Utilidades compartidas para ICASA-GEO
"""
import os
import uuid
from django.utils.text import slugify
from django.core.files.storage import default_storage

def generate_unique_filename(instance, filename):
    """
    Genera un nombre único para archivos subidos
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)

def create_slug(text, max_length=50):
    """
    Crea un slug único basado en el texto
    """
    base_slug = slugify(text)[:max_length]
    return base_slug

def validate_file_size(file, max_size_mb=10):
    """
    Valida el tamaño de un archivo
    """
    max_size = max_size_mb * 1024 * 1024  # Convertir a bytes
    if file.size > max_size:
        raise ValueError(f"El archivo no puede ser mayor a {max_size_mb}MB")
    return True

def get_file_extension(filename):
    """
    Obtiene la extensión de un archivo
    """
    return filename.split('.')[-1].lower() if '.' in filename else ''

class FileUploadHandler:
    """
    Manejador de subida de archivos
    """
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
    MAX_SIZE_MB = 10
    
    @classmethod
    def validate_file(cls, file):
        """Valida un archivo subido"""
        # Validar tamaño
        validate_file_size(file, cls.MAX_SIZE_MB)
        
        # Validar extensión
        ext = get_file_extension(file.name)
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(cls.ALLOWED_EXTENSIONS)}")
        
        return True
    
    @classmethod
    def save_file(cls, file, folder='documents'):
        """Guarda un archivo y retorna la ruta"""
        cls.validate_file(file)
        filename = generate_unique_filename(None, file.name)
        path = os.path.join(folder, filename)
        return default_storage.save(path, file)