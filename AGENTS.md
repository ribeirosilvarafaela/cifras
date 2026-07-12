# Contexto atual

Monólito Flask em Python 3.8 executado em Docker. A API usa Selenium em um
container Firefox separado para consultar o Cifra Club, BeautifulSoup para ler
o HTML, `pychord` para interpretar acordes e gera diagramas SVG em memória.

# Objetivo

Adicionar frontend Jinja e persistência local de músicas sem quebrar a API
existente. A rota de artista/música deve consultar o SQLite antes de abrir o
Selenium e aceitar `refresh=true` para atualização manual.

# Arquitetura

`api.py` expõe JSON, HTML e SVG. `services.py` concentra slugificação, cache,
scraping, upsert e fallback. `cifraclub.py` continua responsável pelo Selenium
e encerra o driver em `finally`. `chords.py` continua puro e não grava imagens.

# Modelo de dados

`models.py` define `songs` com `id`, artista/nome e slugs, URLs, `cifra_json`,
`chords_json`, `chord_warnings_json` e timestamps. A combinação
`artist_slug + song_slug` é única. O banco é SQLite em `/data/cifraclub.db`,
persistido pelo volume `./data:/data`.

# Rotas e telas

- `GET /`: pesquisa e músicas recentes em `index.html`.
- `GET /songs`: lista salva em `songs.html`.
- `GET /songs/<id>`: música salva em `song.html`.
- `GET /artists/<artist>/songs/<song>`: JSON compatível, com cache e refresh.
- `GET /chords/diagram.svg?name=...`: SVG gerado em memória.

# Fluxo de persistência

Normalizar artista e música para slugs, buscar registro único e retornar o JSON
salvo quando não houver refresh. Em caso de refresh ou ausência, executar o
scraper, processar e salvar os JSONs. Se o refresh falhar com registro salvo,
retornar a versão anterior com `warnings`; sem registro salvo, preservar o
retorno de erro existente.

# Arquivos afetados

Alterar `app/api.py`, `app/cifraclub.py`, `app/requirements.txt` e
`docker-compose.yml`. Criar `app/database.py`, `app/models.py`, `app/services.py`,
templates Jinja, `app/static/` e testes em `app/tests/`.

# Etapas de implementação

1. Configurar SQLAlchemy, SQLite e o volume Docker.
2. Criar o modelo `Song` e o serviço de cache/scraping.
3. Ligar a API ao serviço e adicionar as rotas HTML.
4. Criar templates, CSS e JavaScript mínimo.
5. Testar com SQLite temporário e scraper falso.
6. Validar build, API, cache, refresh, fallback e frontend no Docker.

# Testes mínimos

Executar `make test`. Cobrir parser/SVG, slugificação, persistência, segunda
consulta sem Selenium, refresh, upsert, fallback, páginas Jinja, rota por ID e
contrato do campo `cifra` usando SQLite temporário.

# Fora de escopo

Sem React, Node.js, PostgreSQL, Redis, autenticação, microsserviços, cache
externo, migrações complexas, tabela separada de acordes ou arquivos SVG
persistidos.

# Critérios de aceite

`docker compose up --build` inicia API e Selenium; `/` serve o frontend; a
primeira pesquisa salva a música; a segunda não abre Selenium; `refresh=true`
atualiza; fallback retorna versão salva com aviso; recentes e `/songs/<id>`
funcionam; cifra, acordes e SVG permanecem compatíveis; testes usam SQLite
temporário.
