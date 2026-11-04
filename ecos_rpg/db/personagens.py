"""Jogadores, personagens, ouro e progressão (XP e pontos de status)."""

from __future__ import annotations

import asyncpg

from ..engine import progressao
from ..engine.progressao import STAT_EFFECT

Db = asyncpg.Pool | asyncpg.Connection


async def get_or_create_player(db: Db, telegram_id: int, username: str):
    return await db.fetchrow(
        """
        INSERT INTO players (id, username) VALUES ($1, $2)
        ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
        RETURNING *
        """,
        telegram_id,
        username,
    )


async def get_character(db: Db, player_id: int):
    return await db.fetchrow("SELECT * FROM characters WHERE player_id = $1", player_id)


async def create_character(db: Db, player_id: int, name: str, class_key: str, stats: dict):
    return await db.fetchrow(
        """
        INSERT INTO characters
            (player_id, name, class, hp_max, hp_current, mana_max, mana_current,
             attack, defense, spirituality, luck, carry_capacity, safe_slots)
        VALUES ($1, $2, $3, $4, $4, $5, $5, $6, $7, $8, $9, $10, $11)
        RETURNING *
        """,
        player_id,
        name,
        class_key,
        stats["hp_max"],
        stats["mana_max"],
        stats["attack"],
        stats["defense"],
        stats["spirituality"],
        stats["luck"],
        stats["carry_capacity"],
        stats["safe_slots"],
    )


async def update_gold(db: Db, character_id: int, amount: int):
    return await db.fetchrow(
        "UPDATE characters SET gold = GREATEST(0, gold + $1) WHERE id = $2 RETURNING gold",
        amount,
        character_id,
    )


async def restore_hp_mana(db: Db, character_id: int) -> None:
    await db.execute(
        "UPDATE characters SET hp_current = hp_max, mana_current = mana_max WHERE id = $1",
        character_id,
    )


async def add_experience(pool: asyncpg.Pool, character_id: int, xp: int) -> dict:
    """Soma XP e aplica os bônus de nível numa transação (a linha fica travada)."""
    async with pool.acquire() as conn, conn.transaction():
        char = await conn.fetchrow(
            "SELECT level, experience, experience_next FROM characters WHERE id = $1 FOR UPDATE",
            character_id,
        )
        if not char:
            return {"error": "Personagem não encontrado"}
        r = progressao.aplicar_xp(char["level"], char["experience"], char["experience_next"], xp)
        hp, mana = r.bonus("hp_max"), r.bonus("mana_max")
        await conn.execute(
            """
            UPDATE characters SET
                experience = $1, experience_next = $2, level = $3,
                status_points = status_points + $4,
                hp_max = hp_max + $5, hp_current = LEAST(hp_current + $5, hp_max + $5),
                mana_max = mana_max + $6, mana_current = LEAST(mana_current + $6, mana_max + $6),
                attack = attack + $7, defense = defense + $8
            WHERE id = $9
            """,
            r.xp,
            r.xp_proximo,
            r.nivel,
            r.pontos_ganhos,
            hp,
            mana,
            r.bonus("attack"),
            r.bonus("defense"),
            character_id,
        )
    return {
        "xp_added": xp,
        "level": r.nivel,
        "leveled_up": r.subiu,
        "levels_gained": r.niveis_ganhos,
        "points_gained": r.pontos_ganhos,
        "hp_bonus": hp,
        "mana_bonus": mana,
    }


async def allocate_stat(pool: asyncpg.Pool, character_id: int, stat: str, points: int = 1) -> dict:
    # `stat` só chega ao SQL depois de passar pela lista branca STAT_EFFECT
    if stat not in STAT_EFFECT:
        return {"error": f"Stat inválido: {stat}"}
    if points < 1:
        return {"error": "Quantidade inválida"}
    coluna = STAT_EFFECT[stat]["col"]
    ganho = STAT_EFFECT[stat]["value"] * points
    async with pool.acquire() as conn, conn.transaction():
        char = await conn.fetchrow(
            "SELECT status_points FROM characters WHERE id = $1 FOR UPDATE",
            character_id,
        )
        if not char:
            return {"error": "Personagem não encontrado"}
        if char["status_points"] < points:
            return {"error": f"Pontos insuficientes. Você tem {char['status_points']} ponto(s)."}
        novo = await conn.fetchrow(
            f"UPDATE characters SET status_points = status_points - $1, "
            f"sp_{stat} = sp_{stat} + $1, {coluna} = {coluna} + $2 "
            f"WHERE id = $3 RETURNING {coluna} AS valor, status_points",
            points,
            ganho,
            character_id,
        )
    return {
        "success": True,
        "stat": stat,
        "points_used": points,
        "new_value": novo["valor"],
        "points_left": novo["status_points"],
    }


async def reset_stat_points(
    pool: asyncpg.Pool, character_id: int, use_crystals: bool = False
) -> dict:
    """Devolve os pontos alocados e desfaz os bônus. Cobra ouro ou cristais."""
    async with pool.acquire() as conn, conn.transaction():
        char = await conn.fetchrow(
            "SELECT * FROM characters WHERE id = $1 FOR UPDATE", character_id
        )
        if not char:
            return {"error": "Personagem não encontrado"}
        if use_crystals and char["crystals"] < progressao.CUSTO_RESET_CRISTAIS:
            return {
                "error": f"Cristais insuficientes. Você tem {char['crystals']} 💎. "
                f"Necessário: {progressao.CUSTO_RESET_CRISTAIS} 💎"
            }
        if not use_crystals and char["gold"] < progressao.CUSTO_RESET_OURO:
            return {
                "error": f"Ouro insuficiente. Você tem {char['gold']} 🪙. "
                f"Necessário: {progressao.CUSTO_RESET_OURO:,} 🪙"
            }

        alocados = progressao.reembolso_de_pontos(dict(char))
        if not alocados:
            return {"error": "Você não tem pontos alocados para resetar."}

        # nomes de coluna vêm de STAT_EFFECT; valores seguem como parâmetros
        sets, args = ["status_points = status_points + $1"], [sum(alocados.values())]
        for stat, pts in alocados.items():
            args.append(STAT_EFFECT[stat]["value"] * pts)
            sets.append(f"{STAT_EFFECT[stat]['col']} = {STAT_EFFECT[stat]['col']} - ${len(args)}")
        sets += [f"sp_{s} = 0" for s in STAT_EFFECT]
        if use_crystals:
            args.append(progressao.CUSTO_RESET_CRISTAIS)
            sets.append(f"crystals = crystals - ${len(args)}")
        else:
            args.append(progressao.CUSTO_RESET_OURO)
            sets.append(f"gold = gold - ${len(args)}")
        args.append(character_id)
        await conn.execute(
            f"UPDATE characters SET {', '.join(sets)} WHERE id = ${len(args)}", *args
        )
        if use_crystals:
            await conn.execute(
                "INSERT INTO crystal_transactions (character_id, amount, reason) "
                "VALUES ($1, $2, 'stat_reset')",
                character_id,
                -progressao.CUSTO_RESET_CRISTAIS,
            )
    return {
        "success": True,
        "points_back": sum(alocados.values()),
        "paid_with": "crystals" if use_crystals else "gold",
    }
