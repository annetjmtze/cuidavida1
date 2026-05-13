from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

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
    medico_asignado = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True, blank=True, related_name='pacientes')
    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    edad = models.IntegerField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    # Campos adicionales para el Wizard
    curp = models.CharField(max_length=18, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=20, blank=True, null=True)
    tipo_sangre = models.CharField(max_length=5, blank=True, null=True)
    enfermedades = models.TextField(blank=True, null=True)
    antecedentes = models.TextField(blank=True, null=True)
    medicamentos = models.TextField(blank=True, null=True)
    cp = models.CharField(max_length=5, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.CharField(max_length=100, blank=True, null=True)
    num_seguro = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre
    
# 🔹 Datos del médico
class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    cedula = models.CharField(max_length=12, blank=True, null=True)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    # Nuevos campos de dirección para el médico
    cp = models.CharField(max_length=5, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre
#NECESITAMOS CREAR UNA TABLA EN LA BASE DE DATOS DONDE SE LAMECENE ESTOS DATOS 
# 🔹 Modelo para Base de Datos de SEPOMEX (México)
class CodigoPostal(models.Model):
    codigo = models.CharField(max_length=5)
    asentamiento = models.CharField(max_length=100) # Colonia
    tipo_asentamiento = models.CharField(max_length=50)
    municipio = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

# 🔹 Modelo para Recetas
class Receta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='recetas')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    medicamentos = models.TextField()
    indicaciones = models.TextField()

    def __str__(self):
        return f"Receta para {self.paciente.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

# 🔹 Modelo para Citas Médicas
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='citas_medico')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField(blank=True, null=True)
    estatus = models.CharField(max_length=20, default='pendiente') # pendiente, confirmada, cancelada

    def __str__(self):
        return f"Cita: {self.paciente.nombre} con Dr. {self.medico.nombre} el {self.fecha}"

class ContactoEmergencia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='contactos_emergencia')
    nombre = models.CharField(max_length=100)
    relacion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre} ({self.relacion}) - {self.paciente.nombre}"
