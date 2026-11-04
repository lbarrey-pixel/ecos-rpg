"""Instâncias de dungeon e o estado de cada membro."""

from __future__ import annotations

import asyncpg

from ..engine.estado import EstadoCombate

Db = asyncpg.Pool | asyncpg.Connection


async def find_open_instance(db: Db, mode: str):
    return await db.fetchrow(
        "SELECT * FROM dungeons WHERE mode = $1 AND status = 'active' "
        "ORDER BY created_at DESC LIMIT 1",
        mode,
    )


async def create_instance(db: Db, terrain: str, mode: str):
    return await db.fetchrow(
        "INSERT INTO dungeons (terrain, mode) VALUES ($1, $2) RETURNING *",
        terrain,
        mode,
    )


async def get_instance(db: Db, dungeon_id: int):
    return await db.fetchrow("SELECT * FROM dungeons WHERE id = $1", dungeon_id)


async def get_active_member(db: Db, character_id: int):
    return await db.fetchrow(
        """
        SELECT dm.*, d.terrain, d.mode AS dungeon_mode
        FROM dungeon_members dm
        JOIN dungeons d ON d.id = dm.dungeon_id
        WHERE dm.character_id = $1 AND dm.member_status = 'active' AND d.status = 'active'
        """,
        character_id,
    )


async def join_instance(
    db: Db,
    dungeon_id: int,
    character_id: int,
    hp: int,
    mana: int,
    estado: EstadoCombate,
    party_id: int | None = None,
):
    return await db.fetchrow(
        """
        INSERT INTO dungeon_members
            (dungeon_id, character_id, party_id, hp_current, mana_current, combat_state)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb)
        RETURNING *
        """,
        dungeon_id,
        character_id,
        party_id,
        hp,
        mana,
        estado.encode(),
    )


async def save_member(db: Db, character_id: int, hp: int, mana: int, estado: EstadoCombate) -> None:
    await db.execute(
        """
        UPDATE dungeon_members
        SET hp_current = $1, mana_current = $2, combat_state = $3::jsonb, last_updated = now()
        WHERE character_id = $4 AND member_status = 'active'
        """,
        hp,
        mana,
        estado.encode(),
        character_id,
    )


async def exit_member(db: Db, character_id: int, exit_status: str) -> None:
    """``exit_status``: 'extracted' ou 'dead'."""
    await db.execute(
        "UPDATE dungeon_members SET member_status = $1, exited_at = now() "
        "WHERE character_id = $2 AND member_status = 'active'",
        exit_status,
        character_id,
    )


async def close_if_empty(db: Db, dungeon_id: int) -> None:
    await db.execute(
        """
        UPDATE dungeons SET status = 'finished'
        WHERE id = $1 AND NOT EXISTS (
            SELECT 1 FROM dungeon_members WHERE dungeon_id = $1 AND member_status = 'active')
        """,
        dungeon_id,
    )
