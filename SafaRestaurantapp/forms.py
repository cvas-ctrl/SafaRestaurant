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

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")