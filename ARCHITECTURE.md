# Arquitetura Atual

A aplicação é uma API Flask monolítica executada em Docker. O Selenium roda em
um container separado e é usado apenas para acessar o Cifra Club.

## Implantação

```mermaid
flowchart LR
    Client[Cliente HTTP] -->|:3000| API[Container app\nFlask API]
    API -->|WebDriver HTTP :4444| Selenium[Container selenium\nFirefox + Selenium]
    Selenium -->|HTTPS| CifraClub[Cifra Club]
    API --> Chords[app/chords.py\nParser + notas + SVG]
```

## Fluxo da cifra

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as Flask
    participant S as Selenium
    participant W as Cifra Club
    participant P as chords.py

    C->>A: GET /artists/{artist}/songs/{song}
    A->>S: Abre URL da música
    S->>W: Busca página HTML
    W-->>S: HTML da cifra
    S-->>A: Metadados + linhas da cifra
    A->>P: remove_tabs(cifra)
    P-->>A: Cifra sem tablaturas
    A->>P: extract_chords(cifra)
    P-->>A: Acordes, notas e avisos
    A-->>C: JSON com cifra, chords e chord_warnings
    A->>S: quit(), inclusive em erro
```

## Fluxo do diagrama SVG

```mermaid
flowchart LR
    C[Cliente] -->|GET /chords/diagram.svg?name=C%23m7| A[Flask]
    A --> K[keyboard_svg(name)]
    K --> SVG[SVG em memória]
    SVG --> C
```

## Componentes

- `app/api.py`: rotas Flask e serialização da resposta.
- `app/cifraclub.py`: Selenium, BeautifulSoup e extração da página externa.
- `app/chords.py`: remoção de tablaturas, extração, interpretação e SVG.
- `app/test_chords.py`: testes unitários do parser, sem Selenium.
- `docker-compose.yml`: rede local entre API e Selenium.

Não há banco de dados, frontend, autenticação, cache ou arquivos SVG persistidos.
