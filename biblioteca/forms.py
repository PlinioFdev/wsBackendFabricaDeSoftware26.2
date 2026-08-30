from django import forms

from .models import Livro


class LivroForm(forms.ModelForm):
    """Formulário da página web para cadastrar um livro.

    Só o título e a estante são obrigatórios: autor, ano, isbn e capa
    são completados pela Open Library quando ficam em branco.
    """

    class Meta:
        model = Livro
        fields = ['titulo', 'estante', 'autor', 'ano']
        labels = {
            'titulo': 'Título',
            'estante': 'Estante',
            'autor': 'Autor (opcional)',
            'ano': 'Ano (opcional)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'The Hobbit'}),
            'autor': forms.TextInput(attrs={'placeholder': 'deixe vazio para buscar'}),
            'ano': forms.NumberInput(attrs={'placeholder': 'deixe vazio para buscar'}),
        }
