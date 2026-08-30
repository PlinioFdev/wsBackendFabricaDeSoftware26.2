# wsBackendFabricaDeSoftware26.2

API em Django REST Framework para organizar uma biblioteca pessoal, com página
web, autenticação JWT e documentação Swagger.
Projeto do Workshop de Backend da Fábrica de Software 26.2.

O usuário cria estantes e coloca livros dentro delas. Ao cadastrar um livro
basta informar o título: a API busca autor, ano e capa na
[Open Library](https://openlibrary.org) e preenche o resto sozinha.

## Tecnologias

- Python 3.14
- Django 6.1
- Django REST Framework 3.18
- PostgreSQL 17
- Docker e Docker Compose
- Simple JWT (autenticação por token)
- drf-spectacular (Swagger)
- requests (consumo da API externa)

## Como rodar com Docker

É o jeito recomendado: sobe a aplicação e o PostgreSQL juntos, sem instalar nada
além do Docker.

```bash
git clone https://github.com/PlinioFdev/wsBackendFabricaDeSoftware26.2.git
cd wsBackendFabricaDeSoftware26.2
docker compose up --build
```

Pronto. A aplicação fica em http://localhost:8000 e as migrações rodam sozinhas.

Para ver o projeto já com conteúdo, crie estantes e livros de exemplo. Os dados
vêm da Open Library na hora:

```bash
docker compose exec web python manage.py popular_biblioteca
```

Para criar um usuário e conseguir cadastrar pela página ou pela API:

```bash
docker compose exec web python manage.py createsuperuser
```

Para derrubar tudo:

```bash
docker compose down
```

## Como rodar sem Docker

Precisa de Python 3.14. Se você não tem PostgreSQL instalado, use SQLite
colocando `USE_SQLITE=True` no `.env`.

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # depois edite o .env
python manage.py migrate
python manage.py popular_biblioteca   # opcional: dados de exemplo
python manage.py createsuperuser
python manage.py runserver
```

## Variáveis de ambiente

Nenhum dado sensível fica no código. Copie `.env.example` para `.env` e ajuste.

| Variável | Para que serve | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta do Django | obrigatória |
| `DEBUG` | Modo de desenvolvimento | `False` |
| `ALLOWED_HOSTS` | Hosts liberados, separados por virgula | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Nome do banco | `biblioteca` |
| `POSTGRES_USER` | Usuário do banco | `biblioteca` |
| `POSTGRES_PASSWORD` | Senha do banco | `biblioteca` |
| `POSTGRES_HOST` | Endereço do banco | `localhost` |
| `POSTGRES_PORT` | Porta do banco | `5432` |
| `USE_SQLITE` | Usa SQLite no lugar do PostgreSQL | `False` |

Gere uma `SECRET_KEY` nova com:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> **Modo de desenvolvimento.** O `docker-compose.yml` sobe com `DEBUG=True`, que
> é o que faz o Django servir a folha de estilo e mostrar erros detalhados. Com
> `DEBUG=False` as páginas continuam abrindo, mas sem estilo: servir arquivo
> estático em produção é trabalho de um servidor web, não do Django.

## Página web

| Endereço | O que faz |
|---|---|
| `/` | Lista as estantes com os livros e as capas |
| `/livros/novo/` | Formulário para cadastrar livro (exige login) |
| `/contas/login/` | Tela de entrada |
| `/admin/` | Painel administrativo do Django |

No formulário basta digitar o título e escolher a estante. Autor, ano e capa vêm
da Open Library. Se você preencher o autor na mão, o seu valor é mantido.

As páginas usam o **Django Template Language**, o motor de template nativo do
framework. A sintaxe é a mesma do Jinja, mas o DTL integra direto com
`{% csrf_token %}`, `{% url %}`, a renderização de formulários e o sistema de
mensagens do Django — recursos que precisariam ser reimplementados na mão com
Jinja2.

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

Leitura é liberada para qualquer um. Criar, editar e apagar exigem token.

### Estantes

| Metodo | Rota | O que faz | Precisa de token |
|---|---|---|---|
| GET | `/api/estantes/` | Lista as estantes | não |
| POST | `/api/estantes/` | Cria uma estante | sim |
| GET | `/api/estantes/{id}/` | Detalha uma estante | não |
| PUT | `/api/estantes/{id}/` | Atualiza a estante | sim |
| PATCH | `/api/estantes/{id}/` | Atualiza um campo | sim |
| DELETE | `/api/estantes/{id}/` | Apaga a estante | sim |

### Livros

| Metodo | Rota | O que faz | Precisa de token |
|---|---|---|---|
| GET | `/api/livros/` | Lista os livros | não |
| POST | `/api/livros/` | Cria um livro | sim |
| GET | `/api/livros/{id}/` | Detalha um livro | não |
| PUT | `/api/livros/{id}/` | Atualiza o livro | sim |
| PATCH | `/api/livros/{id}/` | Atualiza um campo | sim |
| DELETE | `/api/livros/{id}/` | Apaga o livro | sim |

## Autenticação JWT

Pegue o token com o usuário criado no `createsuperuser`:

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

Use o `access` no cabeçalho das requisições de escrita:

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

## Documentação Swagger

| Endereço | O que e |
|---|---|
| `/api/docs/` | Swagger UI, para ler e testar a API pelo navegador |
| `/api/schema/` | Arquivo OpenAPI 3 gerado automaticamente |

## Consumo da API externa

Ao criar um livro, `biblioteca/services.py` consulta a Open Library:

```
GET https://openlibrary.org/search.json?q=<titulo>&limit=1
```

Os campos `autor`, `ano`, `isbn` e `capa_url` são preenchidos **apenas quando vêm
vazios**. Se você digitar o autor, o seu valor é mantido.

Exemplo, mandando só o título:

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

A API externa pode falhar, e isso não pode derrubar o cadastro. Todos os casos
abaixo salvam o livro normalmente com status **201** e devolvem um campo `aviso`
explicando o que aconteceu:

| Situacao | Aviso devolvido |
|---|---|
| Sem conexao (`ConnectionError`) | Não foi possível conectar na Open Library. |
| Demorou demais (`Timeout`) | A Open Library demorou demais para responder. |
| Outra falha de rede | Falha ao consultar a Open Library. |
| Status diferente de 200 | A Open Library respondeu com status 500. |
| Resposta não e um JSON valido | A Open Library devolveu uma resposta inválida. |
| Busca sem resultado | Nenhum livro com esse título foi encontrado na Open Library. |

Exemplo de resposta com a Open Library fora do ar:

```json
{
  "id": 2,
  "titulo": "Livro Qualquer",
  "autor": "",
  "ano": null,
  "estante": 1,
  "aviso": "Não foi possível conectar na Open Library."
}
```

A Open Library também devolve ano negativo em algumas obras antigas, o que o
banco recusaria. Nesse caso o ano e gravado como nulo em vez de quebrar.

## Testes

```bash
docker compose exec web python manage.py test     # com Docker
python manage.py test                             # sem Docker
```

São 30 testes cobrindo models e relacionamento, consumo da Open Library,
tratamento de erro, CRUD da API, autenticação JWT e as páginas web. As chamadas
externas são simuladas, então a suíte roda sem internet.

## Estrutura do projeto

```
wsBackendFabricaDeSoftware26.2/
├── biblioteca/
│   ├── management/           comando popular_biblioteca
│   ├── migrations/           migrações do banco
│   ├── static/biblioteca/    folha de estilo
│   ├── templates/            páginas HTML
│   ├── tests/                testes automatizados
│   ├── admin.py              registro dos models no painel admin
│   ├── forms.py              formulário da página web
│   ├── models.py             Estante e Livro
│   ├── serializers.py        conversão para JSON
│   ├── services.py           consumo da Open Library
│   ├── urls.py               rotas da API
│   ├── urls_web.py           rotas da página web
│   ├── views.py              viewsets do CRUD
│   └── views_web.py          views das páginas
├── projeto/
│   ├── settings.py
│   └── urls.py
├── .env.example              modelo das variáveis de ambiente
├── docker-compose.yml        aplicação + PostgreSQL
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

## Autor

Plinio Targino
