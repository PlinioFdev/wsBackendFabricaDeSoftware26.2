from rest_framework import serializers

from .models import Estante, Livro


class EstanteSerializer(serializers.ModelSerializer):
    total_livros = serializers.IntegerField(source='livros.count', read_only=True)

    class Meta:
        model = Estante
        fields = ['id', 'nome', 'descricao', 'total_livros', 'criada_em']


class LivroSerializer(serializers.ModelSerializer):
    estante_nome = serializers.CharField(source='estante.nome', read_only=True)

    class Meta:
        model = Livro
        fields = [
            'id',
            'titulo',
            'autor',
            'ano',
            'isbn',
            'capa_url',
            'estante',
            'estante_nome',
            'criado_em',
        ]
