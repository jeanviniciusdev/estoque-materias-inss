
from django import forms
from .models import Material, Movimento

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nome', 'descricao', 'quantidade', 'minimo', 'imagem']
        labels = {
            'minimo': 'Quantidade ideal'
        }
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }

class MovimentoForm(forms.ModelForm):
    class Meta:
        model = Movimento
        fields = ['material', 'tipo', 'quantidade', 'nota']
