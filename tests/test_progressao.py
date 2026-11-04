from datetime import UTC, datetime, timedelta

import pytest

from ecos_rpg.engine import progressao as p
from ecos_rpg.engine.cosmeticos import CATALOGO, COLUNA_POR_TIPO, nome_exibicao

BIGINT_MAX = 2**63 - 1


def test_curva_de_xp_e_estritamente_crescente():
    valores = [p.xp_para_proximo(n) for n in range(1, p.NIVEL_MAX + 1)]
    assert valores[0] == 100
    assert all(b > a for a, b in zip(valores, valores[1:], strict=False))


def test_curva_cabe_em_bigint_mas_nao_em_int4():
    # é o motivo de experience_next ser BIGINT no schema
    assert p.xp_para_proximo(p.NIVEL_MAX) < BIGINT_MAX
    assert p.xp_para_proximo(p.NIVEL_MAX) > 2**31


def test_xp_total_e_a_soma_dos_degraus():
    assert p.xp_total_do_nivel(1) == 0
    assert p.xp_total_do_nivel(4) == sum(p.xp_para_proximo(n) for n in (1, 2, 3))


def test_xp_sem_subir_de_nivel():
    r = p.aplicar_xp(1, 0, 100, 40)
    assert (r.nivel, r.xp, r.xp_proximo, r.subiu, r.pontos_ganhos) == (1, 40, 100, False, 0)


def test_xp_sobe_varios_niveis_em_cascata():
    ganho = p.xp_total_do_nivel(5) + 7
    r = p.aplicar_xp(1, 0, 100, ganho)
    assert r.nivel == 5 and r.xp == 7 and r.niveis_ganhos == 4
    assert r.pontos_ganhos == 4 * p.PONTOS_POR_NIVEL
    assert r.xp_proximo == p.xp_para_proximo(5)
    assert r.bonus("hp_max") == 16 and r.bonus("attack") == 4


def test_nivel_maximo_nao_passa_de_99():
    r = p.aplicar_xp(98, 0, p.xp_para_proximo(98), p.xp_total_do_nivel(99) * 10)
    assert r.nivel == p.NIVEL_MAX


def test_xp_exato_no_limite_sobe():
    assert p.aplicar_xp(1, 0, 100, 100).nivel == 2


def test_reembolso_so_lista_stats_alocados():
    char = {"sp_forca": 3, "sp_sorte": 0, "sp_vitalidade": 1}
    assert p.reembolso_de_pontos(char) == {"forca": 3, "vitalidade": 1}


def test_vip_acumula_regras_de_expiracao():
    agora = datetime(2026, 1, 1, tzinfo=UTC)
    assert not p.vip_ativo(None, agora)
    assert p.vip_ativo(agora + timedelta(days=1), agora)
    assert not p.vip_ativo(agora - timedelta(seconds=1), agora)
    assert p.multiplicador_ouro(agora + timedelta(days=1), agora) == pytest.approx(1.15)
    assert p.multiplicador_ouro(None, agora) == 1.0


def test_barra_de_xp():
    assert p.barra_xp(50, 100) == "[█████░░░░░] 50%"
    assert p.barra_xp(0, 100).startswith("[░")


def test_bloco_de_nivel_mostra_pontos_e_vip():
    agora = datetime(2026, 1, 1, tzinfo=UTC)
    char = {
        "level": 7,
        "experience": 10,
        "experience_next": 100,
        "status_points": 3,
        "vip_expires_at": agora + timedelta(days=5, hours=1),
        "is_founder": True,
    }
    txt = p.bloco_nivel(char, agora)
    assert "Nível *7*" in txt and "3 ponto(s)" in txt and "5 dias" in txt and "🌑" in txt


def test_stats_alocaveis_mapeiam_colunas_validas():
    assert set(p.STAT_EFFECT) == set(p.STAT_LABELS)
    colunas = {v["col"] for v in p.STAT_EFFECT.values()}
    assert colunas == {"hp_max", "mana_max", "attack", "defense", "luck", "spirituality"}


def test_nome_de_exibicao_com_cosmeticos():
    char = {
        "name": "Kael",
        "cosmetic_aura": "aura_fogo",
        "cosmetic_title": "title_implacavel",
        "cosmetic_insignia": "insignia_espada",
    }
    assert nome_exibicao(char) == "🔥 *O Implacável* | Kael ⚔️"
    assert nome_exibicao({"name": "Kael"}) == "Kael"
    assert nome_exibicao({"name": "Kael", "cosmetic_aura": "inexistente"}) == "Kael"


def test_catalogo_de_cosmeticos_e_consistente():
    for chave, c in CATALOGO.items():
        assert c["type"] in COLUNA_POR_TIPO, chave
        assert chave.startswith(c["type"] + "_"), chave
        assert c["cost_crystals"] is None or c["cost_crystals"] > 0
        assert (c["cost_crystals"] is None) == c["is_founder"]
