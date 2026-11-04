"""Inventário: baú, mochila da run, bolsos seguros e equipamentos."""

from __future__ import annotations

import asyncpg

from ..config import EQUIP_SLOTS

Db = asyncpg.Pool | asyncpg.Connection

LOCAIS = ("bau", "mochila", "bolso_seguro", "equipado")
EMPILHAVEIS_EXCLUIDOS = ("weapon", "armor", "accessory")


async def get_inventory(db: Db, character_id: int, location: str | None = None):
    if location:
        return await db.fetch(
            "SELECT * FROM inventory WHERE character_id = $1 AND location = $2 ORDER BY id",
            character_id,
            location,
        )
    return await db.fetch(
        "SELECT * FROM inventory WHERE character_id = $1 ORDER BY location, id",
        character_id,
    )


async def get_inventory_count(db: Db, character_id: int) -> dict[str, int]:
    rows = await db.fetch(
        "SELECT location, COUNT(*) AS total FROM inventory "
        "WHERE character_id = $1 GROUP BY location",
        character_id,
    )
    contagem = dict.fromkeys(LOCAIS, 0)
    contagem.update({r["location"]: r["total"] for r in rows})
    return contagem


async def get_equipped_items(db: Db, character_id: int):
    return await db.fetch(
        "SELECT * FROM inventory WHERE character_id = $1 AND location = 'equipado'",
        character_id,
    )


async def add_item(
    db: Db,
    character_id: int,
    item_name: str,
    item_type: str,
    rarity: str = "common",
    element: str | None = None,
    quantity: int = 1,
    location: str = "bau",
    equip_slot: str | None = None,
    durability_max: int | None = None,
):
    """Consumíveis e materiais empilham no mesmo local; equipamento é sempre uma linha nova."""
    if item_type not in EMPILHAVEIS_EXCLUIDOS:
        existente = await db.fetchrow(
            "SELECT id FROM inventory WHERE character_id = $1 AND item_name = $2 AND location = $3",
            character_id,
            item_name,
            location,
        )
        if existente:
            return await db.fetchrow(
                "UPDATE inventory SET quantity = quantity + $1 WHERE id = $2 RETURNING *",
                quantity,
                existente["id"],
            )
    return await db.fetchrow(
        """
        INSERT INTO inventory
            (character_id, item_name, item_type, element, rarity, quantity,
             location, equip_slot, durability_current, durability_max)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
        RETURNING *
        """,
        character_id,
        item_name,
        item_type,
        element,
        rarity,
        quantity,
        location,
        equip_slot,
        durability_max,
    )


async def remove_item(db: Db, item_id: int, quantity: int = 1) -> None:
    await db.execute(
        """
        WITH alvo AS (SELECT id, quantity FROM inventory WHERE id = $1 FOR UPDATE),
             apagado AS (DELETE FROM inventory USING alvo
                         WHERE inventory.id = alvo.id AND alvo.quantity <= $2)
        UPDATE inventory SET quantity = quantity - $2
        WHERE id = $1 AND quantity > $2
        """,
        item_id,
        quantity,
    )


async def move_item(db: Db, item_id: int, new_location: str):
    return await db.fetchrow(
        "UPDATE inventory SET location = $1 WHERE id = $2 RETURNING *",
        new_location,
        item_id,
    )


async def equip_item(pool: asyncpg.Pool, character_id: int, item_id: int, equip_slot: str):
    """Equipa no slot; o item que já estava lá volta para o baú. Escopo: só este personagem."""
    if equip_slot not in EQUIP_SLOTS:
        return None
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "UPDATE inventory SET location = 'bau' "
            "WHERE character_id = $1 AND location = 'equipado' AND equip_slot = $2",
            character_id,
            equip_slot,
        )
        return await conn.fetchrow(
            "UPDATE inventory SET location = 'equipado', equip_slot = $1 "
            "WHERE id = $2 AND character_id = $3 RETURNING *",
            equip_slot,
            item_id,
            character_id,
        )


async def unequip_item(db: Db, character_id: int, item_id: int):
    return await db.fetchrow(
        "UPDATE inventory SET location = 'bau' " "WHERE id = $1 AND character_id = $2 RETURNING *",
        item_id,
        character_id,
    )


async def update_durability(db: Db, item_id: int, amount: int):
    return await db.fetchrow(
        "UPDATE inventory SET durability_current = GREATEST(0, durability_current + $1) "
        "WHERE id = $2 RETURNING *",
        amount,
        item_id,
    )


async def bind_item(db: Db, item_id: int):
    return await db.fetchrow(
        "UPDATE inventory SET is_bound = TRUE WHERE id = $1 RETURNING *", item_id
    )


async def unbind_all(db: Db, character_id: int) -> None:
    await db.execute("UPDATE inventory SET is_bound = FALSE WHERE character_id = $1", character_id)


async def clear_run_loot(db: Db, character_id: int) -> None:
    """Morte: o que está na mochila se perde. Bolsos seguros ficam."""
    await db.execute(
        "DELETE FROM inventory WHERE character_id = $1 AND location = 'mochila'",
        character_id,
    )


async def transfer_loot_to_bau(db: Db, character_id: int) -> None:
    await db.execute(
        "UPDATE inventory SET location = 'bau' "
        "WHERE character_id = $1 AND location IN ('mochila', 'bolso_seguro')",
        character_id,
    )
