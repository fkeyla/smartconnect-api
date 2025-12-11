from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .views import (
    api_info,
    DepartamentoViewSet,
    RolViewSet,
    PerfilUsuarioViewSet,
    SensorViewSet,
    EventoViewSet,
    BarreraViewSet
)

# Configurar el router de DRF
router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'usuarios', PerfilUsuarioViewSet, basename='usuario')
router.register(r'sensores', SensorViewSet, basename='sensor')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'barreras', BarreraViewSet, basename='barrera')

urlpatterns = [
    # Endpoint de información de la API
    path('info/', api_info, name='api_info'),
    
    # Autenticación JWT
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]
