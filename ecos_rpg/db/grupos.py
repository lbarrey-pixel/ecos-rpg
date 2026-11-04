"""Grupos formados fora da dungeon (o comando de grupo ainda não existe no bot)."""

from __future__ import annotations

import asyncpg

Db = asyncpg.Pool | asyncpg.Connection

TAMANHO_MAX = 4


async def create_party(pool: asyncpg.Pool, leader_character_id: int):
    async with pool.acquire() as conn, conn.transaction():
        grupo = await conn.fetchrow(
            "INSERT INTO parties (leader_id) VALUES ($1) RETURNING *",
            leader_character_id,
        )
        await conn.execute(
            "INSERT INTO party_members (party_id, character_id) VALUES ($1, $2)",
            grupo["id"],
            leader_character_id,
        )
    return grupo


async def get_party_of_character(db: Db, character_id: int):
    return await db.fetchrow(
        "SELECT p.* FROM parties p JOIN party_members pm ON pm.party_id = p.id "
        "WHERE pm.character_id = $1 AND p.status = 'forming'",
        character_id,
    )


async def join_party(pool: asyncpg.Pool, party_id: int, character_id: int):
    """None se o grupo já está cheio. A linha do grupo é travada para duas entradas simultâneas."""
    async with pool.acquire() as conn, conn.transaction():
        await conn.fetchval("SELECT id FROM parties WHERE id = $1 FOR UPDATE", party_id)
        total = await conn.fetchval(
            "SELECT COUNT(*) FROM party_members WHERE party_id = $1", party_id
        )
        if total >= TAMANHO_MAX:
            return None
        return await conn.fetchrow(
            "INSERT INTO party_members (party_id, character_id) VALUES ($1, $2) RETURNING *",
            party_id,
            character_id,
        )


async def get_party_members(db: Db, party_id: int):
    return await db.fetch(
        "SELECT c.*, p.leader_id FROM characters c "
        "JOIN party_members pm ON pm.character_id = c.id "
        "JOIN parties p ON p.id = pm.party_id WHERE pm.party_id = $1",
        party_id,
    )


async def disband_party(db: Db, party_id: int) -> None:
    await db.execute("UPDATE parties SET status = 'disbanded' WHERE id = $1", party_id)
