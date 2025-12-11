from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Departamento, Rol, PerfilUsuario, Sensor, Evento, Barrera


class DepartamentoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Departamento"""
    
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
    
    def validate_nombre(self, value):
        """Validación adicional para el nombre del departamento"""
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        return value


class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol"""
    nombre_display = serializers.CharField(source='get_nombre_display', read_only=True)
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'nombre_display', 'descripcion', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'nombre_display']


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para el modelo User de Django"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo PerfilUsuario con datos anidados del usuario"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    rol_nombre = serializers.CharField(source='rol.get_nombre_display', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        write_only=True
    )
    rol_id = serializers.PrimaryKeyRelatedField(
        source='rol',
        queryset=Rol.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'id',
            'username',
            'email',
            'rol_nombre',
            'user_id',
            'rol_id',
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'username', 'email', 'rol_nombre', 'fecha_creacion']
    
    def to_representation(self, instance):
        """Personaliza la representación de salida"""
        representation = super().to_representation(instance)
        representation['rol'] = {
            'id': instance.rol.id,
            'nombre': instance.rol.nombre,
            'nombre_display': instance.rol.get_nombre_display()
        }
        return representation


class SensorSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Sensor con información anidada"""
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario_asociado.username', read_only=True, allow_null=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Sensor
        fields = [
            'id',
            'uid',
            'estado',
            'estado_display',
            'departamento',
            'departamento_nombre',
            'usuario_asociado',
            'usuario_username',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'estado_display']
    
    def validate_uid(self, value):
        """Validación del UID del sensor"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El UID no puede estar vacío")
        return value.strip()
    
    def validate(self, data):
        """Validación a nivel de objeto"""
        if data.get('estado') == Sensor.PERDIDO and data.get('usuario_asociado'):
            raise serializers.ValidationError(
                "Un sensor perdido no puede tener usuario asociado"
            )
        return data


class SensorSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado del Sensor para usar en relaciones anidadas"""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Sensor
        fields = ['id', 'uid', 'estado', 'estado_display']
        read_only_fields = ['id', 'estado_display']


class EventoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Evento con datos anidados del sensor"""
    sensor_data = SensorSimpleSerializer(source='sensor', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    resultado_display = serializers.CharField(source='get_resultado_display', read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id',
            'sensor',
            'sensor_data',
            'tipo_evento',
            'tipo_evento_display',
            'resultado',
            'resultado_display',
            'fecha',
            'descripcion'
        ]
        read_only_fields = ['id', 'fecha', 'sensor_data', 'tipo_evento_display', 'resultado_display']
    
    def validate_sensor(self, value):
        """Validación del sensor"""
        if value.estado == Sensor.BLOQUEADO:
            raise serializers.ValidationError(
                "No se pueden registrar eventos para sensores bloqueados"
            )
        if value.estado == Sensor.PERDIDO:
            raise serializers.ValidationError(
                "No se pueden registrar eventos para sensores perdidos"
            )
        return value


class EventoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para la creación de eventos con validaciones estrictas"""
    
    class Meta:
        model = Evento
        fields = ['sensor', 'tipo_evento', 'resultado', 'descripcion']
    
    def validate_sensor(self, value):
        """Validación del sensor al crear evento"""
        if value.estado != Sensor.ACTIVO:
            raise serializers.ValidationError(
                f"El sensor está {value.get_estado_display()}. Solo se permiten eventos de sensores activos."
            )
        return value
    
    def create(self, validated_data):
        """Lógica personalizada de creación si es necesaria"""
        return super().create(validated_data)


class BarreraSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Barrera"""
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True, allow_null=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Barrera
        fields = [
            'id',
            'nombre',
            'estado',
            'estado_display',
            'departamento',
            'departamento_nombre',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'estado_display']
    
    def validate_nombre(self, value):
        """Validación adicional para el nombre de la barrera"""
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        return value


class BarreraEstadoSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar solo el estado de la barrera"""
    
    class Meta:
        model = Barrera
        fields = ['id', 'estado', 'estado_display']
        read_only_fields = ['id', 'estado_display']
    
    def update(self, instance, validated_data):
        """Actualiza solo el estado de la barrera"""
        instance.estado = validated_data.get('estado', instance.estado)
        instance.save()
        return instance
