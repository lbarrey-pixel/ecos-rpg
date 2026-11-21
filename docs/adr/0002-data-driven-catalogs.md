# 0002 — Data-driven catalogs

## Context

The game has five classes, 25 skills, dozens of enemies in three tiers, loot tables
by enemy type, and a cosmetics catalog. Balancing means changing numbers all the time;
the logic barely changes.

## Decision

Classes, terrains, blessings, rarities (`config.py`), skills (`SKILLS`), enemies
(`engine/bestiario/`, one module per terrain), loot (`engine/loot.py`), and cosmetics
(`engine/cosmeticos.py`) are pure dictionaries. The code that interprets them is small and
generic: `habilidades.executar` dispatches by `type`, `combate.turno_inimigo` by the enemy
skill type, and `inimigos.get_enemy_stats` scales any entry.

The contract between catalog and engine is tested: every skill type used in the bestiary
must be in `HABILIDADES_CONHECIDAS`, every enemy has all three tiers, and every terrain has
a miniboss pool large enough for two sections. A new entry the engine does not understand
breaks the test, not the player.

The cosmetics catalog is also copied to the database (`cosmetics_catalog`) in `migrar`,
with an upsert, because `character_cosmetics` needs a foreign key. The source remains
the code.

## Consequences

- Rebalancing is a diff of numbers, reviewable and without touching the logic.
- The catalog is versioned together with the code; there is no admin screen.
- Two places store cosmetics (the code and the table). Synchronization is idempotent and runs
  on every startup; removing a key from the code does not remove it from the database.
