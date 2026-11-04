"""Habilidades por classe e sua execução.

``SKILLS`` é só dado. ``executar`` aplica a habilidade sobre o ``EstadoCombate`` e
devolve (hp, mana, mensagens). Habilidades que precisam de uma segunda escolha do
jogador (elemento) marcam ``estado.await_*`` e devolvem a mana; a escolha chega
depois como parâmetro ``elemento``, sem tocar no catálogo global.
"""

from __future__ import annotations

import random

from ..config import TERRAIN_MODIFIERS
from . import combate
from .estado import EstadoCombate

# fmt: off
SKILLS = {
    # Guerreiro
    "ataque_pesado":  {"name": "Ataque Pesado",     "class": "guerreiro", "mana": 0,  "type": "physical", "power": 1.30, "target": "single"},
    "investida":      {"name": "Investida",          "class": "guerreiro", "mana": 20, "type": "physical", "power": 1.10, "target": "single",
                       "effect": {"type": "stun",     "chance": 0.30, "duration": 1}},
    "muralha_ferro":  {"name": "Muralha de Ferro",   "class": "guerreiro", "mana": 15, "type": "buff",     "target": "self",
                       "effect": {"type": "def_up",   "value": 0.40,  "duration": 2}},
    "bravura":        {"name": "Bravura",            "class": "guerreiro", "mana": 25, "type": "buff",     "target": "party",
                       "effect": {"type": "atk_up",   "value": 0.15,  "duration": 3}},
    "grito_guerra":   {"name": "Grito de Guerra",    "class": "guerreiro", "mana": 30, "type": "debuff",   "target": "single", "cd": 4,
                       "effect": {"type": "fear",      "chance": 1.00, "duration": 1}},
    # Paladino
    "golpe_sagrado":  {"name": "Golpe Sagrado",      "class": "paladino",  "mana": 15, "type": "hybrid",   "power_phys": 0.80, "power_mag": 0.60, "element": "holy", "target": "single"},
    "imposicao_maos": {"name": "Imposição de Mãos",  "class": "paladino",  "mana": 20, "type": "heal",     "power": 1.50, "target": "single"},
    "escudo_divino":  {"name": "Escudo Divino",      "class": "paladino",  "mana": 30, "type": "shield",   "power": 0.60, "target": "party"},
    "consagrar":      {"name": "Consagrar",          "class": "paladino",  "mana": 25, "type": "magic",    "element": "holy", "power": 1.20, "target": "single",
                       "effect": {"type": "armor_break","chance": 0.60, "value": 3}},
    "luz_sagrada":    {"name": "Luz Sagrada",        "class": "paladino",  "mana": 40, "type": "magic_heal","element": "holy", "power_dmg": 1.00, "power_heal": 0.80, "target": "all"},
    # Arqueiro
    "tiro_preciso":   {"name": "Tiro Preciso",       "class": "arqueiro",  "mana": 10, "type": "physical", "power": 1.50, "target": "single"},
    "embeber_flecha": {"name": "Embeber Flecha",     "class": "arqueiro",  "mana": 20, "type": "buff",     "target": "self",
                       "effect": {"type": "imbue",    "duration": 3}},
    "armadilha":      {"name": "Armadilha",          "class": "arqueiro",  "mana": 20, "type": "debuff",   "target": "single", "cd": 5,
                       "effect": {"type": "stun",     "chance": 1.00, "duration": 1}},
    "chuva_flechas":  {"name": "Chuva de Flechas",   "class": "arqueiro",  "mana": 30, "type": "physical", "power": 0.80, "target": "all"},
    "olho_aguia":     {"name": "Olho de Águia",      "class": "arqueiro",  "mana": 20, "type": "buff",     "target": "self", "cd": 4,
                       "effect": {"type": "next_crit","multiplier": 2.2}},
    # Bruxo
    "bola_fogo":      {"name": "Bola de Fogo",       "class": "bruxo",     "mana": 20, "type": "magic", "element": "fire",   "power": 1.40, "target": "single",
                       "effect": {"type": "burn",     "chance": 0.70, "value": 0.05, "duration": 2}},
    "lanca_gelo":     {"name": "Lança de Gelo",      "class": "bruxo",     "mana": 20, "type": "magic", "element": "ice",    "power": 1.30, "target": "single",
                       "effect": {"type": "freeze",   "chance": 0.35, "duration": 1}},
    "nuvem_toxica":   {"name": "Nuvem Tóxica",       "class": "bruxo",     "mana": 20, "type": "magic", "element": "poison", "power": 1.10, "target": "single",
                       "effect": {"type": "poison",   "chance": 0.90, "value": 0.05, "duration": 3}},
    "pulso_arcano":   {"name": "Pulso Arcano",       "class": "bruxo",     "mana": 25, "type": "magic", "element": "arcane", "power": 1.20, "target": "single",
                       "effect": {"type": "mana_drain","chance": 1.00, "value": 20}},
    "tempestade":     {"name": "Tempestade Elemental","class": "bruxo",    "mana": 45, "type": "magic", "element": "random", "power": 1.60, "target": "all"},
    # Curandeiro
    "cura":           {"name": "Cura",               "class": "curandeiro","mana": 20, "type": "heal",  "power": 1.60, "target": "single"},
    "escudo_sagrado": {"name": "Escudo Sagrado",     "class": "curandeiro","mana": 30, "type": "shield_heal","target": "self", "cd": 3},
    "cura_area":      {"name": "Cura em Área",       "class": "curandeiro","mana": 35, "type": "heal",  "power": 1.00, "target": "party"},
    "magia_elemental":{"name": "Magia Elemental",    "class": "curandeiro","mana": 25, "type": "magic", "element": "choice", "power": 0.91, "target": "single"},
    "revitalizar":    {"name": "Revitalizar",        "class": "curandeiro","mana": 25, "type": "mana_restore","value": 40,  "target": "single"},
}

CLASS_SKILLS = {
    "guerreiro":  ["ataque_pesado", "investida",      "muralha_ferro", "bravura",        "grito_guerra"],
    "paladino":   ["golpe_sagrado", "imposicao_maos", "escudo_divino", "consagrar",      "luz_sagrada"],
    "arqueiro":   ["tiro_preciso",  "embeber_flecha", "armadilha",     "chuva_flechas",  "olho_aguia"],
    "bruxo":      ["bola_fogo",     "lanca_gelo",     "nuvem_toxica",  "pulso_arcano",   "tempestade"],
    "curandeiro": ["cura",          "escudo_sagrado", "cura_area",     "magia_elemental","revitalizar"],
}
# fmt: on

ELEMENTOS_ESCOLHA = ("fire", "ice", "poison")
ELEMENTOS_TEMPESTADE = ("fire", "ice", "poison", "arcane")
ESCUDO_SAGRADO_PCT = 0.80
IMBUIR_DURACAO = 3


def validar(
    skill_key: str, estado: EstadoCombate, mana: int, classe: str | None = None
) -> str | None:
    """Mensagem de erro se a habilidade não pode ser usada agora; None se pode."""
    sk = SKILLS.get(skill_key)
    if not sk:
        return "❌ Skill desconhecida."
    if classe and sk["class"] != classe:
        return "❌ Essa skill pertence a outra classe."
    custo = sk.get("mana", 0)
    if mana < custo:
        return f"❌ Mana insuficiente ({mana}/{custo})."
    cd = estado.skill_cds.get(skill_key, 0)
    if cd > 0:
        return f"⏳ {sk['name']} em cooldown ({cd} turnos)."
    return None


def executar(
    skill_key: str,
    char: dict,
    estado: EstadoCombate,
    hp: int,
    mana: int,
    rng: random.Random | None = None,
    elemento: str | None = None,
) -> tuple[int, int, list[str]]:
    rng = rng or random
    erro = validar(skill_key, estado, mana, char.get("class"))
    if erro:
        return hp, mana, [erro]
    sk = SKILLS[skill_key]
    custo = sk.get("mana", 0)

    mana -= custo
    inimigo = estado.enemy or {}
    terreno = estado.terrain
    tipo = sk["type"]
    msgs: list[str] = []

    if tipo == "physical":
        dano = int(combate.dano_fisico(char, inimigo, estado) * sk.get("power", 1.0))
        dano = combate.ferir_inimigo(estado, dano)
        msgs.append(f"⚔️ {sk['name']}: {dano} de dano físico!")
        if (eff := sk.get("effect")) and inimigo:
            if combate.aplicar_efeito(estado.e_effects, eff, rng) and eff["type"] == "stun":
                msgs.append("⚡ Inimigo atordoado!")

    elif tipo == "magic":
        element = elemento or sk.get("element", "arcane")
        if element == "random":
            element = rng.choice(ELEMENTOS_TEMPESTADE)
            msgs.append(f"🌀 Elemento sorteado: {element}!")
        if element == "choice":
            estado.await_elem = skill_key
            return hp, mana + custo, ["🌀 Escolha o elemento:"]
        dano = int(combate.dano_magico(char, inimigo, element, terreno) * sk.get("power", 1.0))
        dano = combate.ferir_inimigo(estado, dano)
        mod = TERRAIN_MODIFIERS.get(terreno, {}).get(element, 1.0)
        mod_s = f" [{mod:.2f}×]" if mod != 1.0 else ""
        msgs.append(f"🔮 {sk['name']}: {dano} dano {element}{mod_s}!")
        if (eff := sk.get("effect")) and inimigo:
            combate.aplicar_efeito(estado.e_effects, eff, rng)

    elif tipo == "hybrid":
        fis = int(combate.dano_fisico(char, inimigo, estado) * sk.get("power_phys", 0.8))
        mag = int(
            combate.dano_magico(char, inimigo, sk.get("element", "holy"), terreno)
            * sk.get("power_mag", 0.6)
        )
        total = combate.ferir_inimigo(estado, fis + mag)
        msgs.append(f"⚡ {sk['name']}: {fis} físico + {mag} sagrado = {total} total!")

    elif tipo == "heal":
        curado = combate.cura(char, sk.get("power", 1.0))
        hp = min(char["hp_max"], hp + curado)
        msgs.append(f"💚 {sk['name']}: +{curado} HP!")

    elif tipo == "shield_heal":
        estado.shield = int(combate.espirito_efetivo(char) * ESCUDO_SAGRADO_PCT)
        msgs.append(f"🛡️ {sk['name']}: escudo de {estado.shield} HP! (explode ao quebrar)")

    elif tipo == "shield":
        estado.shield = combate.cura(char, sk.get("power", 0.60))
        msgs.append(f"🛡️ {sk['name']}: escudo de {estado.shield} HP!")

    elif tipo == "buff":
        eff = sk.get("effect", {})
        etipo = eff.get("type")
        if etipo == "def_up":
            estado.def_buff, estado.def_buff_dur = eff["value"], eff["duration"]
            msgs.append(
                f"🛡️ {sk['name']}: +{int(eff['value'] * 100)}% DEF por {eff['duration']} turnos!"
            )
        elif etipo == "atk_up":
            estado.atk_buff, estado.atk_buff_dur = eff["value"], eff["duration"]
            msgs.append(
                f"⚔️ {sk['name']}: +{int(eff['value'] * 100)}% ATK por {eff['duration']} turnos!"
            )
        elif etipo == "next_crit":
            estado.next_crit = True
            msgs.append(f"👁️ {sk['name']}: próximo ataque é crítico {combate.CRIT_MULT}×!")
        elif etipo == "imbue":
            estado.await_imbue = True
            return hp, mana + custo, ["🏹 Escolha o elemento para imbuir:"]

    elif tipo == "debuff":
        eff = sk.get("effect", {})
        if inimigo:
            combate.aplicar_efeito(estado.e_effects, eff, rng)
            rotulo = {"fear": "com medo", "stun": "atordoado"}.get(eff.get("type", ""), "debuffado")
            msgs.append(f"😱 {sk['name']}: inimigo {rotulo}!")

    elif tipo == "magic_heal":
        dano = int(
            combate.dano_magico(char, inimigo, sk.get("element", "holy"), terreno)
            * sk.get("power_dmg", 1.0)
        )
        dano = combate.ferir_inimigo(estado, dano)
        curado = combate.cura(char, sk.get("power_heal", 0.80))
        hp = min(char["hp_max"], hp + curado)
        msgs.append(f"✨ {sk['name']}: {dano} dano sagrado + cura {curado} HP!")

    elif tipo == "mana_restore":
        val = sk.get("value", 40)
        mana = min(char["mana_max"], mana + val)
        msgs.append(f"🔷 {sk['name']}: +{val} mana!")

    if "cd" in sk:
        estado.skill_cds[skill_key] = sk["cd"]
    return hp, mana, msgs


def imbuir(estado: EstadoCombate, elemento: str, mana: int) -> tuple[int, list[str]]:
    """Segunda etapa de Embeber Flecha: cobra a mana e arma o elemento por N ataques."""
    estado.imbue_element = elemento
    estado.imbue_dur = IMBUIR_DURACAO
    estado.await_imbue = False
    mana -= SKILLS["embeber_flecha"]["mana"]
    return mana, [f"🏹 Flechas imbuídas com *{elemento}* por {IMBUIR_DURACAO} ataques!"]


def escolher_elemento(
    estado: EstadoCombate,
    char: dict,
    elemento: str,
    hp: int,
    mana: int,
    rng: random.Random | None = None,
) -> tuple[int, int, list[str]]:
    """Segunda etapa de uma magia com ``element: choice``."""
    skill_key = estado.await_elem or "magia_elemental"
    estado.await_elem = None
    return executar(skill_key, char, estado, hp, mana, rng=rng, elemento=elemento)
