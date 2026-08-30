from django.test import TestCase

from biblioteca.models import Estante, Livro


class EstanteTests(TestCase):
    def test_str_mostra_o_nome(self):
        estante = Estante.objects.create(nome='Fantasia')
        self.assertEqual(str(estante), 'Fantasia')


class LivroTests(TestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')

    def test_str_mostra_o_titulo(self):
        livro = Livro.objects.create(estante=self.estante, titulo='The Hobbit')
        self.assertEqual(str(livro), 'The Hobbit')

    def test_livro_acessivel_pela_estante(self):
        Livro.objects.create(estante=self.estante, titulo='The Hobbit')
        self.assertEqual(self.estante.livros.count(), 1)

    def test_apagar_estante_apaga_os_livros(self):
        Livro.objects.create(estante=self.estante, titulo='The Hobbit')
        self.estante.delete()
        self.assertEqual(Livro.objects.count(), 0)
