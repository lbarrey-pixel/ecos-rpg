import random

from ecos_rpg.engine import fluxo
from ecos_rpg.engine.estado import EstadoCombate
from ecos_rpg.engine.turno import resolver_turno

from .conftest import RngFixo, inimigo


def _em_luta(**kw) -> EstadoCombate:
    est = EstadoCombate(terrain="lava")
    est.definir_inimigo(inimigo(**kw))
    return est


# ── turno ────────────────────────────────────────────────────
def test_ataque_fere_e_inimigo_reage(guerreiro):
    est = _em_luta(hp=500, damage=20)
    r = resolver_turno(guerreiro, est, 200, 60, "attack", RngFixo(0.0))
    assert r.desfecho == "continua"
    assert est.enemy["hp"] == 500 - 37
    assert r.hp == 200 - 20


def test_ataque_letal_nao_da_chance_de_revide(guerreiro):
    est = _em_luta(hp=10)
    r = resolver_turno(guerreiro, est, 200, 60, "attack", RngFixo(0.0))
    assert r.desfecho == "inimigo_morto" and r.hp == 200


def test_efeito_do_inimigo_mata_antes_do_revide(guerreiro):
    est = _em_luta(hp=40, damage=999)
    est.e_effects["poison"] = {"duration": 2, "value": 0.10}
    r = resolver_turno(guerreiro, est, 200, 60, "attack", RngFixo(0.0))
    # 40 - 37 = 3 de vida; o veneno (4) termina o serviço antes do revide
    assert r.desfecho == "inimigo_morto" and est.enemy["hp"] == 0 and r.hp == 200


def test_jogador_morre_no_dano_de_efeito(guerreiro):
    est = _em_luta()
    est.p_effects["burn"] = {"duration": 2, "value": 0.5}
    r = resolver_turno(guerreiro, est, 100, 60, "attack", RngFixo(0.0))
    assert r.desfecho == "jogador_morto" and r.hp == 0 and est.enemy["hp"] == 100


def test_atordoado_perde_a_acao_mas_apanha(guerreiro):
    est = _em_luta(hp=500, damage=20)
    est.p_effects["stun"] = {"duration": 2, "value": 0}
    r = resolver_turno(guerreiro, est, 200, 60, "attack", RngFixo(0.0))
    assert est.enemy["hp"] == 500
    assert r.hp == 180 and any("não pode agir" in m for m in r.msgs)


def test_skill_invalida_nao_gasta_turno_nem_efeitos(guerreiro):
    est = _em_luta()
    est.p_effects["burn"] = {"duration": 2, "value": 0.1}
    r = resolver_turno(guerreiro, est, 200, 5, "sk_investida", RngFixo(0.0))
    assert r.desfecho == "invalida" and r.hp == 200
    assert est.p_effects["burn"]["duration"] == 2


def test_skill_de_cooldown_tambem_e_invalida(guerreiro):
    est = _em_luta()
    est.skill_cds["grito_guerra"] = 2
    assert resolver_turno(guerreiro, est, 200, 60, "sk_grito_guerra").desfecho == "invalida"


def test_acao_desconhecida_e_segunda_etapa_sem_pedido(guerreiro, bruxo):
    est = _em_luta()
    assert resolver_turno(guerreiro, est, 200, 60, "dance").desfecho == "invalida"
    assert resolver_turno(guerreiro, est, 200, 60, "imbue_fire").desfecho == "invalida"
    assert resolver_turno(bruxo, est, 200, 60, "elem_fire").desfecho == "invalida"
    est.await_elem = "magia_elemental"
    bruxo["class"] = "curandeiro"
    assert resolver_turno(bruxo, est, 100, 100, "elem_arcane").desfecho == "invalida"


def test_sem_inimigo():
    est = EstadoCombate()
    assert resolver_turno({"hp_max": 10}, est, 10, 0, "attack").desfecho == "sem_inimigo"


def test_fluxo_de_duas_etapas_da_magia_elemental(bruxo):
    bruxo["class"] = "curandeiro"
    est = _em_luta(hp=1000, damage=1)
    r = resolver_turno(bruxo, est, 100, 100, "sk_magia_elemental", RngFixo(0.0))
    assert r.desfecho == "escolha" and est.await_elem and r.mana == 100
    r = resolver_turno(bruxo, est, r.hp, r.mana, "elem_ice", RngFixo(0.0))
    assert r.desfecho == "continua" and est.await_elem is None and r.mana == 75
    assert est.enemy["hp"] < 1000


def test_cooldown_corre_a_cada_turno(guerreiro):
    est = _em_luta(hp=5000, damage=1)
    resolver_turno(guerreiro, est, 200, 60, "sk_grito_guerra", RngFixo(0.0))
    assert est.skill_cds["grito_guerra"] == 3  # 4 menos o tick do próprio turno


def test_fuga_com_sucesso_cobra_ouro_da_run(guerreiro):
    est = _em_luta()
    est.gold_earned, est.battles_won = 1000, 2
    r = resolver_turno(guerreiro, est, 200, 60, "flee", RngFixo(0.0))
    assert r.desfecho == "fugiu" and r.ouro_perdido == 50
    assert est.gold_earned == 950


def test_fuga_que_falha_custa_um_turno(guerreiro):
    est = _em_luta(damage=30)
    r = resolver_turno(guerreiro, est, 200, 60, "flee", RngFixo(0.99))
    assert r.desfecho == "continua" and r.hp == 170
    assert any("Fuga falhou" in m for m in r.msgs)


def test_atordoado_ainda_pode_fugir(guerreiro):
    est = _em_luta()
    est.p_effects["freeze"] = {"duration": 2, "value": 0}
    assert resolver_turno(guerreiro, est, 200, 60, "flee", RngFixo(0.0)).desfecho == "fugiu"


# ── fuga e perdas ────────────────────────────────────────────
def test_chance_de_fuga_tem_teto():
    assert fluxo.chance_fuga(0) == 0.40
    assert fluxo.chance_fuga(50) == 0.50
    assert fluxo.chance_fuga(10_000) == fluxo.FUGA_MAX


def test_custo_de_fuga_cresce_com_as_vitorias():
    custos = []
    for vitorias in (0, 4, 6, 8, 12):
        est = EstadoCombate(gold_earned=1000, battles_won=vitorias)
        custos.append(fluxo.tentar_fuga(est, 0, RngFixo(0.0)).ouro_perdido)
    assert custos == [50, 50, 80, 120, 200]
    assert custos == sorted(custos)


def test_equipamento_vinculado_nunca_se_perde():
    itens = [
        {"id": 1, "rarity": "common", "is_bound": True},
        {"id": 2, "rarity": "common", "is_bound": False},
    ]
    assert fluxo.equipamentos_perdidos(itens, RngFixo(0.0)) == [2]
    assert fluxo.equipamentos_perdidos(itens, RngFixo(0.999)) == []


def test_chance_de_perda_cai_com_a_raridade():
    rng = random.Random(11)
    taxa = {}
    for raridade in ("common", "rare", "legendary"):
        itens = [{"id": i, "rarity": raridade} for i in range(4000)]
        taxa[raridade] = len(fluxo.equipamentos_perdidos(itens, rng)) / 4000
    assert taxa["common"] > taxa["rare"] > taxa["legendary"]
    assert abs(taxa["common"] - 0.60) < 0.04


# ── progressão da run ────────────────────────────────────────
def test_run_completa_ate_o_boss_com_semente_fixa():
    rng = random.Random(42)
    est = EstadoCombate(terrain="chemical")
    visto = []
    for secao in (1, 2):
        for _ in range(fluxo.SALAS_POR_SECAO):
            assert fluxo.iniciar_sala(est, 10, rng) == "normal"
            v = fluxo.registrar_vitoria(est, rng)
            assert v.destino == "sala"
        assert fluxo.iniciar_sala(est, 10, rng) == "miniboss"
        visto.append(est.enemy["key"])
        v = fluxo.registrar_vitoria(est, rng)
        assert (v.destino, v.secao) == ("extracao", secao)
        if secao == 1:
            assert est.phase == "extraction_1" and est.section == 2
            fluxo.continuar_secao_2(est)
            assert est.phase == "combat" and est.room == 0
    assert est.phase == "extraction_2"
    assert len(set(visto)) == 2  # minibosses não se repetem na mesma run

    ouro_antes = est.gold_earned
    fluxo.iniciar_boss(est, 10, random.Random(1))
    v = fluxo.registrar_vitoria(est, rng)
    assert v.destino == "fim" and v.bonus == int((ouro_antes + v.ouro) * fluxo.BONUS_BOSS)
    assert est.phase == "done" and est.battles_won == 2 * (fluxo.SALAS_POR_SECAO + 1) + 1


def test_iniciar_sala_fora_da_fase_de_combate_nao_faz_nada():
    est = EstadoCombate(phase="extraction_1")
    assert fluxo.iniciar_sala(est, 10) is None and est.enemy is None


def test_o_fim_espera_confirmacao():
    rng = random.Random()
    rng.random = lambda: 0.0
    est = EstadoCombate(terrain="lava")
    assert fluxo.iniciar_boss(est, 10, rng) is True
    assert est.phase == "boss" and not est.in_combat and est.enemy["key"] == "o_fim"
    assert est.enemy["flavor"]  # a tela de aviso usa o texto do tier


def test_vitoria_zera_efeitos_do_inimigo():
    est = _em_luta()
    est.e_effects = {"burn": {"duration": 3, "value": 0.1}}
    fluxo.registrar_vitoria(est, RngFixo(0.0))
    assert est.e_effects == {} and not est.in_combat and est.gold_earned == 5
