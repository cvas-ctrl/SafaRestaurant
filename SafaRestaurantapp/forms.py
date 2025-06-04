from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Camarero, Usuario, Mesa, Hamburguesa, Resena


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

class ResenasForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['comentario', 'puntuacion']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Comentario',
                'id': 'comentario'
            }),
            'puntuacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Puntuacion',
                'id': 'puntuacion'
            }),



        }