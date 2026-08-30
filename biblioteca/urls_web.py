from django.urls import path

from .views_web import cadastrar_livro, pagina_inicial

urlpatterns = [
    path('', pagina_inicial, name='pagina_inicial'),
    path('livros/novo/', cadastrar_livro, name='cadastrar_livro'),
]
