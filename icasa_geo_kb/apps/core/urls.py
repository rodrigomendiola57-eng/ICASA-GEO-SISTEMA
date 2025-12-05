from django.urls import path
from .views import (
    notifications_list, notifications_unread, mark_notification_read,
    mark_all_notifications_read, notifications_api, notification_preferences
)

app_name = 'core'

urlpatterns = [
    path('notifications/', notifications_list, name='notifications_list'),
    path('notifications/unread/', notifications_unread, name='notifications_unread'),
    path('notifications/preferences/', notification_preferences, name='notification_preferences'),
    path('notifications/api/', notifications_api, name='notifications_api'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
]