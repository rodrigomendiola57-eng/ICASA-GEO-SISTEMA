"""
Configuración de Celery para ICASA-GEO
"""
import os
from celery import Celery

# Establecer el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.development')

app = Celery('icasa_geo')

# Usar configuración de Django para Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todas las apps instaladas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')