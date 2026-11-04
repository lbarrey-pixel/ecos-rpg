"""Fórmulas de dano, efeitos de status e turno do inimigo.

Nada aqui conhece Telegram nem banco: recebe o personagem (dict com os stats), o
``EstadoCombate`` e devolve números e mensagens. Toda aleatoriedade passa por ``rng``
para os testes poderem fixar a semente.
"""

from __future__ import annotations

import random

from ..config import TERRAIN_MODIFIERS
from .estado import EstadoCombate

CRIT_MULT = 2.2
ENRAGE_MULT = 1.30
ARMORBREAK_POR_STACK = 0.08
EXPLOSAO_ESCUDO = 1.0

ICONES_EFEITO = {
    "burn": "🔥",
    "poison": "☠️",
    "freeze": "🧊",
    "stun": "⚡",
    "fear": "😱",
}


# ── atributos efetivos ───────────────────────────────────────
def ataque_efetivo(char: dict) -> float:
    return char.get("attack", 10) + char.get("sp_forca", 0) * 3


def espirito_efetivo(char: dict) -> float:
    return char.get("spirituality", 10) + char.get("sp_espiritualidade", 0) * 3.5


def sorte_efetiva(char: dict) -> int:
    return char.get("luck", 18) + char.get("sp_sorte", 0) * 2


# ── fórmulas ─────────────────────────────────────────────────
def dano_magico(attacker: dict, defender: dict, element: str, terrain: str) -> int:
    raw = espirito_efetivo(attacker) + attacker.get("level", 1) * 0.8
    final = max(1, int(raw - defender.get("magic_resist", 0) * 0.4))
    mod = TERRAIN_MODIFIERS.get(terrain, {}).get(element, 1.0)
    return int(final * mod)


def dano_fisico(attacker: dict, defender: dict, estado: EstadoCombate) -> int:
    """Consome o crítico pendente e um uso da flecha imbuída, se houver."""
    raw = ataque_efetivo(attacker) + attacker.get("level", 1) * 1.0
    raw = int(raw * (1 + estado.atk_buff))
    if estado.next_crit:
        estado.next_crit = False
        raw = int(raw * CRIT_MULT)
    final = max(1, int(raw - defender.get("defense", 0) * 0.55))

    if estado.imbue_element and estado.imbue_dur > 0:
        final += int(dano_magico(attacker, defender, estado.imbue_element, estado.terrain) * 0.5)
        estado.imbue_dur -= 1
        if estado.imbue_dur <= 0:
            estado.imbue_element = None
    return final


def cura(healer: dict, power: float) -> int:
    return int((espirito_efetivo(healer) + healer.get("level", 1) * 0.6) * power)


def escudo_inimigo(enemy: dict) -> float:
    """Fração de dano direto que o inimigo ignora (habilidade passiva ``shield``)."""
    for ab in enemy.get("abilities", []):
        if ab.get("type") == "shield":
            return ab.get("value", 0.0)
    return 0.0


def ferir_inimigo(estado: EstadoCombate, dano: int) -> int:
    """Aplica dano direto ao inimigo, descontado o escudo passivo. Retorna o dano real."""
    if not estado.enemy:
        return 0
    dano = max(1, int(dano * (1 - escudo_inimigo(estado.enemy)))) if dano > 0 else 0
    estado.enemy["hp"] = max(0, estado.enemy["hp"] - dano)
    return dano


# ── efeitos de status ────────────────────────────────────────
def _tick(efeitos: dict) -> None:
    """Decrementa a duração de cada efeito e remove os que expiraram."""
    for data in efeitos.values():
        data["duration"] -= 1
    for chave in [k for k, d in efeitos.items() if d["duration"] <= 0]:
        del efeitos[chave]


def aplicar_efeito(efeitos: dict, effect: dict, rng: random.Random | None = None) -> bool:
    rng = rng or random
    if rng.random() >= effect.get("chance", 1.0):
        return False
    efeitos[effect["type"]] = {
        "duration": effect.get("duration", 1),
        "value": effect.get("value", 0.05),
    }
    return True


def tick_efeitos_jogador(estado: EstadoCombate, hp: int, hp_max: int) -> tuple[int, list[str]]:
    msgs = []
    for eff, data in estado.p_effects.items():
        if eff in ("burn", "poison"):
            dmg = max(1, int(hp_max * data.get("value", 0.05)))
            hp = max(0, hp - dmg)
            msgs.append(f"{ICONES_EFEITO[eff]} {eff.capitalize()} causa {dmg} de dano!")
        elif eff in ("freeze", "stun"):
            nome = "congelado" if eff == "freeze" else "atordoado"
            msgs.append(f"{ICONES_EFEITO[eff]} Você está {nome} — não pode agir!")
    _tick(estado.p_effects)
    return hp, msgs


def tick_efeitos_inimigo(estado: EstadoCombate) -> tuple[int, list[str]]:
    """Dano de burn/poison no inimigo (ignora o escudo passivo: é dano por dentro)."""
    if not estado.enemy:
        return 0, []
    msgs, total = [], 0
    hp_max = estado.inimigo_hp_max()
    for eff, data in estado.e_effects.items():
        if eff in ("burn", "poison"):
            dmg = max(1, int(hp_max * data.get("value", 0.05)))
            total += dmg
            msgs.append(f"{ICONES_EFEITO[eff]} {eff.capitalize()} causa {dmg} no inimigo!")
    _tick(estado.e_effects)
    if total:
        estado.enemy["hp"] = max(0, estado.enemy["hp"] - total)
    return total, msgs


def tick_buffs(estado: EstadoCombate) -> None:
    if estado.atk_buff_dur > 0:
        estado.atk_buff_dur -= 1
        if estado.atk_buff_dur <= 0:
            estado.atk_buff = 0.0
    if estado.def_buff_dur > 0:
        estado.def_buff_dur -= 1
        if estado.def_buff_dur <= 0:
            estado.def_buff = 0.0
    for sk in list(estado.skill_cds):
        estado.skill_cds[sk] -= 1
        if estado.skill_cds[sk] <= 0:
            del estado.skill_cds[sk]


# ── turno do inimigo ─────────────────────────────────────────
def dano_recebido(base: int, estado: EstadoCombate) -> int:
    base = int(base * (1 - estado.def_buff))
    if estado.player_armorbreak:
        base = int(base * (1 + estado.player_armorbreak * ARMORBREAK_POR_STACK))
    return max(1, base)


def _absorver_escudo(estado: EstadoCombate, dano: int, msgs: list[str]) -> int:
    if estado.shield <= 0:
        return dano
    if dano >= estado.shield:
        explode = int(estado.shield * EXPLOSAO_ESCUDO)
        msgs.append(f"🛡️ Escudo absorve {estado.shield} e explode causando {explode} no inimigo!")
        estado.enemy["hp"] = max(0, estado.enemy["hp"] - explode)
        dano -= estado.shield
        estado.shield = 0
        return dano
    estado.shield -= dano
    msgs.append(f"🛡️ Escudo absorve {dano}. ({estado.shield} restante)")
    return 0


def turno_inimigo(
    estado: EstadoCombate, hp: int, mana: int, rng: random.Random | None = None
) -> tuple[int, int, list[str]]:
    """Executa habilidades (cada uma com a própria chance) e o ataque base."""
    rng = rng or random
    enemy = estado.enemy or {}
    nome = enemy.get("name", "?")
    msgs: list[str] = []

    for bloqueio in ("stun", "freeze", "fear"):
        if bloqueio in estado.e_effects:
            msgs.append(f"💤 {nome} não pode agir ({bloqueio})!")
            return hp, mana, msgs

    hp_max_inimigo = estado.inimigo_hp_max()
    dmg_base = int(enemy.get("damage", 10) * (ENRAGE_MULT if estado.enemy_enraged else 1.0))

    for ability in enemy.get("abilities", []):
        atype = ability.get("type", "")
        # shield é passivo (ver ferir_inimigo); lifesteal é resolvido junto do ataque base
        if not atype or atype in ("shield", "lifesteal"):
            continue
        if rng.random() > ability.get("chance", 0.5):
            continue

        if atype == "mana_drain":
            drain = ability.get("value", 10)
            mana = max(0, mana - drain)
            msgs.append(f"🔮 {nome} drena {drain} de mana!")
        elif atype in ("burn", "freeze", "poison", "stun"):
            if aplicar_efeito(estado.p_effects, {**ability, "chance": 1.0}, rng):
                msgs.append(f"{ICONES_EFEITO[atype]} {nome} aplica {atype}!")
        elif atype == "armor_break":
            stacks = ability.get("value", 2)
            estado.player_armorbreak += stacks
            msgs.append(f"💥 {nome} quebra sua armadura! (+{stacks} stacks)")
        elif atype == "regen":
            heal = max(1, int(hp_max_inimigo * ability.get("value", 0.05)))
            enemy["hp"] = min(hp_max_inimigo, enemy["hp"] + heal)
            msgs.append(f"💚 {nome} regenera {heal} HP!")
        elif atype == "multi_hit":
            hits = rng.randint(2, 3)
            per = max(1, dmg_base // hits)
            total = 0
            for _ in range(hits):
                golpe = _absorver_escudo(estado, dano_recebido(per, estado), msgs)
                hp = max(0, hp - golpe)
                total += golpe
            msgs.append(f"💥 {nome} ataca {hits}× — {total} dano total!")
            return hp, mana, msgs  # multi-hit substitui o ataque base
        elif atype == "phase_shift":
            limiar = ability.get("hp_threshold", 0.50)
            if enemy["hp"] / hp_max_inimigo <= limiar and not estado.phase_shifted:
                estado.phase_shifted = True
                estado.enemy_enraged = True
                msgs.append(f"⚠️ *{nome} muda de fase!* Enraivecido — +30% dano!")
        elif atype == "void_drain":
            drain = ability.get("value", 25)
            mana = max(0, mana - drain)
            hp = max(0, hp - 10)
            msgs.append(f"🌑 {nome} drena vazio: -{drain} mana, -10 HP!")

    final_dmg = dano_recebido(dmg_base, estado)

    ls = next((a for a in enemy.get("abilities", []) if a.get("type") == "lifesteal"), None)
    if ls and rng.random() < ls.get("chance", 0.5):
        heal = int(final_dmg * ls.get("value", 0.15))
        enemy["hp"] = min(hp_max_inimigo, enemy["hp"] + heal)
        msgs.append(f"🩸 {nome} rouba {heal} HP!")

    final_dmg = _absorver_escudo(estado, final_dmg, msgs)
    if final_dmg > 0:
        hp = max(0, hp - final_dmg)
        msgs.append(f"⚔️ {nome} causa {final_dmg} de dano!")
    return hp, mana, msgs
