from django.db import models


class Estante(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Livro(models.Model):
    estante = models.ForeignKey(
        Estante,
        on_delete=models.CASCADE,
        related_name='livros',
    )
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200, blank=True)
    ano = models.PositiveIntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    capa_url = models.URLField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo
