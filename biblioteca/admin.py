from django.contrib import admin

from .models import Estante, Livro


@admin.register(Estante)
class EstanteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'criada_em']
    search_fields = ['nome']


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'ano', 'estante']
    list_filter = ['estante']
    search_fields = ['titulo', 'autor', 'isbn']
