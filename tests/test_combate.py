from ecos_rpg.engine import combate
from ecos_rpg.engine.estado import EstadoCombate

from .conftest import RngFixo, inimigo


def _estado(**kw) -> EstadoCombate:
    est = EstadoCombate(terrain=kw.pop("terrain", "lava"))
    est.definir_inimigo(inimigo(**kw))
    return est


def test_dano_magico_aplica_modificador_de_terreno(bruxo):
    alvo = {"magic_resist": 0}
    # espiritualidade 55 + 10 * 0.8 = 63
    assert combate.dano_magico(bruxo, alvo, "arcane", "lava") == 63
    assert combate.dano_magico(bruxo, alvo, "fire", "lava") == int(63 * 0.60)
    assert combate.dano_magico(bruxo, alvo, "ice", "lava") == int(63 * 1.40)
    assert combate.dano_magico(bruxo, alvo, "fire", "glacial") == int(63 * 1.40)
    assert combate.dano_magico(bruxo, alvo, "poison", "giants") == int(63 * 1.35)


def test_pontos_alocados_escalam_o_dano(bruxo, guerreiro):
    base = combate.dano_fisico(guerreiro, {"defense": 0}, _estado())
    guerreiro["sp_forca"] = 10
    assert combate.dano_fisico(guerreiro, {"defense": 0}, _estado()) == base + 30
    base_m = combate.dano_magico(bruxo, {}, "arcane", "lava")
    bruxo["sp_espiritualidade"] = 10
    assert combate.dano_magico(bruxo, {}, "arcane", "lava") == base_m + 35


def test_dano_fisico_desconta_defesa_e_nunca_zera(guerreiro):
    est = _estado()
    # 32 + 5 = 37; defesa 20 * 0.55 = 11
    assert combate.dano_fisico(guerreiro, {"defense": 20}, est) == 26
    assert combate.dano_fisico(guerreiro, {"defense": 9999}, est) == 1


def test_critico_vale_uma_vez(guerreiro):
    est = _estado()
    est.next_crit = True
    normal = combate.dano_fisico(guerreiro, {"defense": 0}, _estado())
    assert combate.dano_fisico(guerreiro, {"defense": 0}, est) == int(37 * combate.CRIT_MULT)
    assert est.next_crit is False
    assert combate.dano_fisico(guerreiro, {"defense": 0}, est) == normal


def test_flecha_imbuida_soma_dano_magico_e_expira(guerreiro):
    est = _estado()
    est.imbue_element, est.imbue_dur = "ice", 2
    alvo = {"defense": 0}
    seco = combate.dano_fisico(guerreiro, alvo, _estado())
    extra = int(combate.dano_magico(guerreiro, alvo, "ice", "lava") * 0.5)
    assert combate.dano_fisico(guerreiro, alvo, est) == seco + extra
    combate.dano_fisico(guerreiro, alvo, est)
    assert est.imbue_element is None and est.imbue_dur == 0


def test_escudo_passivo_do_inimigo_reduz_dano_direto():
    est = _estado(abilities=[{"type": "shield", "value": 0.25}])
    assert combate.ferir_inimigo(est, 40) == 30
    assert est.enemy["hp"] == 70
    # dano mínimo de 1 quando há dano
    assert combate.ferir_inimigo(est, 1) == 1


def test_veneno_do_inimigo_ignora_escudo_passivo():
    est = _estado(abilities=[{"type": "shield", "value": 0.5}])
    est.e_effects["poison"] = {"duration": 2, "value": 0.05}
    total, msgs = combate.tick_efeitos_inimigo(est)
    assert total == 5 and est.enemy["hp"] == 95 and msgs


def test_efeitos_expiram_pela_duracao():
    est = _estado()
    est.e_effects["burn"] = {"duration": 2, "value": 0.10}
    combate.tick_efeitos_inimigo(est)
    assert est.e_effects["burn"]["duration"] == 1
    combate.tick_efeitos_inimigo(est)
    assert est.e_effects == {}
    assert est.enemy["hp"] == 80


def test_tick_do_jogador_causa_dano_e_avisa_bloqueio():
    est = _estado()
    est.p_effects = {"burn": {"duration": 1, "value": 0.10}, "stun": {"duration": 2, "value": 0}}
    hp, msgs = combate.tick_efeitos_jogador(est, 100, 100)
    assert hp == 90
    assert any("atordoado" in m for m in msgs)
    assert "burn" not in est.p_effects and "stun" in est.p_effects
    assert est.bloqueado()


def test_mudanca_de_fase_enraivece_uma_unica_vez():
    est = _estado(
        damage=100,
        abilities=[{"type": "phase_shift", "hp_threshold": 0.5, "chance": 1.0}],
    )
    est.enemy["hp"] = 49
    rng = RngFixo(0.0)
    hp, _, msgs = combate.turno_inimigo(est, 1000, 0, rng)
    assert est.phase_shifted and est.enemy_enraged
    assert any("muda de fase" in m for m in msgs)
    # o dano base é fixado antes das habilidades: o golpe da virada ainda sai normal
    assert hp == 900
    hp2, _, msgs = combate.turno_inimigo(est, hp, 0, rng)
    assert not any("muda de fase" in m for m in msgs)
    assert hp2 == 900 - int(100 * combate.ENRAGE_MULT)


def test_fase_nao_muda_acima_do_limiar():
    est = _estado(abilities=[{"type": "phase_shift", "hp_threshold": 0.5, "chance": 1.0}])
    combate.turno_inimigo(est, 100, 0, RngFixo(0.0))
    assert not est.phase_shifted


def test_inimigo_congelado_pula_o_turno():
    est = _estado()
    est.e_effects["freeze"] = {"duration": 1, "value": 0}
    hp, _, msgs = combate.turno_inimigo(est, 100, 0, RngFixo(0.0))
    assert hp == 100 and "não pode agir" in msgs[0]


def test_armor_break_acumula_e_amplifica_dano():
    est = _estado(damage=100, abilities=[{"type": "armor_break", "chance": 1.0, "value": 2}])
    hp, _, _ = combate.turno_inimigo(est, 1000, 0, RngFixo(0.0))
    assert est.player_armorbreak == 2
    # 2 stacks * 8% sobre o dano base
    assert hp == 1000 - int(100 * (1 + 2 * combate.ARMORBREAK_POR_STACK))


def test_multi_hit_substitui_o_ataque_base():
    est = _estado(damage=60, abilities=[{"type": "multi_hit", "chance": 1.0}])
    rng = RngFixo(0.0)  # randint do random.Random continua determinístico (semente 0)
    hp, _, msgs = combate.turno_inimigo(est, 1000, 0, rng)
    assert 1000 - hp <= 60 and any("ataca" in m for m in msgs)
    assert not any("causa" in m and "de dano!" in m for m in msgs)


def test_lifesteal_cura_o_inimigo_a_partir_do_dano_causado():
    est = _estado(damage=100, abilities=[{"type": "lifesteal", "chance": 1.0, "value": 0.5}])
    est.enemy["hp"] = 50
    hp, _, _ = combate.turno_inimigo(est, 1000, 0, RngFixo(0.0))
    assert est.enemy["hp"] == 100 and hp == 900


def test_regen_cura_sem_passar_do_maximo():
    est = _estado(abilities=[{"type": "regen", "chance": 1.0, "value": 0.10}])
    est.enemy["hp"] = 95
    combate.turno_inimigo(est, 1000, 0, RngFixo(0.0))
    assert est.enemy["hp"] == 100


def test_escudo_do_jogador_absorve_e_explode():
    est = _estado(damage=50)
    est.shield = 30
    hp, _, msgs = combate.turno_inimigo(est, 100, 0, RngFixo(0.0))
    # 50 de dano: 30 absorvidos, 20 passam; o escudo devolve 30 ao inimigo
    assert hp == 80 and est.shield == 0 and est.enemy["hp"] == 70
    assert any("explode" in m for m in msgs)


def test_escudo_maior_que_o_dano_so_diminui():
    est = _estado(damage=10)
    est.shield = 25
    hp, _, _ = combate.turno_inimigo(est, 100, 0, RngFixo(0.0))
    assert hp == 100 and est.shield == 15 and est.enemy["hp"] == 100


def test_mana_drain_e_void_drain():
    est = _estado(
        damage=1,
        abilities=[
            {"type": "mana_drain", "chance": 1.0, "value": 10},
            {"type": "void_drain", "chance": 1.0, "value": 25},
        ],
    )
    hp, mana, _ = combate.turno_inimigo(est, 100, 40, RngFixo(0.0))
    assert mana == 5 and hp == 100 - 10 - 1


def test_buffs_e_cooldowns_decrementam():
    est = _estado()
    est.atk_buff, est.atk_buff_dur = 0.15, 1
    est.skill_cds = {"a": 2, "b": 1}
    combate.tick_buffs(est)
    assert est.atk_buff == 0.0 and est.skill_cds == {"a": 1}
