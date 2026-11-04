# 0003 — Motor de jogo isolado do Telegram e do banco

## Contexto

A primeira versão misturava fórmulas de dano, sorteio de inimigo, mensagens do Telegram e SQL
no mesmo arquivo de mais de mil linhas. Testar uma fórmula exigia um bot e um banco; trocar
o transporte exigiria reescrever tudo.

## Decisão

Três camadas com dependência em um só sentido:

- `engine/` é puro: recebe dicts e o `EstadoCombate`, devolve números, mensagens e um
  desfecho (`continua`, `inimigo_morto`, `jogador_morto`, `fugiu`, `escolha`, `invalida`).
  Não importa `telegram` nem `asyncpg`. Toda aleatoriedade passa por um `random.Random`
  injetável.
- `db/` é o repositório asyncpg. Cada função recebe um `Pool` ou uma `Connection`, o que
  permite compor várias operações numa transação (extração e morte são atômicas).
- `bot/` são handlers finos: carregam estado, chamam `engine.turno.resolver_turno`, gravam
  e escolhem a tela. Textos e teclados ficam em `bot/telas.py`.

A ordem do turno (efeitos, ação, reação do inimigo, buffs) é decisão do motor, não dos
handlers. O bot só traduz o desfecho em tela.

## Consequências

- Os testes de combate, habilidades, loot e fluxo da run rodam em milissegundos, sem
  servidor, com semente fixa.
- Só o teste de banco precisa de Postgres; ele aplica a migração num schema descartável.
- Um segundo transporte (web, CLI) reaproveitaria `engine/` e `db/` inteiros.
- A fronteira exige disciplina: regra nova vai para o motor, mesmo quando é mais curto
  escrevê-la direto no handler.
