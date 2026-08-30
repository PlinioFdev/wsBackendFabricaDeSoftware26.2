# wsBackendFabricaDeSoftware26.2

API em Django REST Framework para organizar uma biblioteca pessoal.
Projeto do Workshop de Backend da Fabrica de Software 26.2.

O usuario cadastra estantes e coloca livros dentro delas. Ao cadastrar um livro
basta informar o titulo: a API busca autor, ano e capa na
[Open Library](https://openlibrary.org) e preenche sozinha.

## Tecnologias

- Python 3.14
- Django 6.1
- Django REST Framework 3.18
- requests 2.34
- SQLite

## Como rodar

Clone o repositorio e entre na pasta:

```bash
git clone https://github.com/PlinioFdev/wsBackendFabricaDeSoftware26.2.git
cd wsBackendFabricaDeSoftware26.2
```

Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie o banco e suba o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

A API fica em http://127.0.0.1:8000/api/

Para usar o painel administrativo, crie um usuario:

```bash
python manage.py createsuperuser
```

O painel fica em http://127.0.0.1:8000/admin/

## Modelagem

Duas entidades ligadas por chave estrangeira. Uma estante tem varios livros,
e cada livro pertence a uma estante. Apagar a estante apaga os livros dela.

```
Estante                     Livro
-------                     -----
id                          id
nome                        estante  (FK -> Estante)
descricao                   titulo
criada_em                   autor
                            ano
                            isbn
                            capa_url
                            criado_em
```

## Endpoints

### Estantes

| Metodo | Rota                  | O que faz            |
|--------|-----------------------|----------------------|
| GET    | `/api/estantes/`      | Lista as estantes    |
| POST   | `/api/estantes/`      | Cria uma estante     |
| GET    | `/api/estantes/{id}/` | Detalha uma estante  |
| PUT    | `/api/estantes/{id}/` | Atualiza a estante   |
| PATCH  | `/api/estantes/{id}/` | Atualiza um campo    |
| DELETE | `/api/estantes/{id}/` | Apaga a estante      |

### Livros

| Metodo | Rota                | O que faz          |
|--------|---------------------|--------------------|
| GET    | `/api/livros/`      | Lista os livros    |
| POST   | `/api/livros/`      | Cria um livro      |
| GET    | `/api/livros/{id}/` | Detalha um livro   |
| PUT    | `/api/livros/{id}/` | Atualiza o livro   |
| PATCH  | `/api/livros/{id}/` | Atualiza um campo  |
| DELETE | `/api/livros/{id}/` | Apaga o livro      |

## Consumo da API externa

Ao criar um livro, `LivroViewSet.perform_create` chama
`biblioteca/services.py`, que consulta a Open Library:

```
GET https://openlibrary.org/search.json?q=<titulo>&limit=1
```

Os campos `autor`, `ano`, `isbn` e `capa_url` sao preenchidos **apenas quando
vem vazios** na requisicao. Se voce digitar o autor, o seu valor e mantido.

Exemplo, mandando so o titulo:

```bash
curl -X POST http://127.0.0.1:8000/api/livros/ \
  -H "Content-Type: application/json" \
  -d '{"titulo": "The Hobbit", "estante": 1}'
```

Resposta:

```json
{
  "id": 1,
  "titulo": "The Hobbit",
  "autor": "J.R.R. Tolkien",
  "ano": 1937,
  "isbn": "",
  "capa_url": "https://covers.openlibrary.org/b/id/14627509-M.jpg",
  "estante": 1,
  "estante_nome": "Fantasia",
  "criado_em": "2026-08-29T19:27:33-03:00"
}
```

## Tratamento de erros

A API externa pode falhar, e isso nao pode derrubar o cadastro. Todos os casos
abaixo salvam o livro normalmente com status **201** e devolvem um campo
`aviso` explicando o que aconteceu:

| Situacao                            | Aviso devolvido                                          |
|-------------------------------------|----------------------------------------------------------|
| Sem conexao (`ConnectionError`)     | Nao foi possivel conectar na Open Library.               |
| Demorou demais (`Timeout`)          | A Open Library demorou demais para responder.            |
| Outra falha de rede                 | Falha ao consultar a Open Library.                       |
| Status diferente de 200             | A Open Library respondeu com status 500.                 |
| Resposta nao e um JSON valido       | A Open Library devolveu uma resposta invalida.           |
| Busca sem resultado                 | Nenhum livro com esse titulo foi encontrado na Open Library. |

Exemplo de resposta com a Open Library fora do ar:

```json
{
  "id": 2,
  "titulo": "Livro Qualquer",
  "autor": "",
  "ano": null,
  "estante": 1,
  "aviso": "Nao foi possivel conectar na Open Library."
}
```

## Estrutura do projeto

```
wsBackendFabricaDeSoftware26.2/
├── biblioteca/
│   ├── migrations/       migracoes do banco
│   ├── admin.py          registro dos models no painel admin
│   ├── models.py         Estante e Livro
│   ├── serializers.py    conversao para JSON
│   ├── services.py       consumo da Open Library
│   ├── urls.py           rotas da API
│   └── views.py          viewsets do CRUD
├── projeto/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── README.md
```

## Autor

Plinio Targino
