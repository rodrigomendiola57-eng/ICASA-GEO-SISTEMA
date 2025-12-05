from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationalViewSet

app_name = 'organizational'

router = DefaultRouter()
router.register(r'', OrganizationalViewSet, basename='organizational')

urlpatterns = [
    path('', include(router.urls)),
]