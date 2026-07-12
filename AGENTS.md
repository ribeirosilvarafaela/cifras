# Contexto atual

API Flask em Python 3.8. `app/api.py` expõe as rotas, e `app/cifraclub.py` usa Selenium e BeautifulSoup para retornar metadados e `cifra`. O CLI apenas consome esse JSON. Não há testes hoje.

# Objetivo do MVP

Manter o endpoint `/artists/<artist>/songs/<song>`, removendo blocos de tablatura do campo `cifra` e acrescentando acordes únicos, notas e diagramas SVG de teclado. A ordem dos acordes deve ser a primeira ocorrência na cifra, preservando a grafia original.

# Fora de escopo

Sem banco, cache, autenticação, frontend, arquivos SVG persistidos, transcrição para piano, ritmo, compassos, mãos, voicings, inversões automáticas ou grande refatoração.

# Arquitetura proposta

Criar `app/chords.py`, módulo puro responsável por extrair, normalizar, interpretar e renderizar. Usar `pychord==1.2.2`, versão pequena e compatível com Python 3.8, chamando `Chord.components()`. Normalizar apenas para cálculo (`7M(9)` -> `maj9`, `7M` -> `maj7`); nunca substituir o nome exibido.

Remover seções `[Tab ...]` inteiras antes da extração, incluindo linhas `E|...`, `B|...`, `Parte 1 de 5` e marcações rítmicas. Remover o rótulo inicial `[Seção]`, separar tokens por espaços/parênteses e aceitar somente tokens inteiros que correspondam à gramática de acordes e sejam validados pelo `pychord`. Assim, palavras de letras não viram acordes. Deduplicar pelo nome original.

Gerar SVG determinístico em memória: duas oitavas, teclas brancas/pretas e notas do acorde destacadas. Servir por `GET /chords/diagram.svg?name=C%23m7`; nenhum arquivo de imagem será gravado. Em `CifraClub.cifra`, encerrar o driver em `finally`.

# Formato da resposta

Preservar todos os campos atuais e adicionar:

```json
{
  "chords": [{"name": "C#m7", "notes": ["C#", "E", "G#", "B"], "diagram": "/chords/diagram.svg?name=C%23m7"}],
  "chord_warnings": [{"name": "X...", "reason": "unsupported chord"}]
}
```

`chords` e `chord_warnings` são listas vazias quando não houver resultados. Um acorde inválido gera aviso e não interrompe a resposta.

# Etapas de implementação

1. Adicionar `pychord==1.2.2` às dependências.
2. Implementar parser, normalização, deduplicação e cálculo das notas.
3. Implementar o SVG e sua rota.
4. Remover tablaturas, enriquecer o resultado e corrigir o encerramento do Selenium.
5. Adicionar e executar testes unitários, lint e teste manual do endpoint.

# Arquivos afetados

Alterar `app/requirements.txt`, `app/cifraclub.py` e `app/api.py`. Criar somente `app/chords.py` e `app/test_chords.py`. O CLI não precisa mudar.

# Testes mínimos

Com `pytest`, sem Selenium: validar os 14 acordes do escopo e suas notas; normalizações `E7M`/`E7M(9)`/`F#m7(11)/C#`; ordem e deduplicação de The Scientist; remoção de tablaturas; rejeição de letras, seções e `Parte N de M`; aviso único para acorde não suportado; SVG válido contendo as notas destacadas. Testar `driver.quit()` com driver falso quando houver sucesso e exceção.

# Critérios de aceite

`make test` e `make lint` passam. The Scientist retorna, nesta ordem, `C#m7`, `A9`, `E`, `E9`, `E7M(9)`, `E6`, `B`, `B11/D#`, `E7M`; cada item tem notas e URL SVG válida. A cifra textual permanece, exceto pela remoção explícita de tablaturas; falsos positivos são rejeitados, falhas isoladas viram avisos únicos e o Selenium sempre é encerrado.
