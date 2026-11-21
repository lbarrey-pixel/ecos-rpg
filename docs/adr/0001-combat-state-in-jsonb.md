# 0001 — Combat state in JSONB, one per member

## Context

A dungeon can be shared: several players enter the same instance (terrain),
but each one faces their own sequence of rooms, with their own enemy, status effects,
cooldowns, and buffs. A turn's state has about thirty fields, several of them nested
(`p_effects`, `e_effects`, `skill_cds`, the whole enemy with its skills), and it changes on every click.

## Decision

The state lives in `dungeon_members.combat_state` (JSONB), one row per player and run.
The code sees it as the `EstadoCombate` dataclass, which knows how to serialize itself (`encode`) and
read itself (`decode`), and which drops unknown keys and converts old names. The instance
(`dungeons`) stores only what is truly shared: terrain, mode, and status.

A partial unique index (`character_id WHERE member_status = 'active'`) guarantees one
active run per character and lets the same character return to the instance after leaving.

## Consequences

- Reading and writing a turn is one row, with no joins and no lock between players in the same instance.
- Adding a field to the state does not require a migration: `decode` fills in the default.
- You cannot query "who is poisoned" with plain SQL and an index; if that is ever
  needed, the field moves out of the JSON into a column.
- The JSON is not validated by the database; validation lives in `decode` and in the round-trip tests.
- Two simultaneous clicks from the same player would be two reads of the same state. The bot
  serializes actions per character with an in-memory lock (enough for a single polling
  process; with multiple processes it would be `SELECT ... FOR UPDATE` on the member's row).
