"""Consumo da API externa da Open Library."""

import requests

URL_BUSCA = 'https://openlibrary.org/search.json'
TIMEOUT_SEGUNDOS = 5


def buscar_dados_do_livro(titulo):
    """Busca um titulo na Open Library e devolve autor, ano, isbn e capa."""
    resposta = requests.get(
        URL_BUSCA,
        params={'q': titulo, 'limit': 1},
        timeout=TIMEOUT_SEGUNDOS,
    )
    resposta.raise_for_status()

    resultados = resposta.json().get('docs', [])
    if not resultados:
        return None

    livro = resultados[0]
    capa_id = livro.get('cover_i')

    return {
        'autor': (livro.get('author_name') or [''])[0],
        'ano': livro.get('first_publish_year'),
        'isbn': (livro.get('isbn') or [''])[0],
        'capa_url': (
            f'https://covers.openlibrary.org/b/id/{capa_id}-M.jpg' if capa_id else ''
        ),
    }
