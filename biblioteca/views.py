from rest_framework import viewsets

from .models import Estante, Livro
from .serializers import EstanteSerializer, LivroSerializer
from .services import ErroNaApiExterna, buscar_dados_do_livro

CAMPOS_PREENCHIDOS_PELA_API = ['autor', 'ano', 'isbn', 'capa_url']


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
        try:
            dados = buscar_dados_do_livro(serializer.validated_data['titulo'])
        except ErroNaApiExterna as erro:
            self.aviso = str(erro)
            dados = None
        else:
            if dados is None:
                self.aviso = 'Nenhum livro com esse titulo foi encontrado na Open Library.'

        complemento = {}
        if dados:
            for campo in CAMPOS_PREENCHIDOS_PELA_API:
                if not serializer.validated_data.get(campo) and dados.get(campo):
                    complemento[campo] = dados[campo]

        serializer.save(**complemento)

    def create(self, request, *args, **kwargs):
        resposta = super().create(request, *args, **kwargs)
        if self.aviso:
            resposta.data['aviso'] = self.aviso
        return resposta
