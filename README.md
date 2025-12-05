# ICASA-GEO: Sistema de Gestión Estratégica Organizacional

## Descripción
ICASA-GEO es un sistema web centralizado para la gestión del Manual de Organización de ICASA, que digitaliza la creación, gestión, visualización y mantenimiento de la estructura orgánica, funciones y procesos organizacionales.

## Características Principales
- **Base de Conocimiento**: Editor WYSIWYG para documentación organizacional
- **Modelado Organizacional**: Herramientas de diagramación para organigramas y flujogramas
- **Gestión de Puestos**: Sistema completo de descripciones de puestos y roles
- **Flujo de Aprobación**: Workflow formal para revisión y aprobación de cambios
- **Control de Versiones**: Historial completo de cambios y revisiones

## Tecnologías
- **Backend**: Django 4.2 + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Editor**: CKEditor para contenido enriquecido
- **Estructura Jerárquica**: django-mptt

## Estructura del Proyecto
```
icasa_geo/
├── manage.py
├── requirements.txt
├── icasa_geo/
│   ├── settings/          # Configuraciones por ambiente
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/              # Funcionalidades base
│   ├── knowledge_base/    # Módulo de documentación
│   ├── organizational/    # Módulo de diagramación
│   └── positions/         # Módulo de puestos
├── static/
├── media/
└── templates/
```

## Instalación y Configuración

### 1. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
copy .env.example .env
# Editar .env con tus configuraciones
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## Módulos del Sistema

### Core (apps.core)
- Modelos base con auditoría y versionado
- Sistema de permisos personalizado
- Utilidades compartidas

### Knowledge Base (apps.knowledge_base)
- Editor de contenido enriquecido
- Estructura jerárquica de documentos
- Control de versiones de contenido

### Organizational (apps.organizational)
- Creación de organigramas
- Modelado de procesos (BPMN)
- Vinculación con puestos de trabajo

### Positions (apps.positions)
- Gestión de descripciones de puestos
- Perfiles y requisitos
- Relaciones organizacionales

## Desarrollo

### Comandos útiles
```bash
# Ejecutar tests
python manage.py test

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar Celery (en desarrollo)
celery -A icasa_geo worker --loglevel=info
```

### Estructura de Apps
Cada aplicación sigue la estructura estándar de Django:
- `models.py`: Modelos de datos
- `views.py`: Vistas y ViewSets de API
- `serializers.py`: Serializers para API REST
- `urls.py`: Configuración de URLs
- `admin.py`: Configuración del panel de administración
- `tests.py`: Tests unitarios

## Contribución
1. Fork del proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia
Proyecto propietario de ICASA - Todos los derechos reservados

## Contacto
Equipo de Desarrollo ICASA
Email: desarrollo@icasa.com