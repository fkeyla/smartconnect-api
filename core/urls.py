from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Handlers personalizados para errores HTTP
handler404 = 'api.views.error_404'
handler500 = 'api.views.error_500'
