import copy
import random

import pytest

from ecos_rpg.engine import combate, habilidades
from ecos_rpg.engine.estado import EstadoCombate

from .conftest import RngFixo, inimigo


@pytest.fixture
def luta():
    est = EstadoCombate(terrain="lava")
    est.definir_inimigo(inimigo(hp=1000, defense=0))
    return est


def test_toda_classe_tem_cinco_skills_existentes():
    for classe, chaves in habilidades.CLASS_SKILLS.items():
        assert len(chaves) == 5
        for chave in chaves:
            assert habilidades.SKILLS[chave]["class"] == classe


def test_skill_sem_mana_nao_executa(guerreiro, luta):
    hp, mana, msgs = habilidades.executar("investida", guerreiro, luta, 100, 5)
    assert (hp, mana) == (100, 5)
    assert "Mana insuficiente" in msgs[0]
    assert luta.enemy["hp"] == 1000


def test_skill_de_outra_classe_e_recusada(guerreiro, luta):
    _, mana, msgs = habilidades.executar("bola_fogo", guerreiro, luta, 100, 100)
    assert mana == 100 and "outra classe" in msgs[0]


def test_cooldown_bloqueia_ate_expirar(guerreiro, luta):
    rng = RngFixo(0.0)
    _, mana, _ = habilidades.executar("grito_guerra", guerreiro, luta, 100, 60, rng=rng)
    assert mana == 30
    assert luta.skill_cds["grito_guerra"] == 4
    assert "fear" in luta.e_effects
    _, mana, msgs = habilidades.executar("grito_guerra", guerreiro, luta, 100, mana, rng=rng)
    assert mana == 30 and "cooldown" in msgs[0]
    for _ in range(4):
        combate.tick_buffs(luta)
    assert habilidades.validar("grito_guerra", luta, 60, "guerreiro") is None


def test_investida_atordoa_conforme_a_chance(guerreiro, luta):
    habilidades.executar("investida", guerreiro, luta, 100, 60, rng=RngFixo(0.0))
    assert "stun" in luta.e_effects
    outro = EstadoCombate(terrain="lava")
    outro.definir_inimigo(inimigo(hp=1000))
    habilidades.executar("investida", guerreiro, outro, 100, 60, rng=RngFixo(0.99))
    assert "stun" not in outro.e_effects


def test_buffs_de_ataque_e_defesa(guerreiro, luta):
    habilidades.executar("muralha_ferro", guerreiro, luta, 100, 60)
    assert (luta.def_buff, luta.def_buff_dur) == (0.40, 2)
    habilidades.executar("bravura", guerreiro, luta, 100, 60)
    assert (luta.atk_buff, luta.atk_buff_dur) == (0.15, 3)


def test_cura_nao_passa_do_maximo(bruxo, luta):
    bruxo["class"] = "curandeiro"
    hp, mana, _ = habilidades.executar("cura", bruxo, luta, 95, 100)
    assert hp == 100 and mana == 80


def test_escudo_sagrado_usa_80pct_da_espiritualidade(bruxo, luta):
    bruxo["class"] = "curandeiro"
    habilidades.executar("escudo_sagrado", bruxo, luta, 100, 100)
    assert luta.shield == int(55 * 0.8)
    assert luta.skill_cds["escudo_sagrado"] == 3


def test_magia_elemental_em_duas_etapas_sem_tocar_no_catalogo(bruxo, luta):
    bruxo["class"] = "curandeiro"
    antes = copy.deepcopy(habilidades.SKILLS)
    hp, mana, msgs = habilidades.executar("magia_elemental", bruxo, luta, 100, 100)
    # etapa 1: pede o elemento e devolve a mana
    assert mana == 100 and luta.await_elem == "magia_elemental"
    assert luta.enemy["hp"] == 1000 and "Escolha" in msgs[0]
    # etapa 2: o elemento chega como argumento
    hp, mana, msgs = habilidades.escolher_elemento(luta, bruxo, "ice", hp, mana, rng=RngFixo(0.0))
    assert luta.await_elem is None and mana == 75
    assert luta.enemy["hp"] < 1000
    assert "ice" in msgs[0]
    assert habilidades.SKILLS == antes
    assert "_tmp" not in habilidades.SKILLS


def test_elemento_muda_o_dano_pelo_terreno(bruxo):
    bruxo["class"] = "curandeiro"
    resultados = {}
    for elemento in ("fire", "ice"):
        est = EstadoCombate(terrain="lava")
        est.definir_inimigo(inimigo(hp=1000))
        habilidades.executar("magia_elemental", bruxo, est, 100, 100, elemento=elemento)
        resultados[elemento] = 1000 - est.enemy["hp"]
    assert resultados["ice"] > resultados["fire"]


def test_embeber_flecha_cobra_mana_so_na_segunda_etapa(guerreiro, luta):
    guerreiro["class"] = "arqueiro"
    _, mana, _ = habilidades.executar("embeber_flecha", guerreiro, luta, 100, 50)
    assert mana == 50 and luta.await_imbue
    mana, _ = habilidades.imbuir(luta, "fire", mana)
    assert mana == 30 and luta.imbue_element == "fire" and luta.imbue_dur == 3
    assert not luta.await_imbue


def test_olho_de_aguia_arma_o_critico(guerreiro, luta):
    guerreiro["class"] = "arqueiro"
    habilidades.executar("olho_aguia", guerreiro, luta, 100, 50)
    assert luta.next_crit and luta.skill_cds["olho_aguia"] == 4


def test_tempestade_sorteia_elemento_com_a_semente(bruxo, luta):
    _, _, msgs = habilidades.executar("tempestade", bruxo, luta, 100, 100, rng=random.Random(1))
    assert "Elemento sorteado" in msgs[0]


def test_revitalizar_restaura_mana_ate_o_teto(bruxo, luta):
    bruxo["class"] = "curandeiro"
    _, mana, _ = habilidades.executar("revitalizar", bruxo, luta, 100, 150)
    assert mana == 160


def test_luz_sagrada_fere_e_cura(bruxo, luta):
    bruxo["class"] = "paladino"
    hp, _, _ = habilidades.executar("luz_sagrada", bruxo, luta, 50, 100)
    assert hp > 50 and luta.enemy["hp"] < 1000
