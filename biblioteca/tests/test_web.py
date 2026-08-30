from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from biblioteca.models import Estante, Livro

RESPOSTA_OK = {
    'docs': [{'author_name': ['Ursula K. Le Guin'], 'first_publish_year': 1968}]
}


class PaginaInicialTests(TestCase):
    def test_abre_sem_login(self):
        resposta = self.client.get(reverse('pagina_inicial'))
        self.assertEqual(resposta.status_code, 200)

    def test_mostra_os_livros_cadastrados(self):
        estante = Estante.objects.create(nome='Fantasia')
        Livro.objects.create(estante=estante, titulo='The Hobbit')

        resposta = self.client.get(reverse('pagina_inicial'))

        self.assertContains(resposta, 'Fantasia')
        self.assertContains(resposta, 'The Hobbit')


class CadastrarLivroTests(TestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')
        User.objects.create_user('plinio', password='senha-de-teste')

    def test_sem_login_manda_para_a_tela_de_entrada(self):
        resposta = self.client.get(reverse('cadastrar_livro'))

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('login'), resposta.url)

    def test_com_login_abre_o_formulario(self):
        self.client.login(username='plinio', password='senha-de-teste')

        resposta = self.client.get(reverse('cadastrar_livro'))

        self.assertEqual(resposta.status_code, 200)

    @patch('biblioteca.services.requests.get')
    def test_formulario_cadastra_e_completa_pela_open_library(self, get):
        get.return_value = Mock(status_code=200, json=Mock(return_value=RESPOSTA_OK))
        self.client.login(username='plinio', password='senha-de-teste')

        self.client.post(
            reverse('cadastrar_livro'),
            {'titulo': 'A Wizard of Earthsea', 'estante': self.estante.id},
        )

        livro = Livro.objects.get(titulo='A Wizard of Earthsea')
        self.assertEqual(livro.autor, 'Ursula K. Le Guin')
        self.assertEqual(livro.ano, 1968)
