from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=100)
    max_capacity = models.IntegerField(default=100)  # Capacidad máxima

    class Meta:
        permissions = [
            ("can_manage_storage", "Can manage storage"),
            ("can_access_almacenero", "Can access almacenero view"),
            ("can_access_responsable_almacen", "Can access responsable almacen view"),
            ("can_access_analista_inventario", "Can access analista inventario view"),
            ("can_access_gerente", "Can access gerente view"),
            ("can_access_gerente_inventario", "Can access gerente inventario view"),
        ]

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    condition = models.CharField(max_length=50, choices=[('Nuevo', 'Nuevo'), ('Usado', 'Usado'), ('Reparado', 'Reparado')], default='Nuevo')

    def __str__(self):
        return self.name

class StorageCapacity(models.Model):
    limit = models.IntegerField(default=1000)  # Capacidad total del almacén

    def __str__(self):
        return f"Capacity Limit: {self.limit}"

class Alert(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alert at {self.location.name} by {self.created_by.username}"

