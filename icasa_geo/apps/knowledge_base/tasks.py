"""
Tareas asíncronas para Knowledge Base
"""
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from .models import Document, DocumentRevision

@shared_task
def send_approval_notification(document_id, action):
    """
    Enviar notificación de aprobación/rechazo
    """
    try:
        document = Document.objects.get(id=document_id)
        
        # Obtener usuarios que deben ser notificados
        recipients = [document.created_by.email]
        
        if action == 'approved':
            subject = f'Documento Aprobado: {document.title}'
            message = f"""
            El documento "{document.title}" ({document.document_code}) ha sido aprobado.
            
            Aprobado por: {document.approved_by.get_full_name()}
            Fecha de aprobación: {document.approved_at.strftime('%d/%m/%Y %H:%M')}
            
            Puedes ver el documento en: {document.get_absolute_url()}
            """
        else:
            subject = f'Documento Rechazado: {document.title}'
            message = f"""
            El documento "{document.title}" ({document.document_code}) ha sido rechazado.
            
            Motivo: {document.rejection_reason}
            
            Por favor, revisa y corrige el documento antes de enviarlo nuevamente para revisión.
            """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        
        return f"Notificación enviada para documento {document_id}"
        
    except Document.DoesNotExist:
        return f"Documento {document_id} no encontrado"
    except Exception as e:
        return f"Error enviando notificación: {str(e)}"

@shared_task
def cleanup_old_revisions():
    """
    Limpiar revisiones antiguas de autoguardado
    """
    from datetime import datetime, timedelta
    
    # Eliminar autoguardados más antiguos a 30 días
    cutoff_date = datetime.now() - timedelta(days=30)
    
    deleted_count = DocumentRevision.objects.filter(
        is_auto_save=True,
        created_at__lt=cutoff_date
    ).delete()[0]
    
    return f"Eliminadas {deleted_count} revisiones antiguas"

@shared_task
def generate_document_report(user_id, date_from, date_to):
    """
    Generar reporte de actividad de documentos
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Aquí iría la lógica para generar el reporte
        # Por ahora, solo un placeholder
        
        return f"Reporte generado para {user.username}"
        
    except User.DoesNotExist:
        return f"Usuario {user_id} no encontrado"

@shared_task
def check_document_review_dates():
    """
    Verificar documentos que necesitan revisión
    """
    from datetime import datetime
    
    today = datetime.now().date()
    
    # Buscar documentos que necesitan revisión
    documents_to_review = Document.objects.filter(
        review_date__lte=today,
        status='approved'
    )
    
    notifications_sent = 0
    
    for document in documents_to_review:
        # Enviar notificación al creador del documento
        try:
            send_mail(
                f'Documento requiere revisión: {document.title}',
                f"""
                El documento "{document.title}" ({document.document_code}) 
                ha alcanzado su fecha de revisión programada ({document.review_date}).
                
                Por favor, revisa y actualiza el documento si es necesario.
                """,
                settings.DEFAULT_FROM_EMAIL,
                [document.created_by.email],
                fail_silently=False,
            )
            notifications_sent += 1
        except Exception as e:
            continue
    
    return f"Enviadas {notifications_sent} notificaciones de revisión"