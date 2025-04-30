from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import User, PermissionsMixin
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

##################### MESAS

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    dni = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class EstadoMesa(models.TextChoices):
    LIBRE = 'LIBRE', 'Libre'
    OCUPADA = 'OCUPADA', 'Ocupada'
    ESPERANDO_PEDIDO = 'ESPERANDO', 'Esperando Pedido'

class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoMesa.choices,
        default=EstadoMesa.LIBRE
    )
    cliente = models.ForeignKey('Cliente', null=True, blank=True, on_delete=models.SET_NULL)
    camarero = models.ForeignKey('Camarero', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Mesa {self.numero} - {self.get_estado_display()}"


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
    finalizado = models.BooleanField(default=False)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    def __str__(self):
        return f"Pedido #{self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    @property
    def precio_total(self):
        return sum(detalle.hamburguesa.precio * detalle.cantidad for detalle in self.detalles.all())

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

##################### CUENTA

class EstadoCuenta(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PAGADO = 'PAGADO', 'Pagado'

class Cuenta(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='cuenta')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoCuenta.choices,
        default=EstadoCuenta.PENDIENTE
    )
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Cuenta para el Pedido #{self.pedido.id}"

##################### USUARIOS

class UsuarioManager(BaseUserManager):

   def create_user(self, email, nombre, rol, password=None):
       if not email:
           raise ValueError("El usuario debe tener un email")
       email = self.normalize_email(email)
       usuario = self.model(email=email, nombre=nombre, rol=rol)
       usuario.set_password(password)
       usuario.save(using=self._db)
       return usuario

   def create_superuser(self, email, nombre, rol='admin', password=None):
       usuario = self.create_user(email, nombre, rol, password)
       usuario.is_superuser = True
       usuario.is_staff = True
       usuario.save(using=self._db)
       return usuario

class Usuario(AbstractBaseUser, PermissionsMixin):
   ROLES = (
       ('admin','Administrador'),
       ('cliente','Cliente'),
       ('cocinero','Cocinero'),
       ('camarero','Camarero')
   )

   email = models.EmailField(max_length=500, unique=True)
   nombre = models.CharField(max_length=250)
   rol = models.CharField(max_length=25, choices=ROLES)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)

   objects = UsuarioManager()

   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['nombre', 'rol']

   def __str__(self):
       return self.email + "-" + self.nombre + ":" + self.rol