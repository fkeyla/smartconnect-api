from rest_framework import permissions
from .models import PerfilUsuario, Rol


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - Admin: CRUD completo (GET, POST, PUT, PATCH, DELETE)
    - Operador: Solo lectura (GET, HEAD, OPTIONS)
    - No autenticados: Denegado
    """
    
    def has_permission(self, request, view):
        # Debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Si es método de solo lectura (GET, HEAD, OPTIONS), permitir
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos de escritura, verificar si es Admin
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
            return perfil.rol.nombre == Rol.ADMIN
        except PerfilUsuario.DoesNotExist:
            return False


class IsAdminOnly(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios con rol Admin
    """
    
    def has_permission(self, request, view):
        # Debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si es Admin
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
            return perfil.rol.nombre == Rol.ADMIN
        except PerfilUsuario.DoesNotExist:
            return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que permite:
    - Admin: acceso completo
    - Usuario propietario: acceso a sus propios datos
    """
    
    def has_object_permission(self, request, view, obj):
        # Debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Si es método de solo lectura, permitir
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si es Admin
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
            if perfil.rol.nombre == Rol.ADMIN:
                return True
        except PerfilUsuario.DoesNotExist:
            pass
        
        # Verificar si es el propietario (para PerfilUsuario)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
