"""Cristais, VIP, cosméticos e textos de perfil."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import asyncpg

from ..engine.cosmeticos import CATALOGO, COLUNA_POR_TIPO

Db = asyncpg.Pool | asyncpg.Connection

GRITO_MAX = 60
EPITAFIO_MAX = 80


async def sincronizar_catalogo(db: Db) -> None:
    """Upsert do catálogo em código para a tabela. Idempotente."""
    await db.executemany(
        """
        INSERT INTO cosmetics_catalog (key, name, type, cost_crystals, is_vip_pool, is_founder)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (key) DO UPDATE SET
            name = EXCLUDED.name, type = EXCLUDED.type, cost_crystals = EXCLUDED.cost_crystals,
            is_vip_pool = EXCLUDED.is_vip_pool, is_founder = EXCLUDED.is_founder
        """,
        [
            (
                k,
                c["name"],
                c["type"],
                c["cost_crystals"],
                c["is_vip_pool"],
                c["is_founder"],
            )
            for k, c in CATALOGO.items()
        ],
    )


# ── cristais ─────────────────────────────────────────────────
async def update_crystals(pool: asyncpg.Pool, character_id: int, amount: int, reason: str) -> dict:
    """Credita ou debita cristais e registra a transação; o saldo nunca fica negativo."""
    async with pool.acquire() as conn, conn.transaction():
        saldo = await conn.fetchval(
            "SELECT crystals FROM characters WHERE id = $1 FOR UPDATE", character_id
        )
        if saldo is None:
            return {"error": "Personagem não encontrado"}
        if saldo + amount < 0:
            return {"error": f"Cristais insuficientes. Você tem {saldo} 💎"}
        novo = await conn.fetchval(
            "UPDATE characters SET crystals = crystals + $1 WHERE id = $2 RETURNING crystals",
            amount,
            character_id,
        )
        await conn.execute(
            "INSERT INTO crystal_transactions (character_id, amount, reason) VALUES ($1, $2, $3)",
            character_id,
            amount,
            reason,
        )
    return {"success": True, "balance": novo, "change": amount}


async def get_crystal_history(db: Db, character_id: int, limit: int = 10):
    return await db.fetch(
        "SELECT amount, reason, created_at FROM crystal_transactions "
        "WHERE character_id = $1 ORDER BY created_at DESC, id DESC LIMIT $2",
        character_id,
        limit,
    )


# ── VIP ──────────────────────────────────────────────────────
async def activate_vip(
    pool: asyncpg.Pool, character_id: int, days: int, is_founder: bool = False
) -> dict:
    """Ativa ou estende o VIP; os dias acumulam sobre a expiração vigente."""
    async with pool.acquire() as conn, conn.transaction():
        char = await conn.fetchrow(
            "SELECT vip_expires_at, is_founder FROM characters WHERE id = $1 FOR UPDATE",
            character_id,
        )
        if not char:
            return {"error": "Personagem não encontrado"}
        agora = datetime.now(UTC)
        atual = char["vip_expires_at"]
        base = atual if atual and atual > agora else agora
        expira = base + timedelta(days=days)
        await conn.execute(
            "UPDATE characters SET vip_expires_at = $1, is_founder = is_founder OR $2 "
            "WHERE id = $3",
            expira,
            is_founder,
            character_id,
        )
    return {
        "success": True,
        "expires_at": expira,
        "is_founder": is_founder or char["is_founder"],
    }


# ── cosméticos ───────────────────────────────────────────────
async def unlock_cosmetic(db: Db, character_id: int, cosmetic_key: str) -> dict:
    if not await db.fetchval("SELECT 1 FROM cosmetics_catalog WHERE key = $1", cosmetic_key):
        return {"error": "Cosmético não encontrado"}
    inserido = await db.fetchval(
        "INSERT INTO character_cosmetics (character_id, cosmetic_key) VALUES ($1, $2) "
        "ON CONFLICT DO NOTHING RETURNING 1",
        character_id,
        cosmetic_key,
    )
    if not inserido:
        return {"error": "Você já possui este cosmético"}
    return {"success": True, "cosmetic_key": cosmetic_key}


async def equip_cosmetic(db: Db, character_id: int, cosmetic_key: str) -> dict:
    tipo = await db.fetchval(
        "SELECT c.type FROM character_cosmetics cc "
        "JOIN cosmetics_catalog c ON c.key = cc.cosmetic_key "
        "WHERE cc.character_id = $1 AND cc.cosmetic_key = $2",
        character_id,
        cosmetic_key,
    )
    if tipo is None:
        return {"error": "Você não possui este cosmético"}
    coluna = COLUNA_POR_TIPO.get(tipo)
    if not coluna:
        return {"error": "Tipo de cosmético inválido"}
    await db.execute(
        f"UPDATE characters SET {coluna} = $1 WHERE id = $2", cosmetic_key, character_id
    )
    return {"success": True, "slot": tipo}


async def unequip_cosmetic(db: Db, character_id: int, slot: str) -> dict:
    coluna = COLUNA_POR_TIPO.get(slot)
    if not coluna:
        return {"error": "Slot inválido"}
    await db.execute(f"UPDATE characters SET {coluna} = NULL WHERE id = $1", character_id)
    return {"success": True}


async def get_character_cosmetics(db: Db, character_id: int):
    return await db.fetch(
        "SELECT cc.cosmetic_key, c.name, c.type, c.cost_crystals "
        "FROM character_cosmetics cc JOIN cosmetics_catalog c ON c.key = cc.cosmetic_key "
        "WHERE cc.character_id = $1 ORDER BY c.type, c.name",
        character_id,
    )


# ── textos de perfil ─────────────────────────────────────────
async def set_war_cry(db: Db, character_id: int, texto: str) -> dict:
    texto = texto.strip()
    if len(texto) > GRITO_MAX:
        return {"error": f"Grito de guerra muito longo (máx {GRITO_MAX} caracteres)"}
    await db.execute("UPDATE characters SET war_cry = $1 WHERE id = $2", texto, character_id)
    return {"success": True}


async def set_epitaph(db: Db, character_id: int, texto: str) -> dict:
    texto = texto.strip()
    if len(texto) > EPITAFIO_MAX:
        return {"error": f"Epitáfio muito longo (máx {EPITAFIO_MAX} caracteres)"}
    await db.execute("UPDATE characters SET epitaph = $1 WHERE id = $2", texto, character_id)
    return {"success": True}
