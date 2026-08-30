from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from biblioteca.models import Estante, Livro

RESPOSTA_OK = {
    'docs': [
        {
            'author_name': ['J.R.R. Tolkien'],
            'first_publish_year': 1937,
            'cover_i': 42,
        }
    ]
}


class LeituraPublicaTests(APITestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')

    def test_listar_estantes_sem_login(self):
        resposta = self.client.get('/api/estantes/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)

    def test_listar_livros_sem_login(self):
        resposta = self.client.get('/api/livros/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)


class EscritaProtegidaTests(APITestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')

    def test_criar_estante_sem_token_e_negado(self):
        resposta = self.client.post('/api/estantes/', {'nome': 'Invasor'})
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_apagar_estante_sem_token_e_negado(self):
        resposta = self.client.delete(f'/api/estantes/{self.estante.id}/')
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenJWTTests(APITestCase):
    def setUp(self):
        User.objects.create_user('plinio', password='senha-de-teste')

    def test_token_e_gerado_com_credenciais_corretas(self):
        resposta = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'plinio', 'password': 'senha-de-teste'},
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn('access', resposta.data)
        self.assertIn('refresh', resposta.data)

    def test_senha_errada_nao_gera_token(self):
        resposta = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'plinio', 'password': 'errada'},
        )
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_permite_criar_estante(self):
        token = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'plinio', 'password': 'senha-de-teste'},
        ).data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resposta = self.client.post('/api/estantes/', {'nome': 'Autenticada'})

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)


class CriarLivroTests(APITestCase):
    def setUp(self):
        self.estante = Estante.objects.create(nome='Fantasia')
        self.client.force_authenticate(User.objects.create_user('plinio'))

    @patch('biblioteca.services.requests.get')
    def test_open_library_completa_os_dados(self, get):
        get.return_value = Mock(status_code=200, json=Mock(return_value=RESPOSTA_OK))

        resposta = self.client.post(
            '/api/livros/', {'titulo': 'The Hobbit', 'estante': self.estante.id}
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['autor'], 'J.R.R. Tolkien')
        self.assertEqual(resposta.data['ano'], 1937)

    @patch('biblioteca.services.requests.get', side_effect=requests.ConnectionError())
    def test_falha_da_api_externa_nao_impede_o_cadastro(self, get):
        resposta = self.client.post(
            '/api/livros/', {'titulo': 'The Hobbit', 'estante': self.estante.id}
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertIn('aviso', resposta.data)
        self.assertEqual(Livro.objects.count(), 1)

    def test_livro_sem_estante_e_recusado(self):
        resposta = self.client.post('/api/livros/', {'titulo': 'Orfao'})
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('biblioteca.services.requests.get')
    def test_resposta_mostra_o_nome_da_estante(self, get):
        get.return_value = Mock(status_code=200, json=Mock(return_value=RESPOSTA_OK))

        resposta = self.client.post(
            '/api/livros/', {'titulo': 'The Hobbit', 'estante': self.estante.id}
        )

        self.assertEqual(resposta.data['estante_nome'], 'Fantasia')
