from django.urls import path
from .views import almacenero_view, responsable_almacen_view, analista_inventario_view, gerente_view, gerente_inventario_view, register, profile_view, dashboard, generate_report_view

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path('', dashboard, name='dashboard'),  # Ruta para la raíz
    path('almacenero/', almacenero_view, name='almacenero'),
    path('responsable/', responsable_almacen_view, name='responsable_almacen'),
    path('analista/', analista_inventario_view, name='analista_inventario'),
    path('gerente/', gerente_view, name='gerente'),
    path('gerente_inventario/', gerente_inventario_view, name='gerente_inventario'),
    path('generate_report/', generate_report_view, name='generate_report'),
]
