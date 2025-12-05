from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Notification
from .notifications import NotificationService

@login_required
def notifications_list(request):
    """Vista para listar todas las notificaciones del usuario"""
    notifications = NotificationService.get_user_notifications(request.user, limit=50)
    unread_count = NotificationService.get_unread_count(request.user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/list.html', context)

@login_required
def notifications_unread(request):
    """Vista para listar solo notificaciones no leídas"""
    notifications = NotificationService.get_user_notifications(request.user, unread_only=True, limit=20)
    
    context = {
        'notifications': notifications,
        'unread_only': True,
    }
    return render(request, 'notifications/list.html', context)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Marcar una notificación como leída"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    return JsonResponse({'success': True, 'message': 'Notificación marcada como leída'})

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Marcar todas las notificaciones como leídas"""
    NotificationService.mark_all_as_read(request.user)
    
    return JsonResponse({'success': True, 'message': 'Todas las notificaciones marcadas como leídas'})

@login_required
def notifications_api(request):
    """API para obtener notificaciones (para actualizaciones en tiempo real)"""
    unread_notifications = NotificationService.get_user_notifications(
        request.user, 
        unread_only=True, 
        limit=10
    )
    
    notifications_data = []
    for notification in unread_notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'priority_class': notification.get_priority_class(),
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': len(notifications_data),
    })

@login_required
def notification_preferences(request):
    """Vista para gestionar preferencias de notificaciones"""
    from .models import NotificationPreference
    
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Actualizar preferencias
        for field in ['email_document_created', 'email_document_approved', 'email_document_rejected', 
                     'email_document_review', 'web_document_created', 'web_document_approved', 
                     'web_document_rejected', 'web_document_review']:
            setattr(preferences, field, field in request.POST)
        
        preferences.save()
        messages.success(request, 'Preferencias de notificación actualizadas')
    
    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)