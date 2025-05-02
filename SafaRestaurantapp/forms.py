from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Camarero, Usuario


class CamareroForm(forms.ModelForm):
    class Meta:
        model = Camarero
        fields = ['nombre', 'apellidos', 'dni', 'email', 'fecha_nacimiento']

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
            })
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

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")