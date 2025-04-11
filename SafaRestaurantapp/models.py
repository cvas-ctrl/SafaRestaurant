from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.

##################### CAMARERO

class Camarero(models.Model):
    nombre = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    dni = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return self.nombre

class AuditoriaCamarero(models.Model):
    nombre_completo = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    mensaje = models.CharField(max_length=400)

    def __str__(self):
        return f"Auditoría {self.id} - {self.nombre_completo}"

##################### PEDIDOS

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

class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    camarero = models.ForeignKey(Camarero, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    hamburguesa = models.ForeignKey(Hamburguesa, on_delete=models.CASCADE)
    ingredientes = models.ManyToManyField(Ingrediente, through='IngredienteDetalle')
    cantidad = models.PositiveIntegerField(default=1)

class IngredienteDetalle(models.Model):
    detalle = models.ForeignKey(DetallePedido, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

##################### COCINERO

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


