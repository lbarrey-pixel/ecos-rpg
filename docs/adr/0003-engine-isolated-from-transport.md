# 0003 — Game engine isolated from Telegram and the database

## Context

The first version mixed damage formulas, enemy rolls, Telegram messages, and SQL
in the same file of more than a thousand lines. Testing a formula required a bot and a database;
changing the transport would require rewriting everything.

## Decision

Three layers with a dependency in only one direction:

- `engine/` is pure: it receives dicts and the `EstadoCombate`, and returns numbers, messages, and an
  outcome (`continua`, `inimigo_morto`, `jogador_morto`, `fugiu`, `escolha`, `invalida`).
  It does not import `telegram` or `asyncpg`. All randomness goes through an injectable `random.Random`.
- `db/` is the asyncpg repository. Each function receives a `Pool` or a `Connection`, which
  makes it possible to compose several operations in one transaction (extraction and death are atomic).
- `bot/` is thin handlers: they load state, call `engine.turno.resolver_turno`, save,
  and choose the screen. Texts and keyboards live in `bot/telas.py`.

Turn order (effects, action, enemy reaction, buffs) is the engine's decision, not the
handlers'. The bot only turns the outcome into a screen.

## Consequences

- The combat, skills, loot, and run-flow tests run in milliseconds, with no
  server, with a fixed seed.
- Only the database test needs Postgres; it applies the migration in a disposable schema.
- A second transport (web, CLI) would reuse `engine/` and `db/` in full.
- The boundary requires discipline: a new rule goes into the engine, even when it is shorter
  to write it directly in the handler.
