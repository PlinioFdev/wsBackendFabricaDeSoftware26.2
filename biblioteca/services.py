"""Consumo da API externa da Open Library."""

import requests

URL_BUSCA = 'https://openlibrary.org/search.json'
TIMEOUT_SEGUNDOS = 5


class ErroNaApiExterna(Exception):
    """A Open Library não respondeu como o esperado."""


def buscar_dados_do_livro(titulo):
    """Busca um título na Open Library e devolve autor, ano, isbn e capa.

    Devolve None quando a busca não encontra nenhum livro.
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
        raise ErroNaApiExterna('Não foi possível conectar na Open Library.')
    except requests.RequestException:
        raise ErroNaApiExterna('Falha ao consultar a Open Library.')

    if resposta.status_code != 200:
        raise ErroNaApiExterna(
            f'A Open Library respondeu com status {resposta.status_code}.'
        )

    try:
        resultados = resposta.json().get('docs', [])
    except ValueError:
        raise ErroNaApiExterna('A Open Library devolveu uma resposta inválida.')

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


CAMPOS_COMPLETADOS = ['autor', 'ano', 'isbn', 'capa_url']


def completar_campos_vazios(livro):
    """Completa os campos vazios do livro com dados da Open Library.

    Não sobrescreve nada que o usuário tenha preenchido.
    Devolve uma mensagem de aviso quando não deu para completar,
    ou uma string vazia quando deu tudo certo.
    """
    try:
        dados = buscar_dados_do_livro(livro.titulo)
    except ErroNaApiExterna as erro:
        return str(erro)

    if dados is None:
        return 'Nenhum livro com esse título foi encontrado na Open Library.'

    for campo in CAMPOS_COMPLETADOS:
        if not getattr(livro, campo) and dados.get(campo):
            setattr(livro, campo, dados[campo])

    return ''
