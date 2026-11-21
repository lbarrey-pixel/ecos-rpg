# ecos-rpg

Turn-based extraction RPG that runs inside Telegram. The player picks a class, descends into a
ten-room dungeon in two sections, decides whether to extract or risk everything on the boss, and
whatever they bring back becomes gold and items in the chest. Dying costs the backpack and,
sometimes, the equipment.

The technical interest of the project is the separation: a **pure, testable game engine**
(combat, skills, enemy AI, loot, progression), an **asyncpg repository** on
Postgres 16, and **thin Telegram handlers** that only turn the engine's result into a screen.

> Portfolio version. The system runs in production for a client; brand and data here are fictional, and the production code is private by contract.

## Why it exists

Telegram bot games tend to become a single file with formulas, SQL, and messages
mixed together, impossible to test without starting the bot. This project starts from the opposite
problem: the rules (terrain damage, cooldowns, boss phase, loot distribution) need to be
verifiable with a fixed seed, and each player's state needs to survive a process
restart, because the Telegram conversation stays open.

## Stack

- Python 3.12, `python-telegram-bot` 20.7 (polling)
- PostgreSQL 16 via `asyncpg` 0.30 (combat state in JSONB)
- pytest + pytest-asyncio, ruff (lint and formatting)
- Docker Compose (database and bot), GitHub Actions (ruff + pytest with Postgres as a service)

## How to run

```bash
cp .env.example .env          # fill in BOT_TOKEN (BotFather)
docker compose up --build     # starts Postgres 16 and the bot; migrations and the catalog are applied on startup
```

Without Docker for the bot (only the database in Compose):

```bash
docker compose up -d db
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python -m ecos_rpg.db.migrar   # applies migrations/*.sql and syncs cosmetics
python main.py
```

Tests and lint:

```bash
ruff check . && ruff format --check .
pytest                          # the database test uses TEST_DATABASE_URL and is skipped without a server
```

## Structure

| Path | What it is |
|---|---|
| `ecos_rpg/engine/` | Pure engine, with no Telegram and no database |
| `engine/estado.py` | `EstadoCombate`: dataclass with `encode`/`decode` (JSONB) |
| `engine/combate.py` | Damage formulas, terrain modifier, status, enemy turn |
| `engine/habilidades.py` | 25 skills (5 per class), validation, cooldowns, two-step choices |
| `engine/inimigos.py`, `engine/bestiario/` | 37 enemies in 3 tiers, scaling by level, rolled by terrain |
| `engine/loot.py` | Four independent rolls, rarity by weight, luck bonus |
| `engine/fluxo.py` | Rooms, minibosses, extraction windows, boss, flee, losses on death |
| `engine/turno.py` | One complete turn: effects, action, enemy reaction, buffs |
| `engine/progressao.py`, `engine/cosmeticos.py` | XP curve, status points, VIP, cosmetics |
| `ecos_rpg/db/` | asyncpg repository and `migrations/0001_schema.sql` |
| `ecos_rpg/bot/` | Handlers (`start`, `status`, `bastiao`, `dungeon`) and `telas.py` |
| `ecos_rpg/config.py` | Classes, terrains, blessings, rarities, durability (data) |
| `tests/` | 124 tests: engine with a fixed seed and Postgres integration |
| `docs/adr/` | Architecture decisions |

## The dungeon in one paragraph

On entry, the terrain is rolled (lava, glacial, chemical, or giants) and each element deals
more or less depending on the terrain: fire in lava deals 60% of the damage, ice deals 140%.
**Section 1** has five normal rooms and a miniboss; then comes an **extraction window**: leave
with everything or continue to section 2 (another five rooms and another miniboss, never the
same one). A second window precedes the **terrain boss**, with a small chance (0.5% to 2%, by
tier) that "O Fim" appears instead, which only starts after a confirmation and has a free
escape. Each turn resolves, in this order: effect damage on the player, the action (attack,
skill, flee), effect damage on the enemy, the enemy reaction (skills with their own chance,
a phase change below 50% health, multiple hits, lifesteal, shield), and the decay of buffs
and cooldowns. Fleeing works according to luck and costs a percentage of the run's gold that grows
with victories; dying wipes the backpack and rolls the loss of each piece of equipment by
rarity (bound items are spared). Victories pay gold, XP, and loot; completing the boss yields
a 10% bonus.

## Data model

- `players` (Telegram id) 1:1 `characters`: class, level, XP, gold, crystals, attributes,
  allocated status points (`sp_*`), VIP, equipped cosmetics, active blessing.
- `inventory`: items per character, with `location` (`bau`, `mochila`, `bolso_seguro`,
  `equipado`), rarity, durability, and binding. A unique index guarantees one equipped item per slot.
- `dungeons` (instance: terrain, mode, status) 1:N `dungeon_members` (one per player and run:
  HP, mana, and `combat_state` JSONB). Partial unique index: one active run per character.
- `parties` / `party_members`: groups of up to 4 (the data layer exists; the group command
  and PvP do not yet).
- `crystal_transactions`: crystal ledger. `cosmetics_catalog` and `character_cosmetics`:
  cosmetic ownership, with the catalog synced from the code.

## Decisions

1. [Combat state in JSONB, one per member](docs/adr/0001-combat-state-in-jsonb.md)
2. [Data-driven catalogs](docs/adr/0002-data-driven-catalogs.md)
3. [Engine isolated from transport](docs/adr/0003-engine-isolated-from-transport.md)

## What does not exist yet

Bastião's shop, blacksmith, temple, and market are placeholder screens. Item use in
combat, groups, and PvP are not implemented. Progression (status points, reset), crystals,
VIP, and cosmetics have a tested engine and repository, but still have no command in the bot;
only the XP from each defeated enemy is connected to the game.
