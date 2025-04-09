from django.db import models

# Create your models here.

class Camarero(models.Model):
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    dni = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return self.nombre

class Hamburguesa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    ingredientes = models.ManyToManyField('Ingrediente', blank=True)

    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    es_predeterminado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cocinero(models.Model):
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    dni = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return self.nombre

class TipoCocinero(models.TextChoices):
    ASADOR = 'ASADOR', 'Asador'
    FREIDOR = 'FREIDOR', 'Freidor'
    PLANCHA = 'PLANCHA', 'Plancha'
    GENERAL = 'GENERAL', 'General'

class TareaCocina(models.Model):
    codigo = models.CharField(max_length=15)

    tipo = models.CharField(
        max_length=50,
        choices=TipoCocinero.choices,
        default=TipoCocinero.GENERAL
    )

    cocinero = models.ForeignKey(
        'Cocinero',
        on_delete=models.DO_NOTHING,
        related_name='tareas'
    )


