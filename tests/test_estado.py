import json

from ecos_rpg.engine.estado import EstadoCombate

from .conftest import inimigo


def test_ida_e_volta_preserva_tudo():
    est = EstadoCombate(terrain="glacial", phase="miniboss_2", section=2, room=5)
    est.definir_inimigo(inimigo(hp=321))
    est.p_effects = {"burn": {"duration": 2, "value": 0.05}}
    est.e_effects = {"freeze": {"duration": 1, "value": 0}}
    est.skill_cds = {"cura": 2}
    est.used_minibosses = ["a", "b"]
    est.imbue_element, est.imbue_dur = "ice", 2
    est.shield, est.atk_buff, est.atk_buff_dur = 40, 0.15, 3
    est.next_crit = est.phase_shifted = est.enemy_enraged = True
    est.await_elem, est.player_armorbreak, est.gold_earned = "magia_elemental", 4, 250

    volta = EstadoCombate.decode(est.encode())
    assert volta == est
    assert volta.enemy["max_hp"] == 321


def test_decode_aceita_dict_e_bytes():
    est = EstadoCombate(room=3)
    assert EstadoCombate.decode(json.loads(est.encode())).room == 3
    assert EstadoCombate.decode(est.encode().encode()).room == 3


def test_decode_de_lixo_devolve_estado_novo():
    for ruim in (None, "", "{", "[1, 2]", b"\xff", 42):
        assert EstadoCombate.decode(ruim) == EstadoCombate()


def test_decode_ignora_chaves_desconhecidas_e_converte_as_antigas():
    bruto = json.dumps({"room": 2, "_terrain": "giants", "_phase_shifted": True, "lixo": 1})
    est = EstadoCombate.decode(bruto)
    assert est.room == 2 and est.terrain == "giants" and est.phase_shifted


def test_definir_inimigo_reseta_efeitos_e_fase():
    est = EstadoCombate()
    est.e_effects = {"burn": {"duration": 1, "value": 0.1}}
    est.phase_shifted = est.enemy_enraged = True
    est.definir_inimigo(inimigo(hp=77))
    assert est.e_effects == {} and not est.phase_shifted and not est.enemy_enraged
    assert est.enemy["max_hp"] == 77 and est.in_combat and est.inimigo_vivo()


def test_instancias_nao_compartilham_dicts():
    a, b = EstadoCombate(), EstadoCombate()
    a.skill_cds["x"] = 1
    a.used_minibosses.append("y")
    assert b.skill_cds == {} and b.used_minibosses == []
