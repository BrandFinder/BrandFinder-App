from django import forms
from django.forms import ValidationError

COLOR_CHOICES = [
    ('default', 'Seleccione un color'),
    ('negro', 'Negro'),
    ('blanco','Blanco'),
    ('rojo', 'Rojo'),
    ('verde', 'Verde'),
    ('azul', 'Azul'),
    ('amarillo', 'Amarillo'),
    ('magenta', 'Magenta'),
    ('cian', 'Cian')
]
class SearchBrandForm(forms.Form):
    image = forms.ImageField(label='Suba una imagen', required=True)
    color = forms.ChoiceField(choices=COLOR_CHOICES, label='Seleccione un color', required=True)