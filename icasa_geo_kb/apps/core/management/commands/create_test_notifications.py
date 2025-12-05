from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.notifications import NotificationService

class Command(BaseCommand):
    help = 'Crear notificaciones de prueba para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando notificaciones de prueba...')
        
        # Obtener usuarios
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No hay usuarios en el sistema'))
            return
        
        admin_user = users.first()
        
        # Crear notificaciones de prueba para cada usuario
        for user in users:
            # Notificación de bienvenida
            NotificationService.create_notification(
                recipient=user,
                notification_type='system_update',
                title='¡Bienvenido a ICASA-GEO!',
                message='El sistema de notificaciones está funcionando correctamente. Ahora recibirás actualizaciones importantes sobre documentos y actividades del sistema.',
                priority='medium'
            )
            
            # Notificación de documento creado (simulada)
            NotificationService.create_notification(
                recipient=user,
                sender=admin_user,
                notification_type='document_created',
                title='Nuevo documento: Política de Seguridad',
                message='Se ha creado un nuevo documento que requiere tu atención.',
                priority='high',
                action_url='/knowledge/'
            )
            
            # Notificación de revisión pendiente
            if user.groups.filter(name__in=['Gerentes', 'Revisores', 'Administradores ICASA']).exists():
                NotificationService.create_notification(
                    recipient=user,
                    sender=admin_user,
                    notification_type='document_review',
                    title='Documento pendiente de revisión',
                    message='Hay documentos esperando tu revisión y aprobación.',
                    priority='urgent',
                    action_url='/knowledge/'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Notificaciones de prueba creadas para {users.count()} usuarios')
        )