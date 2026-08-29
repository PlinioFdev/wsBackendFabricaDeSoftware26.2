from rest_framework import viewsets

from .models import Estante
from .serializers import EstanteSerializer


class EstanteViewSet(viewsets.ModelViewSet):
    """CRUD completo de estantes."""

    queryset = Estante.objects.all()
    serializer_class = EstanteSerializer
