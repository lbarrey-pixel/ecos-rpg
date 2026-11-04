import random
from collections import Counter

from ecos_rpg.engine import inimigos as ini
from ecos_rpg.engine import loot


def _rodar(chave, classe="guerreiro", luck=18, n=3000, semente=7):
    rng = random.Random(semente)
    inimigo = ini.get_enemy_stats(chave, 10)
    return [loot.generate_loot(inimigo, classe, luck, rng) for _ in range(n)]


def test_mesma_semente_mesmo_loot():
    assert _rodar("salamandra", n=50) == _rodar("salamandra", n=50)
    assert _rodar("salamandra", n=50, semente=1) != _rodar("salamandra", n=50, semente=2)


def test_limite_de_itens_por_tipo_de_inimigo():
    boss = ini.BOSS_BY_TERRAIN["lava"]
    mini = ini.MINIBOSS_BY_TERRAIN["lava"][0]
    for chave, teto in (("salamandra", 1), (mini, 2), (boss, 3)):
        assert max(len(d) for d in _rodar(chave, n=1500)) <= teto


def test_taxa_de_queda_do_inimigo_normal_perto_do_base():
    drops = _rodar("salamandra")
    taxa = sum(1 for d in drops if d) / len(drops)
    # material 45%; com consumível/equipamento/acessório a taxa de "algo" sobe um pouco
    assert 0.45 < taxa < 0.75


def test_boss_quase_sempre_derruba_algo():
    # a chance de queda tem teto de 95%, mesmo com base 100%
    boss = ini.BOSS_BY_TERRAIN["glacial"]
    drops = _rodar(boss, n=2000)
    taxa = sum(1 for d in drops if d) / len(drops)
    assert taxa > 0.93


def test_material_vem_do_terreno_do_inimigo():
    nomes = {m[0] for m in loot.TERRAIN_MATS["glacial"]}
    achados = {
        i["name"]
        for d in _rodar(
            "lobo_glacial" if "lobo_glacial" in ini.ENEMIES else ini.NORMAL_BY_TERRAIN["glacial"][0]
        )
        for i in d
        if i["type"] == "material"
    }
    assert achados and achados <= nomes


def test_equipamento_respeita_a_classe_e_o_slot():
    pecas = {
        "guerreiro": {i[0] for i in loot.CLASS_WEAPONS["guerreiro"] + loot.CLASS_ARMOR["guerreiro"]}
    }
    boss = ini.BOSS_BY_TERRAIN["giants"]
    equipados = [
        i for d in _rodar(boss, "guerreiro") for i in d if i["equip_slot"] in ("weapon", "armor")
    ]
    assert equipados
    assert all(i["name"] in pecas["guerreiro"] for i in equipados)
    assert all(i["type"] == i["equip_slot"] for i in equipados)


def test_boss_favorece_raridades_altas():
    boss = ini.BOSS_BY_TERRAIN["lava"]
    rng = random.Random(5)
    chefe = Counter(loot.pick_rarity("boss", rng) for _ in range(4000))
    comum = Counter(loot.pick_rarity("normal", rng) for _ in range(4000))
    assert chefe["epic"] + chefe["legendary"] > 5 * (comum["epic"] + comum["legendary"])
    assert comum["legendary"] == 0
    assert boss in ini.ENEMIES


def test_sorte_aumenta_a_chance_de_queda():
    baixa = sum(len(d) for d in _rodar("salamandra", luck=18))
    alta = sum(len(d) for d in _rodar("salamandra", luck=120))
    assert alta > baixa


def test_bonus_de_sorte_e_degrau_de_5_pontos_acima_de_20():
    assert loot.bonus_sorte(20) == 0.0
    assert loot.bonus_sorte(24) == 0.0
    assert loot.bonus_sorte(25) == 0.01
    assert loot.bonus_sorte(45) == 0.05
    assert loot.bonus_sorte(5) == 0.0


def test_chance_de_queda_tem_teto():
    # com sorte absurda o inimigo normal ainda pode não dropar (teto 95%)
    drops = _rodar("salamandra", luck=5000, n=2000)
    assert any(not any(i["type"] == "material" for i in d) for d in drops)
