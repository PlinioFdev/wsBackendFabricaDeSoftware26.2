from rest_framework import viewsets

from .models import Estante, Livro
from .serializers import EstanteSerializer, LivroSerializer
from .services import buscar_dados_do_livro

CAMPOS_PREENCHIDOS_PELA_API = ['autor', 'ano', 'isbn', 'capa_url']


class EstanteViewSet(viewsets.ModelViewSet):
    """CRUD completo de estantes."""

    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class LivroViewSet(viewsets.ModelViewSet):
    """CRUD completo de livros, com dados vindos da Open Library."""

    queryset = Livro.objects.select_related('estante')
    serializer_class = LivroSerializer

    def perform_create(self, serializer):
        """Completa com a Open Library os campos que o usuario nao enviou."""
        dados = buscar_dados_do_livro(serializer.validated_data['titulo'])

        complemento = {}
        if dados:
            for campo in CAMPOS_PREENCHIDOS_PELA_API:
                if not serializer.validated_data.get(campo) and dados.get(campo):
                    complemento[campo] = dados[campo]

        serializer.save(**complemento)
