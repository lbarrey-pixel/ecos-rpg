import random

import pytest

from ecos_rpg.config import TERRAINS
from ecos_rpg.engine import inimigos as ini


def test_todo_inimigo_tem_os_tres_tiers_e_campos_obrigatorios():
    assert ini.ENEMIES
    for chave, e in ini.ENEMIES.items():
        assert set(e["tiers"]) == {1, 2, 3}, chave
        assert e["type"] in {"normal", "miniboss", "boss", "boss_special"}, chave
        for t in e["tiers"].values():
            assert t["hp"] > 0 and t["damage"] > 0 and t["xp"] > 0, chave
            assert t["gold"][0] <= t["gold"][1], chave


def test_habilidades_do_catalogo_sao_todas_conhecidas_pelo_motor():
    usadas = {a["type"] for e in ini.ENEMIES.values() for a in e.get("abilities", [])}
    assert usadas <= ini.HABILIDADES_CONHECIDAS, usadas - ini.HABILIDADES_CONHECIDAS


def test_cada_terreno_tem_pool_suficiente_e_um_boss():
    for terreno in TERRAINS:
        assert len(ini.NORMAL_BY_TERRAIN[terreno]) >= 3
        # duas seções, um miniboss por seção, sem repetir
        assert len(ini.MINIBOSS_BY_TERRAIN[terreno]) >= 2
        assert ini.BOSS_BY_TERRAIN[terreno] in ini.ENEMIES


def test_tiers_por_nivel():
    assert [ini.get_tier(n) for n in (1, 15, 16, 30, 31, 99)] == [1, 1, 2, 2, 3, 3]


def test_escala_cresce_7pct_por_nivel_dentro_do_tier():
    assert ini.scale(100, 1) == 100
    assert ini.scale(100, 11) == 170
    assert ini.scale(100, 16) == 100  # tier novo recomeça do piso
    assert ini.scale(1, 1) >= 1


def test_instancia_de_combate_vem_escalada_e_completa():
    e = ini.get_enemy_stats("salamandra", 10)
    base = ini.ENEMIES["salamandra"]["tiers"][1]
    assert e["hp"] == ini.scale(base["hp"], 10) > base["hp"]
    assert e["key"] == "salamandra" and e["tier"] == 1 and e["abilities"]
    assert e["gold_min"] <= e["gold_max"]


def test_instancia_nao_compartilha_habilidades_com_o_catalogo():
    e = ini.get_enemy_stats("salamandra", 1)
    e["abilities"].append({"type": "x"})
    assert {"type": "x"} not in ini.ENEMIES["salamandra"]["abilities"]


def test_miniboss_respeita_a_exclusao():
    rng = random.Random(3)
    pool = ini.MINIBOSS_BY_TERRAIN["lava"]
    for _ in range(30):
        e = ini.pick_miniboss("lava", 5, exclude=pool[:-1], rng=rng)
        assert e["key"] == pool[-1]


def test_boss_do_terreno_ou_o_fim():
    sempre_fim = random.Random()
    sempre_fim.random = lambda: 0.0
    assert ini.pick_boss("lava", 5, sempre_fim)["key"] == ini.BOSS_ESPECIAL
    nunca = random.Random()
    nunca.random = lambda: 0.999
    assert ini.pick_boss("lava", 5, nunca)["key"] == ini.BOSS_BY_TERRAIN["lava"]


def test_chance_do_fim_cresce_com_o_tier():
    chances = ini.ENEMIES[ini.BOSS_ESPECIAL]["spawn_chance"]
    assert chances[1] < chances[2] < chances[3] < 0.05


@pytest.mark.parametrize("chave", ["golem_fragmentado"])
def test_ouro_dentro_da_faixa(chave):
    e = ini.get_enemy_stats(chave, 3)
    rng = random.Random(1)
    assert all(e["gold_min"] <= ini.roll_gold(e, rng) <= e["gold_max"] for _ in range(50))
