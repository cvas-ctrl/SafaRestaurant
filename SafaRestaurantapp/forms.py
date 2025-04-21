from django import forms
from .models import Camarero

class CamareroForm(forms.ModelForm):
    class Meta:
        model = Camarero
        fields = ['nombre', 'apellidos', 'dni', 'email', 'fecha_nacimiento']