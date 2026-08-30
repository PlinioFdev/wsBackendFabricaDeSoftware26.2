from django import forms

from .models import Livro


class LivroForm(forms.ModelForm):
    """Formulario da pagina web para cadastrar um livro.

    Só o titulo e a estante sao obrigatorios: autor, ano, isbn e capa
    sao completados pela Open Library quando ficam em branco.
    """

    class Meta:
        model = Livro
        fields = ['titulo', 'estante', 'autor', 'ano']
        labels = {
            'titulo': 'Titulo',
            'estante': 'Estante',
            'autor': 'Autor (opcional)',
            'ano': 'Ano (opcional)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'The Hobbit'}),
            'autor': forms.TextInput(attrs={'placeholder': 'deixe vazio para buscar'}),
            'ano': forms.NumberInput(attrs={'placeholder': 'deixe vazio para buscar'}),
        }
