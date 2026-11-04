# ecos-rpg

RPG de extração por turnos que roda dentro do Telegram. O jogador escolhe uma classe, desce a
uma dungeon de dez salas em duas seções, decide se extrai ou arrisca tudo no boss, e o que
traz de volta vira ouro e itens no baú. Morrer custa a mochila e, às vezes, o equipamento.

O interesse técnico do projeto está na separação: um **motor de jogo puro e testável**
(combate, habilidades, IA de inimigos, loot, progressão), um **repositório asyncpg** sobre
Postgres 16 e **handlers do Telegram finos**, que só traduzem o resultado do motor em tela.

> Versão de portfólio. O sistema roda em produção para um cliente; aqui marca e dados são fictícios, e o código em produção é privado por contrato.

## Por que existe

Jogos em bot de Telegram costumam virar um arquivo único com fórmula, SQL e mensagem
misturados, impossível de testar sem subir o bot. Este projeto parte do problema oposto:
as regras (dano por terreno, cooldowns, fase de chefe, distribuição de loot) precisam ser
verificáveis com uma semente fixa, e o estado de cada jogador precisa sobreviver a reinício
do processo, porque a conversa no Telegram continua aberta.

## Stack

- Python 3.12, `python-telegram-bot` 20.7 (polling)
- PostgreSQL 16 via `asyncpg` 0.30 (estado de combate em JSONB)
- pytest + pytest-asyncio, ruff (lint e formatação)
- Docker Compose (banco e bot), GitHub Actions (ruff + pytest com Postgres como serviço)

## Como rodar

```bash
cp .env.example .env          # preencha BOT_TOKEN (BotFather)
docker compose up --build     # sobe Postgres 16 e o bot; migrações e catálogo são aplicados na subida
```

Sem Docker para o bot (só o banco no compose):

```bash
docker compose up -d db
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python -m ecos_rpg.db.migrar   # aplica migrations/*.sql e sincroniza cosméticos
python main.py
```

Testes e lint:

```bash
ruff check . && ruff format --check .
pytest                          # o teste de banco usa TEST_DATABASE_URL e é pulado sem servidor
```

## Estrutura

| Caminho | O que é |
|---|---|
| `ecos_rpg/engine/` | Motor puro, sem Telegram nem banco |
| `engine/estado.py` | `EstadoCombate`: dataclass com `encode`/`decode` (JSONB) |
| `engine/combate.py` | Fórmulas de dano, modificador de terreno, status, turno do inimigo |
| `engine/habilidades.py` | 25 habilidades (5 por classe), validação, cooldowns, escolhas em duas etapas |
| `engine/inimigos.py`, `engine/bestiario/` | 37 inimigos em 3 tiers, escala por nível, sorteio por terreno |
| `engine/loot.py` | Quatro rolagens independentes, raridade por peso, bônus de sorte |
| `engine/fluxo.py` | Salas, minibosses, janelas de extração, boss, fuga, perdas na morte |
| `engine/turno.py` | Um turno completo: efeitos, ação, reação do inimigo, buffs |
| `engine/progressao.py`, `engine/cosmeticos.py` | Curva de XP, pontos de status, VIP, cosméticos |
| `ecos_rpg/db/` | Repositório asyncpg e `migrations/0001_schema.sql` |
| `ecos_rpg/bot/` | Handlers (`start`, `status`, `bastiao`, `dungeon`) e `telas.py` |
| `ecos_rpg/config.py` | Classes, terrenos, bênçãos, raridades, durabilidade (dados) |
| `tests/` | 124 testes: motor com semente fixa e integração com Postgres |
| `docs/adr/` | Decisões de arquitetura |

## A dungeon em um parágrafo

Ao entrar, o terreno é sorteado (lava, glacial, químico ou gigantes) e cada elemento rende
mais ou menos conforme o terreno: fogo em lava causa 60% do dano, gelo causa 140%. A **seção 1**
tem cinco salas normais e um miniboss; depois vem uma **janela de extração**: sair com tudo ou
seguir para a seção 2 (outras cinco salas e outro miniboss, nunca o mesmo). Uma segunda janela
antecede o **boss do terreno**, com chance pequena (0,5% a 2%, por tier) de aparecer "O Fim"
no lugar, que só começa depois de uma confirmação e tem fuga gratuita. Cada turno resolve, nessa
ordem: dano de efeitos sobre o jogador, a ação (ataque, habilidade, fuga), dano de efeitos sobre
o inimigo, a reação do inimigo (habilidades com chance própria, mudança de fase abaixo de 50% de
vida, golpes múltiplos, roubo de vida, escudo) e o decaimento de buffs e cooldowns. Fugir funciona
conforme a sorte e custa um percentual do ouro da run que cresce com as vitórias; morrer apaga a
mochila e sorteia a perda de cada equipamento por raridade (itens vinculados são poupados).
Vitórias pagam ouro, XP e loot; completar o boss rende 10% de bônus.

## Modelo de dados

- `players` (id do Telegram) 1:1 `characters`: classe, nível, XP, ouro, cristais, atributos,
  pontos de status alocados (`sp_*`), VIP, cosméticos equipados, bênção ativa.
- `inventory`: item por personagem, com `location` (`bau`, `mochila`, `bolso_seguro`,
  `equipado`), raridade, durabilidade e vínculo. Um índice único garante um equipado por slot.
- `dungeons` (instância: terreno, modo, status) 1:N `dungeon_members` (um por jogador e run:
  HP, mana e `combat_state` JSONB). Índice único parcial: uma run ativa por personagem.
- `parties` / `party_members`: grupos de até 4 (a camada de dados existe; o comando de grupo
  e o PvP ainda não).
- `crystal_transactions`: livro-razão de cristais. `cosmetics_catalog` e `character_cosmetics`:
  posse de cosméticos, com o catálogo sincronizado a partir do código.

## Decisões

1. [Estado de combate em JSONB, um por membro](docs/adr/0001-estado-de-combate-em-jsonb.md)
2. [Catálogos orientados a dados](docs/adr/0002-catalogos-orientados-a-dados.md)
3. [Motor isolado do transporte](docs/adr/0003-motor-isolado-do-transporte.md)

## O que ainda não existe

Loja, ferreiro, templo e mercado do Bastião são telas de espaço reservado. Uso de itens em
combate, grupos e PvP não estão implementados. Progressão (pontos de status, reset), cristais,
VIP e cosméticos têm motor e repositório testados, mas ainda não têm comando no bot; só o XP
de cada inimigo derrotado está ligado ao jogo.

---

## English

Turn-based extraction RPG that runs inside Telegram. The player picks a class, descends into
a ten-room, two-section dungeon, chooses between extracting and gambling everything on the
boss, and whatever comes back becomes gold and items in the stash. Dying costs the backpack
and sometimes the equipment.

The point of the project is the separation of concerns: a **pure, testable game engine**
(combat, skills, enemy AI, loot, progression), an **asyncpg repository** on Postgres 16, and
**thin Telegram handlers** that only turn engine results into screens.

> Portfolio version. The system runs in production for a client; brand and data are fictional here, and the production code is private by contract.

**Stack:** Python 3.12, python-telegram-bot 20.7 (polling), PostgreSQL 16 with asyncpg 0.30
(combat state in JSONB), pytest, ruff, Docker Compose, GitHub Actions with a Postgres service.

**Run it:**

```bash
cp .env.example .env            # set BOT_TOKEN
docker compose up --build       # Postgres 16 + bot; migrations run on startup
pytest                          # DB test uses TEST_DATABASE_URL, skipped without a server
```

**Dungeon loop.** The terrain is rolled on entry and changes elemental damage (fire in lava
deals 60%, ice 140%). Section 1 has five rooms and a miniboss, followed by an extraction
window: leave with the loot or continue to section 2 (five more rooms and a different
miniboss), then another window before the terrain boss. A rare special boss ("The End",
0.5% to 2% by tier) can replace it and requires confirmation, with a free escape. A turn
resolves in a fixed order: status damage on the player, the chosen action, status damage on
the enemy, the enemy reaction (per-ability chances, phase shift under 50% HP, multi-hit,
lifesteal, passive shield) and buff/cooldown decay. Fleeing succeeds by luck and costs a
growing share of the run's gold; dying wipes the backpack and rolls a loss per equipped item
by rarity (bound items are safe).

**Data model.** `players` 1:1 `characters` (class, level, XP, gold, crystals, stats, spent
status points, VIP, equipped cosmetics, blessing); `inventory` with `location`, rarity,
durability and binding (unique index: one equipped item per slot); `dungeons` 1:N
`dungeon_members`, one row per player and run holding HP, mana and the `combat_state` JSONB
(partial unique index: one active run per character); `parties`; `crystal_transactions`
ledger; `cosmetics_catalog` / `character_cosmetics`.

**Architecture decisions:** see `docs/adr/` (combat state as JSONB per member, data-driven
catalogs, engine isolated from transport).

**Not built yet:** shops, item use in combat, parties and PvP. Stat points, crystals, VIP and
cosmetics have a tested engine and repository but no bot command yet; only XP from kills is
wired into the game.
