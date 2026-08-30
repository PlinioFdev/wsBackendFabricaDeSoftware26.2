# wsBackendFabricaDeSoftware26.2

API em Django REST Framework para organizar uma biblioteca pessoal, com pagina
web, autenticacao JWT e documentacao Swagger.
Projeto do Workshop de Backend da Fabrica de Software 26.2.

O usuario cria estantes e coloca livros dentro delas. Ao cadastrar um livro
basta informar o titulo: a API busca autor, ano e capa na
[Open Library](https://openlibrary.org) e preenche o resto sozinha.

## Tecnologias

- Python 3.14
- Django 6.1
- Django REST Framework 3.18
- PostgreSQL 17
- Docker e Docker Compose
- Simple JWT (autenticacao por token)
- drf-spectacular (Swagger)
- requests (consumo da API externa)

## Como rodar com Docker

E o jeito recomendado: sobe a aplicacao e o PostgreSQL juntos, sem instalar nada
alem do Docker.

```bash
git clone https://github.com/PlinioFdev/wsBackendFabricaDeSoftware26.2.git
cd wsBackendFabricaDeSoftware26.2
docker compose up --build
```

Pronto. A aplicacao fica em http://localhost:8000 e as migracoes rodam sozinhas.

Para criar um usuario e conseguir cadastrar dados:

```bash
docker compose exec web python manage.py createsuperuser
```

Para derrubar tudo:

```bash
docker compose down
```

## Como rodar sem Docker

Precisa de Python 3.14. Se voce nao tem PostgreSQL instalado, use SQLite
colocando `USE_SQLITE=True` no `.env`.

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # depois edite o .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variaveis de ambiente

Nenhum dado sensivel fica no codigo. Copie `.env.example` para `.env` e ajuste.

| Variavel | Para que serve | Padrao |
|---|---|---|
| `SECRET_KEY` | Chave secreta do Django | obrigatoria |
| `DEBUG` | Modo de desenvolvimento | `False` |
| `ALLOWED_HOSTS` | Hosts liberados, separados por virgula | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Nome do banco | `biblioteca` |
| `POSTGRES_USER` | Usuario do banco | `biblioteca` |
| `POSTGRES_PASSWORD` | Senha do banco | `biblioteca` |
| `POSTGRES_HOST` | Endereco do banco | `localhost` |
| `POSTGRES_PORT` | Porta do banco | `5432` |
| `USE_SQLITE` | Usa SQLite no lugar do PostgreSQL | `False` |

Gere uma `SECRET_KEY` nova com:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Pagina web

| Endereco | O que faz |
|---|---|
| `/` | Lista as estantes com os livros e as capas |
| `/livros/novo/` | Formulario para cadastrar livro (exige login) |
| `/contas/login/` | Tela de entrada |
| `/admin/` | Painel administrativo do Django |

No formulario basta digitar o titulo e escolher a estante. Autor, ano e capa vem
da Open Library. Se voce preencher o autor na mao, o seu valor e mantido.

## Modelagem

Duas entidades ligadas por chave estrangeira. Uma estante tem varios livros, e
cada livro pertence a uma estante. Apagar a estante apaga os livros dela.

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

## Endpoints da API

Leitura e liberada para qualquer um. Criar, editar e apagar exigem token.

### Estantes

| Metodo | Rota | O que faz | Precisa de token |
|---|---|---|---|
| GET | `/api/estantes/` | Lista as estantes | nao |
| POST | `/api/estantes/` | Cria uma estante | sim |
| GET | `/api/estantes/{id}/` | Detalha uma estante | nao |
| PUT | `/api/estantes/{id}/` | Atualiza a estante | sim |
| PATCH | `/api/estantes/{id}/` | Atualiza um campo | sim |
| DELETE | `/api/estantes/{id}/` | Apaga a estante | sim |

### Livros

| Metodo | Rota | O que faz | Precisa de token |
|---|---|---|---|
| GET | `/api/livros/` | Lista os livros | nao |
| POST | `/api/livros/` | Cria um livro | sim |
| GET | `/api/livros/{id}/` | Detalha um livro | nao |
| PUT | `/api/livros/{id}/` | Atualiza o livro | sim |
| PATCH | `/api/livros/{id}/` | Atualiza um campo | sim |
| DELETE | `/api/livros/{id}/` | Apaga o livro | sim |

## Autenticacao JWT

Pegue o token com o usuario criado no `createsuperuser`:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu-usuario", "password": "sua-senha"}'
```

Resposta:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Use o `access` no cabecalho das requisicoes de escrita:

```bash
curl -X POST http://localhost:8000/api/livros/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_ACCESS" \
  -d '{"titulo": "The Hobbit", "estante": 1}'
```

O `access` vale 1 hora. Quando expirar, renove com o `refresh`:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "SEU_TOKEN_REFRESH"}'
```

Sem token, as rotas de escrita respondem **401**.

## Documentacao Swagger

| Endereco | O que e |
|---|---|
| `/api/docs/` | Swagger UI, para ler e testar a API pelo navegador |
| `/api/schema/` | Arquivo OpenAPI 3 gerado automaticamente |

## Consumo da API externa

Ao criar um livro, `biblioteca/services.py` consulta a Open Library:

```
GET https://openlibrary.org/search.json?q=<titulo>&limit=1
```

Os campos `autor`, `ano`, `isbn` e `capa_url` sao preenchidos **apenas quando vem
vazios**. Se voce digitar o autor, o seu valor e mantido.

Exemplo, mandando so o titulo:

```bash
curl -X POST http://localhost:8000/api/livros/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_ACCESS" \
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
  "criado_em": "2026-08-30T09:06:10-03:00"
}
```

## Tratamento de erros

A API externa pode falhar, e isso nao pode derrubar o cadastro. Todos os casos
abaixo salvam o livro normalmente com status **201** e devolvem um campo `aviso`
explicando o que aconteceu:

| Situacao | Aviso devolvido |
|---|---|
| Sem conexao (`ConnectionError`) | Nao foi possivel conectar na Open Library. |
| Demorou demais (`Timeout`) | A Open Library demorou demais para responder. |
| Outra falha de rede | Falha ao consultar a Open Library. |
| Status diferente de 200 | A Open Library respondeu com status 500. |
| Resposta nao e um JSON valido | A Open Library devolveu uma resposta invalida. |
| Busca sem resultado | Nenhum livro com esse titulo foi encontrado na Open Library. |

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

A Open Library tambem devolve ano negativo em algumas obras antigas, o que o
banco recusaria. Nesse caso o ano e gravado como nulo em vez de quebrar.

## Testes

```bash
docker compose exec web python manage.py test     # com Docker
python manage.py test                             # sem Docker
```

Sao 30 testes cobrindo models e relacionamento, consumo da Open Library,
tratamento de erro, CRUD da API, autenticacao JWT e as paginas web. As chamadas
externas sao simuladas, entao a suite roda sem internet.

## Estrutura do projeto

```
wsBackendFabricaDeSoftware26.2/
├── biblioteca/
│   ├── migrations/           migracoes do banco
│   ├── static/biblioteca/    folha de estilo
│   ├── templates/            paginas HTML
│   ├── tests/                testes automatizados
│   ├── admin.py              registro dos models no painel admin
│   ├── forms.py              formulario da pagina web
│   ├── models.py             Estante e Livro
│   ├── serializers.py        conversao para JSON
│   ├── services.py           consumo da Open Library
│   ├── urls.py               rotas da API
│   ├── urls_web.py           rotas da pagina web
│   ├── views.py              viewsets do CRUD
│   └── views_web.py          views das paginas
├── projeto/
│   ├── settings.py
│   └── urls.py
├── .env.example              modelo das variaveis de ambiente
├── docker-compose.yml        aplicacao + PostgreSQL
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

## Autor

Plinio Targino
