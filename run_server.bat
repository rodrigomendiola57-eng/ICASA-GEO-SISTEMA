@echo off
echo Iniciando servidor ICASA-GEO...
cd /d "c:\Sistema GEO (Gestión Estratégica Organizacional)\icasa_geo_kb"

echo Aplicando migraciones...
python manage.py makemigrations
python manage.py migrate

echo Iniciando servidor de desarrollo...
python manage.py runserver 8000

pause