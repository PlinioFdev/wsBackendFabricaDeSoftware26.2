"""Cria dados de exemplo para quem acabou de subir o projeto."""

from django.core.management.base import BaseCommand

from biblioteca.models import Estante, Livro
from biblioteca.services import completar_campos_vazios

ACERVO = [
    (
        'Fantasia',
        'Mundos inventados',
        ['The Hobbit', 'Dune', 'A Wizard of Earthsea', 'The Name of the Wind'],
    ),
    (
        'Literatura brasileira',
        'Clássicos nacionais',
        ['Dom Casmurro', 'Vidas Secas', 'Grande Sertão Veredas'],
    ),
]


class Command(BaseCommand):
    help = 'Cria estantes e livros de exemplo, buscando os dados na Open Library.'

    def handle(self, *args, **opcoes):
        if Livro.objects.exists():
            self.stdout.write('Já existem livros cadastrados. Nada foi criado.')
            return

        for nome, descricao, titulos in ACERVO:
            estante = Estante.objects.create(nome=nome, descricao=descricao)
            self.stdout.write(f'\nEstante "{estante.nome}":')

            for titulo in titulos:
                livro = Livro(estante=estante, titulo=titulo)
                aviso = completar_campos_vazios(livro)
                livro.save()

                if aviso:
                    self.stdout.write(self.style.WARNING(f'  {titulo} — {aviso}'))
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'  {titulo} — {livro.autor}, {livro.ano}')
                    )

        self.stdout.write(
            f'\n{Estante.objects.count()} estantes e {Livro.objects.count()} livros criados.'
        )
