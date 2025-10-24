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
    data_devolucao = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Movimento
        fields = ['material', 'tipo', 'quantidade', 'nota', 'data_devolucao']
        widgets = {
            'nota': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        data_dev = cleaned.get('data_devolucao')
        if tipo == 'EMPRESTIMO' and not data_dev:
            raise forms.ValidationError('Para Empréstimo é necessário informar a data prevista de devolução.')
        return cleaned
