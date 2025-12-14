from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Departamento, Rol, PerfilUsuario, Sensor, Evento, Barrera
from .serializers import (
    DepartamentoSerializer,
    RolSerializer,
    PerfilUsuarioSerializer,
    SensorSerializer,
    EventoSerializer,
    EventoCreateSerializer,
    BarreraSerializer,
    BarreraEstadoSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOnly, IsOwnerOrAdmin


# Vista personalizada para login con mensajes en español
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([AllowAny])  # Endpoint público
def api_info(request):
    """Endpoint de información de la API (público, no requiere autenticación)"""
    return Response({
        "autor": ["Keyla"],
        "asignatura": "Programación Back End",
        "proyecto": "SmartConnect API",
        "descripcion": "API para gestión de sensores RFID y control de accesos.",
        "version": "1.0"
    })


class DepartamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Departamentos
    
    - Admin: CRUD completo
    - Operador: Solo lectura
    """
    queryset = Departamento.objects.all().order_by('nombre')
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion']


class RolViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Roles
    
    - Solo Admin puede crear, modificar o eliminar roles
    - GET permite ver los roles disponibles
    """
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Perfiles de Usuario
    
    - Admin: Puede crear y gestionar perfiles
    - Operador: Solo puede ver perfiles
    """
    queryset = PerfilUsuario.objects.all().select_related('user', 'rol')
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['rol']
    search_fields = ['user__username', 'user__email']
    
    def perform_create(self, serializer):
        """Crear un nuevo perfil de usuario"""
        serializer.save()


class SensorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Sensores RFID
    
    - Admin: CRUD completo
    - Operador: Solo lectura
    - Permite filtrar por departamento y estado
    """
    queryset = Sensor.objects.all().select_related('departamento', 'usuario_asociado').order_by('-fecha_creacion')
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'departamento', 'usuario_asociado']
    search_fields = ['uid', 'departamento__nombre']
    ordering_fields = ['fecha_creacion', 'uid', 'estado']
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOnly])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint para cambiar el estado de un sensor
        PATCH /api/sensores/{id}/cambiar_estado/
        Body: {"estado": "activo"|"inactivo"|"bloqueado"|"perdido"}
        """
        sensor = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {"error": "El campo 'estado' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estados_validos = [choice[0] for choice in Sensor.ESTADO_CHOICES]
        if nuevo_estado not in estados_validos:
            return Response(
                {"error": f"Estado inválido. Opciones: {estados_validos}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sensor.estado = nuevo_estado
        sensor.save()
        
        serializer = self.get_serializer(sensor)
        return Response(serializer.data)


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Eventos de acceso
    
    - GET: Usa EventoSerializer (con datos anidados del sensor)
    - POST: Usa EventoCreateSerializer (validación estricta)
    - Admin: CRUD completo
    - Operador: Solo lectura
    """
    queryset = Evento.objects.all().select_related('sensor', 'sensor__departamento').order_by('-fecha')
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_evento', 'resultado', 'sensor', 'sensor__departamento']
    ordering_fields = ['fecha']
    
    def get_serializer_class(self):
        """Usar serializer diferente según la acción"""
        if self.action == 'create':
            return EventoCreateSerializer
        return EventoSerializer
    
    def perform_create(self, serializer):
        """Crear un nuevo evento con validaciones"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """
        Obtener los últimos 10 eventos
        GET /api/eventos/recientes/
        """
        eventos = self.queryset[:10]
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_sensor(self, request):
        """
        Obtener eventos de un sensor específico
        GET /api/eventos/por_sensor/?sensor_id=1
        """
        sensor_id = request.query_params.get('sensor_id')
        if not sensor_id:
            return Response(
                {"error": "El parámetro 'sensor_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eventos = self.queryset.filter(sensor_id=sensor_id)
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)


class BarreraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Barreras de acceso
    
    - Admin: CRUD completo
    - Operador: Solo lectura
    - Incluye endpoint especial para cambiar estado
    """
    queryset = Barrera.objects.all().select_related('departamento').order_by('nombre')
    serializer_class = BarreraSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['estado', 'departamento']
    search_fields = ['nombre']
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOnly])
    def estado(self, request, pk=None):
        """
        Endpoint para cambiar solo el estado de una barrera
        PATCH /api/barreras/{id}/estado/
        Body: {"estado": "abierta"|"cerrada"}
        """
        barrera = self.get_object()
        serializer = BarreraEstadoSerializer(barrera, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def abiertas(self, request):
        """
        Obtener todas las barreras abiertas
        GET /api/barreras/abiertas/
        """
        barreras = self.queryset.filter(estado=Barrera.ABIERTA)
        serializer = self.get_serializer(barreras, many=True)
        return Response(serializer.data)


# ============================================
# HANDLERS PERSONALIZADOS DE ERRORES HTTP
# ============================================

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def error_404(request, exception=None):
    """
    Handler personalizado para rutas no encontradas (404)
    Maneja todos los métodos HTTP y devuelve una respuesta JSON consistente
    """
    return Response({
        "error": "Recurso no encontrado",
        "detail": "La ruta solicitada no existe en la API",
        "status_code": 404,
        "path": request.path
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def error_500(request):
    """
    Handler personalizado para errores internos del servidor (500)
    Captura errores inesperados y devuelve respuesta JSON
    """
    return Response({
        "error": "Error interno del servidor",
        "detail": "Ha ocurrido un error inesperado. Por favor contacte al administrador.",
        "status_code": 500
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
