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

