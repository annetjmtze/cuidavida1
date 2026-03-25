from django.db import models
from django.contrib.auth.models import User

# 🔹 Perfil para definir tipo de usuario
class Perfil(models.Model):
    TIPOS = (
        ('paciente', 'Paciente'),
        ('medico', 'Medico'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"


# 🔹 Datos del paciente
class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre
    
# 🔹 Datos del médico
class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre