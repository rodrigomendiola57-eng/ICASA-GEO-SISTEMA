"""
Configuración SQLite para desarrollo rápido
"""
from .development import *

# Usar SQLite en lugar de PostgreSQL para desarrollo rápido
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Desactivar Celery para desarrollo simple
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True