"""Geração de loot ao derrotar um inimigo.

Quatro rolagens independentes (material do terreno, consumível, equipamento da classe,
acessório), cada uma com chance que cresce com a sorte; o resultado é cortado no
máximo de itens do tipo de inimigo. Raridade do equipamento sai de uma tabela de pesos
por tipo de inimigo.
"""

from __future__ import annotations

import random

# fmt: off
RARITY_WEIGHTS = {
    "normal":   {"common": 60, "uncommon": 28, "rare": 10, "epic": 2,  "legendary": 0},
    "miniboss": {"common": 30, "uncommon": 40, "rare": 22, "epic": 7,  "legendary": 1},
    "boss":     {"common": 10, "uncommon": 25, "rare": 35, "epic": 22, "legendary": 8},
}

# (nome, tipo, raridade, elemento)
TERRAIN_MATS = {
    "lava":     [("Escama Flamejante", "material", "common", "fire"),      ("Cristal de Fogo", "material", "uncommon", "fire"),       ("Núcleo de Magma", "material", "rare", "fire"),         ("Essência do Inferno", "material", "epic", "fire")],
    "glacial":  [("Shard Glacial", "material", "common", "ice"),           ("Núcleo de Gelo", "material", "uncommon", "ice"),         ("Cristal do Permafrost", "material", "rare", "ice"),    ("Essência do Silêncio", "material", "epic", "ice")],
    "chemical": [("Fungo Corrosivo", "material", "common", "poison"),      ("Veneno Concentrado", "material", "uncommon", "poison"),  ("Ácido Puro", "material", "rare", "poison"),            ("Essência da Névoa", "material", "epic", "poison")],
    "giants":   [("Ossada de Gigante", "material", "common", "physical"),  ("Couro de Titã", "material", "uncommon", "physical"),     ("Coração de Gigante", "material", "rare", "physical"),  ("Legado do Colosso", "material", "epic", "physical")],
}

CLASS_WEAPONS = {
    "guerreiro":  [("Espada de Ferro", "weapon", "common", "physical"),    ("Espada de Aço", "weapon", "uncommon", "physical"),    ("Espada Encantada", "weapon", "rare", "physical"),  ("Lâmina do Caos", "weapon", "epic", "physical"),      ("Espada do Bastião", "weapon", "legendary", "physical")],
    "paladino":   [("Maça Sagrada", "weapon", "common", "holy"),           ("Martelo Divino", "weapon", "uncommon", "holy"),       ("Flail Bendita", "weapon", "rare", "holy"),         ("Ceifador da Luz", "weapon", "epic", "holy"),         ("Arauto do Criador", "weapon", "legendary", "holy")],
    "arqueiro":   [("Arco Curto", "weapon", "common", "physical"),         ("Arco Longo", "weapon", "uncommon", "physical"),       ("Arco Élfrico", "weapon", "rare", "physical"),      ("Arco da Tempestade", "weapon", "epic", "physical"),  ("Arco do Crepúsculo", "weapon", "legendary", "physical")],
    "bruxo":      [("Cajado de Aprendiz", "weapon", "common", None),       ("Cajado Rúnico", "weapon", "uncommon", None),          ("Cajado do Abismo", "weapon", "rare", None),        ("Cajado do Vazio", "weapon", "epic", None),           ("Cajado Eterno", "weapon", "legendary", None)],
    "curandeiro": [("Bastão de Ervas", "weapon", "common", "holy"),        ("Bastão Sagrado", "weapon", "uncommon", "holy"),       ("Bastão da Luz", "weapon", "rare", "holy"),         ("Sceptro Divino", "weapon", "epic", "holy"),          ("Cetro da Aurora", "weapon", "legendary", "holy")],
}

CLASS_ARMOR = {
    "guerreiro":  [("Armadura de Ferro", "armor", "common", None),  ("Cota de Malha", "armor", "uncommon", None),      ("Armadura de Placas", "armor", "rare", None), ("Armadura Rúnica", "armor", "epic", None)],
    "paladino":   [("Escudo Sacro", "armor", "common", "holy"),     ("Armadura Sagrada", "armor", "uncommon", "holy"), ("Armadura da Luz", "armor", "rare", "holy"),  ("Proteção Divina", "armor", "epic", "holy")],
    "arqueiro":   [("Couro de Caçador", "armor", "common", None),   ("Couro Reforçado", "armor", "uncommon", None),    ("Couro Élfrico", "armor", "rare", None),      ("Couro das Sombras", "armor", "epic", None)],
    "bruxo":      [("Vestes de Aprendiz", "armor", "common", None), ("Vestes Encantadas", "armor", "uncommon", None),  ("Vestes Rúnicas", "armor", "rare", None),     ("Vestes do Abismo", "armor", "epic", None)],
    "curandeiro": [("Vestes da Luz", "armor", "common", "holy"),    ("Manto Sagrado", "armor", "uncommon", "holy"),    ("Vestes Divinas", "armor", "rare", "holy"),   ("Manto da Aurora", "armor", "epic", "holy")],
}

CONSUMABLES = [
    ("Poção de Vida Pequena", "consumable", "common", None),
    ("Poção de Vida Média",   "consumable", "uncommon", None),
    ("Poção de Mana Pequena", "consumable", "common", None),
    ("Antídoto",              "consumable", "common", None),
    ("Bálsamo Sagrado",       "consumable", "uncommon", None),
]

ACCESSORIES = [
    ("Amuleto de Força",       "accessory", "uncommon", "physical"),
    ("Anel de Proteção",       "accessory", "uncommon", None),
    ("Colar de Sorte",         "accessory", "rare",     None),
    ("Pingente de Vitalidade", "accessory", "uncommon", None),
    ("Bracelete de Mana",      "accessory", "uncommon", None),
    ("Anel Elemental",         "accessory", "rare",     None),
    ("Amuleto do Extrator",    "accessory", "epic",     None),
]

DROP_BASE   = {"normal": 0.45, "miniboss": 0.85, "boss": 1.00, "boss_special": 1.00}
MAX_ITEMS   = {"normal": 1,    "miniboss": 2,    "boss": 3,    "boss_special": 4}
EQUIP_BASE  = {"normal": 0.10, "miniboss": 0.40, "boss": 0.70, "boss_special": 0.90}
ACC_BASE    = {"normal": 0.05, "miniboss": 0.20, "boss": 0.40, "boss_special": 0.60}
# fmt: on

EQUIPAVEIS = ("weapon", "armor", "accessory")


def _item(entrada: tuple, equip_slot: str | None) -> dict:
    nome, tipo, raridade, elemento = entrada
    return {
        "name": nome,
        "type": tipo,
        "rarity": raridade,
        "element": elemento,
        "equip_slot": equip_slot,
    }


def pick_rarity(enemy_type: str, rng: random.Random | None = None) -> str:
    rng = rng or random
    pesos = RARITY_WEIGHTS.get(enemy_type, RARITY_WEIGHTS["normal"])
    return rng.choices(list(pesos), weights=list(pesos.values()), k=1)[0]


def bonus_sorte(luck: int) -> float:
    """+1% por 5 pontos de sorte acima de 20."""
    return max(0, (luck - 20) // 5) * 0.01


def generate_loot(
    enemy: dict, char_class: str, luck: int, rng: random.Random | None = None
) -> list[dict]:
    rng = rng or random
    terrain = enemy["terrain"] if enemy["terrain"] != "all" else "lava"
    etype = enemy["type"]
    rtype = "boss" if etype in ("boss", "boss_special") else etype
    luck_bonus = bonus_sorte(luck)
    drop_chance = min(0.95, DROP_BASE.get(etype, 0.45) + luck_bonus)
    loot: list[dict] = []

    if rng.random() < drop_chance:
        loot.append(_item(rng.choice(TERRAIN_MATS[terrain]), None))

    if rng.random() < drop_chance * 0.55:
        loot.append(_item(rng.choice(CONSUMABLES), None))

    if rng.random() < EQUIP_BASE.get(etype, 0.10) + luck_bonus:
        rarity = pick_rarity(rtype, rng)
        slot = rng.choice(["weapon", "armor"])
        pool = (CLASS_WEAPONS if slot == "weapon" else CLASS_ARMOR).get(char_class, [])
        opts = [i for i in pool if i[2] == rarity] or pool
        if opts:
            loot.append(_item(rng.choice(opts), slot))

    if rng.random() < ACC_BASE.get(etype, 0.05) + luck_bonus:
        loot.append(_item(rng.choice(ACCESSORIES), "accessory"))

    return loot[: MAX_ITEMS.get(etype, 1)]
