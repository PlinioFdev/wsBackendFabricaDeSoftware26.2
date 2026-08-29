from rest_framework import viewsets

from .models import Estante, Livro
from .serializers import EstanteSerializer, LivroSerializer


class EstanteViewSet(viewsets.ModelViewSet):
    """CRUD completo de estantes."""

    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer


class LivroViewSet(viewsets.ModelViewSet):
    """CRUD completo de livros."""

    queryset = Livro.objects.select_related('estante')
    serializer_class = LivroSerializer
