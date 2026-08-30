from rest_framework import viewsets

from .models import Estante, Livro
from .serializers import EstanteSerializer, LivroSerializer
from .services import CAMPOS_COMPLETADOS, completar_campos_vazios


class EstanteViewSet(viewsets.ModelViewSet):
    """CRUD completo de estantes."""

    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class LivroViewSet(viewsets.ModelViewSet):
    """CRUD completo de livros, com dados vindos da Open Library."""

    queryset = Livro.objects.select_related('estante')
    serializer_class = LivroSerializer
    aviso = ''

    def perform_create(self, serializer):
        """Completa com a Open Library os campos que o usuario nao enviou.

        Se a API externa falhar, o livro e salvo mesmo assim e a resposta
        leva um aviso explicando o que aconteceu.
        """
        livro = Livro(**serializer.validated_data)
        self.aviso = completar_campos_vazios(livro)

        serializer.save(**{campo: getattr(livro, campo) for campo in CAMPOS_COMPLETADOS})

    def create(self, request, *args, **kwargs):
        resposta = super().create(request, *args, **kwargs)
        if self.aviso:
            resposta.data['aviso'] = self.aviso
        return resposta
