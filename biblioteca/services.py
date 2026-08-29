"""Consumo da API externa da Open Library."""

import requests

URL_BUSCA = 'https://openlibrary.org/search.json'
TIMEOUT_SEGUNDOS = 5


class ErroNaApiExterna(Exception):
    """A Open Library nao respondeu como o esperado."""


def buscar_dados_do_livro(titulo):
    """Busca um titulo na Open Library e devolve autor, ano, isbn e capa.

    Devolve None quando a busca nao encontra nenhum livro.
    Levanta ErroNaApiExterna quando a API falha.
    """
    try:
        resposta = requests.get(
            URL_BUSCA,
            params={'q': titulo, 'limit': 1},
            timeout=TIMEOUT_SEGUNDOS,
        )
    except requests.Timeout:
        raise ErroNaApiExterna('A Open Library demorou demais para responder.')
    except requests.ConnectionError:
        raise ErroNaApiExterna('Nao foi possivel conectar na Open Library.')
    except requests.RequestException:
        raise ErroNaApiExterna('Falha ao consultar a Open Library.')

    if resposta.status_code != 200:
        raise ErroNaApiExterna(
            f'A Open Library respondeu com status {resposta.status_code}.'
        )

    try:
        resultados = resposta.json().get('docs', [])
    except ValueError:
        raise ErroNaApiExterna('A Open Library devolveu uma resposta invalida.')

    if not resultados:
        return None

    livro = resultados[0]
    capa_id = livro.get('cover_i')
    ano = livro.get('first_publish_year')

    return {
        'autor': (livro.get('author_name') or [''])[0],
        'ano': ano if ano and ano > 0 else None,
        'isbn': (livro.get('isbn') or [''])[0],
        'capa_url': (
            f'https://covers.openlibrary.org/b/id/{capa_id}-M.jpg' if capa_id else ''
        ),
    }
