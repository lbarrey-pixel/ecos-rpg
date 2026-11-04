"""Catálogo de inimigos, escala por nível e sorteio por terreno.

Os dados vivem em ``bestiario/`` (um módulo por terreno). Aqui só entra o que precisa
de código: tiers, escala e seleção. Dentro de um tier cada stat cresce 7% por nível
acima do piso do tier.
"""

from __future__ import annotations

import copy
import random

from .bestiario import chefes, gigantes, glacial, lava, quimica

TIER_RANGES = {1: (1, 15), 2: (16, 30), 3: (31, 99)}
ESCALA_POR_NIVEL = 0.07

_TERRENOS = {"lava": lava, "glacial": glacial, "chemical": quimica, "giants": gigantes}

ENEMIES: dict[str, dict] = {}
for _mod in _TERRENOS.values():
    ENEMIES.update(_mod.NORMAIS)
    ENEMIES.update(_mod.MINIBOSSES)
ENEMIES.update(chefes.CHEFES)
ENEMIES.update(chefes.ESPECIAIS)

NORMAL_BY_TERRAIN = {t: list(m.NORMAIS) for t, m in _TERRENOS.items()}
MINIBOSS_BY_TERRAIN = {t: list(m.MINIBOSSES) for t, m in _TERRENOS.items()}
BOSS_BY_TERRAIN = {dados["terrain"]: chave for chave, dados in chefes.CHEFES.items()}
BOSS_ESPECIAL = "o_fim"

# "undying" está no catálogo de O Fim mas ainda não tem efeito no motor (é ignorada).
# Habilidades que o turno do inimigo sabe executar. Serve de contrato entre o
# catálogo e ``combate.turno_inimigo``; o teste do catálogo confere.
HABILIDADES_CONHECIDAS = frozenset(
    {
        "burn",
        "freeze",
        "poison",
        "stun",
        "fear",
        "mana_drain",
        "armor_break",
        "multi_hit",
        "lifesteal",
        "regen",
        "shield",
        "phase_shift",
        "void_drain",
        "undying",
    }
)


def get_tier(player_level: int) -> int:
    for tier, (min_lv, max_lv) in TIER_RANGES.items():
        if min_lv <= player_level <= max_lv:
            return tier
    return 3


def scale(base: int, player_level: int) -> int:
    tier = get_tier(player_level)
    tier_min = TIER_RANGES[tier][0]
    return max(1, int(base * (1 + ESCALA_POR_NIVEL * (player_level - tier_min))))


def get_enemy_stats(enemy_key: str, player_level: int) -> dict:
    """Instância pronta para combate: stats escalados + habilidades do catálogo."""
    dados = ENEMIES[enemy_key]
    tier = get_tier(player_level)
    base = dados["tiers"][tier]
    return {
        "key": enemy_key,
        "name": dados["name"],
        "terrain": dados["terrain"],
        "type": dados["type"],
        "element": dados["element"],
        "tier": tier,
        "hp": scale(base["hp"], player_level),
        "damage": scale(base["damage"], player_level),
        "defense": scale(base["defense"], player_level),
        "xp": scale(base["xp"], player_level),
        "gold_min": scale(base["gold"][0], player_level),
        "gold_max": scale(base["gold"][1], player_level),
        "abilities": copy.deepcopy(dados.get("abilities", [])),
        "loot": list(dados.get("loot", [])),
        "flavor": base.get("flavor", ""),
    }


def roll_gold(enemy_stats: dict, rng: random.Random | None = None) -> int:
    rng = rng or random
    return rng.randint(enemy_stats["gold_min"], enemy_stats["gold_max"])


def pick_normal(terrain: str, player_level: int, rng: random.Random | None = None) -> dict:
    rng = rng or random
    return get_enemy_stats(rng.choice(NORMAL_BY_TERRAIN[terrain]), player_level)


def pick_miniboss(
    terrain: str,
    player_level: int,
    exclude: list[str] | None = None,
    rng: random.Random | None = None,
) -> dict:
    rng = rng or random
    pool = [k for k in MINIBOSS_BY_TERRAIN[terrain] if k not in (exclude or [])]
    return get_enemy_stats(rng.choice(pool), player_level)


def pick_boss(terrain: str, player_level: int, rng: random.Random | None = None) -> dict:
    """Boss do terreno, com uma chance pequena (por tier) de O Fim aparecer no lugar."""
    rng = rng or random
    tier = get_tier(player_level)
    if rng.random() < ENEMIES[BOSS_ESPECIAL]["spawn_chance"][tier]:
        return get_enemy_stats(BOSS_ESPECIAL, player_level)
    return get_enemy_stats(BOSS_BY_TERRAIN[terrain], player_level)
