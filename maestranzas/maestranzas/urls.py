from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Incluye las URLs de autenticación de Django
    path('', include('inventory.urls')),  # Asegúrate de que esta línea está presente
]
