"""Progressão da run: salas, miniboss, janelas de extração, boss, fuga e morte.

Muta o ``EstadoCombate`` recebido e devolve só o que a camada de transporte precisa
para escolher a tela seguinte.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..config import EQUIPMENT_LOSS_CHANCE, get_flee_cost
from .estado import EstadoCombate
from .inimigos import BOSS_ESPECIAL, pick_boss, pick_miniboss, pick_normal, roll_gold

SALAS_POR_SECAO = 5
BONUS_BOSS = 0.10
FUGA_BASE = 0.40
FUGA_POR_SORTE = 0.002
FUGA_MAX = 0.85
PERDA_PADRAO = 0.30


def iniciar_sala(estado: EstadoCombate, nivel: int, rng: random.Random | None = None) -> str | None:
    """Sorteia o próximo inimigo. Devolve 'normal', 'miniboss' ou None se a fase não é de combate."""
    if estado.phase != "combat":
        return None
    if estado.room >= SALAS_POR_SECAO:
        estado.phase = "miniboss_1" if estado.section == 1 else "miniboss_2"
        inimigo = pick_miniboss(estado.terrain, nivel, exclude=estado.used_minibosses, rng=rng)
        estado.definir_inimigo(inimigo)
        estado.used_minibosses.append(inimigo["key"])
        return "miniboss"
    estado.definir_inimigo(pick_normal(estado.terrain, nivel, rng))
    estado.room += 1
    return "normal"


def iniciar_boss(estado: EstadoCombate, nivel: int, rng: random.Random | None = None) -> bool:
    """Põe o boss em cena. True se foi O Fim, que espera confirmação antes de lutar."""
    inimigo = pick_boss(estado.terrain, nivel, rng)
    estado.definir_inimigo(inimigo)
    estado.phase = "boss"
    especial = inimigo["key"] == BOSS_ESPECIAL
    if especial:
        estado.in_combat = False
    return especial


def continuar_secao_2(estado: EstadoCombate) -> None:
    estado.phase = "combat"
    estado.section = 2
    estado.room = 0


@dataclass(frozen=True)
class Vitoria:
    ouro: int
    destino: str  # "sala" | "extracao" | "fim"
    secao: int = 0  # seção exibida na janela de extração
    bonus: int = 0  # bônus de ouro por completar até o boss


def registrar_vitoria(estado: EstadoCombate, rng: random.Random | None = None) -> Vitoria:
    """Paga o ouro do inimigo morto e decide para onde a run segue."""
    ouro = roll_gold(estado.enemy, rng)
    estado.gold_earned += ouro
    estado.battles_won += 1
    estado.in_combat = False
    estado.e_effects = {}

    if estado.phase == "miniboss_1":
        estado.phase, estado.section, estado.room = "extraction_1", 2, 0
        return Vitoria(ouro, "extracao", secao=1)
    if estado.phase == "miniboss_2":
        estado.phase = "extraction_2"
        return Vitoria(ouro, "extracao", secao=2)
    if estado.phase == "boss":
        bonus = int(estado.gold_earned * BONUS_BOSS)
        estado.gold_earned += bonus
        estado.phase = "done"
        return Vitoria(ouro, "fim", bonus=bonus)
    return Vitoria(ouro, "sala")


def chance_fuga(sorte: int) -> float:
    return min(FUGA_MAX, FUGA_BASE + sorte * FUGA_POR_SORTE)


@dataclass(frozen=True)
class Fuga:
    ok: bool
    chance: float
    ouro_perdido: int = 0


def tentar_fuga(estado: EstadoCombate, sorte: int, rng: random.Random | None = None) -> Fuga:
    """Em caso de sucesso desconta do ouro da run um percentual que cresce com as vitórias."""
    rng = rng or random
    chance = chance_fuga(sorte)
    if rng.random() >= chance:
        return Fuga(False, chance)
    perdido = int(estado.gold_earned * get_flee_cost(estado.battles_won) / 100)
    estado.gold_earned = max(0, estado.gold_earned - perdido)
    return Fuga(True, chance, perdido)


def equipamentos_perdidos(equipados: list[dict], rng: random.Random | None = None) -> list[int]:
    """Ids dos itens equipados perdidos na morte. Item vinculado nunca se perde."""
    rng = rng or random
    perdidos = []
    for item in equipados:
        if item.get("is_bound"):
            continue
        if rng.random() < EQUIPMENT_LOSS_CHANCE.get(item["rarity"], PERDA_PADRAO):
            perdidos.append(item["id"])
    return perdidos
