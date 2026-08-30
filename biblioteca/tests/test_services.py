from unittest.mock import Mock, patch

import requests
from django.test import TestCase

from biblioteca.models import Estante, Livro
from biblioteca.services import (
    ErroNaApiExterna,
    buscar_dados_do_livro,
    completar_campos_vazios,
)

RESPOSTA_OK = {
    'docs': [
        {
            'author_name': ['J.R.R. Tolkien'],
            'first_publish_year': 1937,
            'isbn': ['0261102214'],
            'cover_i': 42,
        }
    ]
}


def resposta_falsa(status=200, json_retorno=None):
    return Mock(status_code=status, json=Mock(return_value=json_retorno))


class BuscarDadosDoLivroTests(TestCase):
    @patch('biblioteca.services.requests.get')
    def test_devolve_os_campos_do_livro(self, get):
        get.return_value = resposta_falsa(json_retorno=RESPOSTA_OK)

        dados = buscar_dados_do_livro('The Hobbit')

        self.assertEqual(dados['autor'], 'J.R.R. Tolkien')
        self.assertEqual(dados['ano'], 1937)
        self.assertEqual(dados['isbn'], '0261102214')
        self.assertIn('covers.openlibrary.org', dados['capa_url'])

    @patch('biblioteca.services.requests.get')
    def test_devolve_none_quando_nao_encontra(self, get):
        get.return_value = resposta_falsa(json_retorno={'docs': []})

        self.assertIsNone(buscar_dados_do_livro('titulo inexistente'))

    @patch('biblioteca.services.requests.get')
    def test_ignora_ano_negativo(self, get):
        get.return_value = resposta_falsa(
            json_retorno={'docs': [{'first_publish_year': -750}]}
        )

        self.assertIsNone(buscar_dados_do_livro('Iliada')['ano'])

    @patch('biblioteca.services.requests.get', side_effect=requests.ConnectionError())
    def test_erro_de_conexao_vira_erro_da_api_externa(self, get):
        with self.assertRaises(ErroNaApiExterna):
            buscar_dados_do_livro('The Hobbit')

    @patch('biblioteca.services.requests.get', side_effect=requests.Timeout())
    def test_timeout_vira_erro_da_api_externa(self, get):
        with self.assertRaises(ErroNaApiExterna):
            buscar_dados_do_livro('The Hobbit')

    @patch('biblioteca.services.requests.get')
    def test_status_diferente_de_200_vira_erro(self, get):
        get.return_value = resposta_falsa(status=500)

        with self.assertRaises(ErroNaApiExterna) as contexto:
            buscar_dados_do_livro('The Hobbit')

        self.assertIn('500', str(contexto.exception))

    @patch('biblioteca.services.requests.get')
    def test_json_invalido_vira_erro(self, get):
        get.return_value = Mock(status_code=200, json=Mock(side_effect=ValueError()))

        with self.assertRaises(ErroNaApiExterna):
            buscar_dados_do_livro('The Hobbit')


class CompletarCamposVaziosTests(TestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')

    @patch('biblioteca.services.requests.get')
    def test_completa_o_que_esta_vazio(self, get):
        get.return_value = resposta_falsa(json_retorno=RESPOSTA_OK)
        livro = Livro(estante=self.estante, titulo='The Hobbit')

        aviso = completar_campos_vazios(livro)

        self.assertEqual(aviso, '')
        self.assertEqual(livro.autor, 'J.R.R. Tolkien')

    @patch('biblioteca.services.requests.get')
    def test_nao_sobrescreve_o_que_o_usuario_preencheu(self, get):
        get.return_value = resposta_falsa(json_retorno=RESPOSTA_OK)
        livro = Livro(estante=self.estante, titulo='The Hobbit', autor='Escrito por mim')

        completar_campos_vazios(livro)

        self.assertEqual(livro.autor, 'Escrito por mim')

    @patch('biblioteca.services.requests.get', side_effect=requests.ConnectionError())
    def test_devolve_aviso_quando_a_api_falha(self, get):
        livro = Livro(estante=self.estante, titulo='The Hobbit')

        self.assertIn('conectar', completar_campos_vazios(livro))
