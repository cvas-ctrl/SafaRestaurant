from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Camarero, Usuario, Mesa, Hamburguesa, Reserva, Articulo, Resena, Plato, Sugerencia


class CamareroForm(forms.ModelForm):
    class Meta:
        model = Camarero
        fields = ['nombre', 'apellidos', 'dni', 'email', 'fecha_nacimiento']


class MesaForm(forms.ModelForm):
   class Meta:
       model = Mesa
       fields = ['numero', 'estado', 'cliente', 'camarero']

class HamburguesaForm(forms.ModelForm):
   class Meta:
       model = Hamburguesa
       fields = ['nombre', 'descripcion', 'precio']

class ReservaForm(forms.ModelForm):
    fecha_reserva = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora_reserva = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    class Meta:
        model = Reserva
        fields = ['fecha_reserva', 'hora_reserva', 'numero_personas', 'estado']

    def clean_numero_personas(self):
        numero_personas = self.cleaned_data.get('numero_personas')
        if numero_personas is None:
            raise ValidationError("Este campo es obligatorio.")
        if not (1 <= numero_personas <= 20):
            raise ValidationError("El número de personas debe estar entre 1 y 20.")

        return numero_personas

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['titulo', 'contenido', 'estado']

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if len(titulo) == 0:
            raise ValidationError("Este campo es obligatorio.")
        elif len(titulo) < 5:
            raise ValidationError("Debe contener almenos 5 caracteres.")

        return titulo


class ResenaForm(forms.ModelForm):
    # Por defecto, ModelChoiceField se renderiza como un <select> (combo box)
    # Si quisieras filtrar los platos, lo harías en el __init__ de la vista.
    # Plato.objects.all() hará que aparezcan todos los platos disponibles.
    plato = forms.ModelChoiceField(queryset=Plato.objects.filter(disponible=True).order_by('nombre'),
                                   empty_label="Selecciona un plato",
                                   label="Plato a puntuar")
    # La puntuación se convierte automáticamente en un select por IntegerField con choices
    puntuacion = forms.ChoiceField(choices=Resena.PUNTUACION_CHOICES, label="Tu Puntuación (1-5 Estrellas)")

    class Meta:
        model = Resena
        fields = ['plato', 'puntuacion', 'comentario']
        # No incluyas 'cliente' aquí, lo asigna automáticamente la vista.
        # No incluyas 'fecha_creacion', es auto_now_add.
        widgets = {
            'comentario': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Escribe aquí tu comentario sobre el plato...'}),
        }

    # Validación a nivel de formulario (clean) para reglas adicionales
    def clean(self):
        cleaned_data = super().clean()

        # Aquí puedes añadir validaciones adicionales si es necesario.
        # Por ejemplo, si el comentario es obligatorio para puntuaciones bajas.
        puntuacion = cleaned_data.get('puntuacion')
        comentario = cleaned_data.get('comentario')

        if puntuacion and int(puntuacion) < 3 and not comentario:
            self.add_error('comentario',
                           "Para puntuaciones bajas (menos de 3 estrellas), el comentario es obligatorio.")

        return cleaned_data


class SugerenciaForm(forms.ModelForm):
    # Los ChoiceField se renderizan automáticamente como combo boxes (<select>)
    tipo = forms.ChoiceField(choices=Sugerencia.TIPO_CHOICES, label="Tipo de Sugerencia" )
    categoria = forms.ChoiceField(choices=Sugerencia.CATEGORIA_CHOICES, label="Categoría")
    prioridad = forms.ChoiceField(choices=Sugerencia.PRIORIDAD_CHOICES, label="Prioridad")

    class Meta:
        model = Sugerencia
        fields = ['tipo', 'categoria', 'prioridad', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe tu sugerencia en detalle...'}),
        }

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje')
        if not mensaje:
            raise forms.ValidationError("El mensaje de la sugerencia no puede estar vacío.")
        if len(mensaje) < 20:
            raise forms.ValidationError("El mensaje debe tener al menos 20 caracteres.")
        return mensaje

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        mensaje = cleaned_data.get('mensaje')

        # Ejemplo de validación cruzada: si el tipo es 'OTROS', el mensaje debe especificar
        if tipo == 'OTROS' and mensaje and 'especificar' not in mensaje.lower():
            self.add_error('mensaje', "Si el tipo es 'Otros', por favor, especifica más en tu mensaje.")

        return cleaned_data

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'rol', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo',
                'id': 'email'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de Usuario',
                'id': 'nombre'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña',
                'id': 'password'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': '----',
                'id': 'rol'
            }),
        }

    def save(self, commit=True):
        email = self.cleaned_data['email']
        nombre = self.cleaned_data['nombre']
        rol = self.cleaned_data['rol']
        password = self.cleaned_data['password']

        user = Usuario.objects.create_user(
            email=email,
            nombre=nombre,
            password=password,
            rol=rol
        )

        return user


class AccesoEmpleadoForm(forms.Form):
    ROLES = (
        ('admin', 'Administrador'),
        ('cocinero', 'Cocinero'),
        ('camarero', 'Camarero')
    )

    rol = forms.ChoiceField(choices=ROLES, widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'selectRol'
    }))

    pin = forms.CharField(max_length=6, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'PIN de Seguridad',
        'id': 'inputPIN'
    }))

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        pin = cleaned_data.get('pin')

        PINES = {
            'admin': '9999',
            'cocinero': '1234',
            'camarero': '5678'
        }

        if pin != PINES.get(rol):
            raise forms.ValidationError("PIN incorrecto para este rol")

        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")