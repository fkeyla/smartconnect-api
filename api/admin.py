from django.contrib import admin
from .models import Departamento, Rol, PerfilUsuario, Sensor, Evento, Barrera


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion']
    search_fields = ['nombre']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'fecha_creacion']
    list_filter = ['rol']
    search_fields = ['user__username', 'user__email']


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['uid', 'estado', 'departamento', 'usuario_asociado', 'fecha_creacion']
    list_filter = ['estado', 'departamento']
    search_fields = ['uid', 'usuario_asociado__username']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'tipo_evento', 'resultado', 'fecha']
    list_filter = ['tipo_evento', 'resultado', 'fecha']
    search_fields = ['sensor__uid', 'descripcion']
    readonly_fields = ['fecha']
    date_hierarchy = 'fecha'


@admin.register(Barrera)
class BarreraAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'departamento', 'fecha_creacion']
    list_filter = ['estado', 'departamento']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
