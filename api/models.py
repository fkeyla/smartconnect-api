from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


class Departamento(models.Model):
    """Modelo para representar departamentos o zonas en el sistema"""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(3, 'El nombre debe tener al menos 3 caracteres')]
    )
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """Modelo para definir roles de usuario en el sistema"""
    ADMIN = 'Admin'
    OPERADOR = 'Operador'
    
    ROLES_CHOICES = [
        (ADMIN, 'Administrador'),
        (OPERADOR, 'Operador'),
    ]
    
    nombre = models.CharField(
        max_length=20,
        choices=ROLES_CHOICES,
        unique=True
    )
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()


class PerfilUsuario(models.Model):
    """Extensión del modelo User de Django para agregar rol"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.user.username} - {self.rol}"


class Sensor(models.Model):
    """Modelo para representar sensores RFID en el sistema"""
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'
    BLOQUEADO = 'bloqueado'
    PERDIDO = 'perdido'
    
    ESTADO_CHOICES = [
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
        (BLOQUEADO, 'Bloqueado'),
        (PERDIDO, 'Perdido'),
    ]
    
    uid = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='UID/MAC del sensor',
        help_text='Identificador único del sensor RFID (ej: MAC o UID)'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ACTIVO
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='sensores'
    )
    usuario_asociado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sensores'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        ordering = ['-fecha_creacion']
    
    def clean(self):
        """Validación personalizada"""
        if self.estado == self.PERDIDO and self.usuario_asociado:
            raise ValidationError('Un sensor perdido no puede tener usuario asociado')
    
    def __str__(self):
        return f"Sensor {self.uid} - {self.get_estado_display()}"


class Evento(models.Model):
    """Modelo para registrar eventos de acceso del sistema"""
    ACCESO = 'acceso'
    MANUAL_ABIERTO = 'manual_abierto'
    MANUAL_CERRADO = 'manual_cerrado'
    
    TIPO_EVENTO_CHOICES = [
        (ACCESO, 'Acceso con sensor'),
        (MANUAL_ABIERTO, 'Apertura manual'),
        (MANUAL_CERRADO, 'Cierre manual'),
    ]
    
    PERMITIDO = 'permitido'
    DENEGADO = 'denegado'
    
    RESULTADO_CHOICES = [
        (PERMITIDO, 'Permitido'),
        (DENEGADO, 'Denegado'),
    ]
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        default=ACCESO
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES
    )
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['sensor', '-fecha']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.get_resultado_display()} ({self.fecha.strftime('%Y-%m-%d %H:%M')})"


class Barrera(models.Model):
    """Modelo para representar barreras de acceso"""
    ABIERTA = 'abierta'
    CERRADA = 'cerrada'
    
    ESTADO_CHOICES = [
        (ABIERTA, 'Abierta'),
        (CERRADA, 'Cerrada'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(3, 'El nombre debe tener al menos 3 caracteres')]
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=CERRADA
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='barreras',
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Barrera'
        verbose_name_plural = 'Barreras'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
