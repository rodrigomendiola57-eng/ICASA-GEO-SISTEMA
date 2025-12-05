"""
WSGI config for ICASA-GEO project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icasa_geo.settings.production')

application = get_wsgi_application()