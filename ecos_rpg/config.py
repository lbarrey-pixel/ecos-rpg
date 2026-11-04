"""Constantes do jogo: classes, terrenos, bênçãos, raridade e durabilidade.

Tudo aqui é dado. Regras que precisam de código ficam no pacote ``engine``.
"""

# fmt: off
CLASSES = {
    "paladino": {
        "emoji": "⚔️",
        "name": "Holy Paladino",
        "lore": "Cruzados que juraram proteger o Bastião com sangue e fé. Carregam a luz sagrada como arma — e os feridos da PT como responsabilidade.",
        "playstyle": "Progride com segurança e sustain. Em solo, sua cura e resistência garantem runs longas e estáveis. Em PT, é o escudo, o cofre e o coração do grupo.",
        "stats": {
            "hp_max": 180, "mana_max": 80, "attack": 35, "defense": 30,
            "spirituality": 20, "luck": 18, "carry_capacity": 12, "safe_slots": 4,
        },
    },
    "arqueiro": {
        "emoji": "🏹",
        "name": "Arqueiro",
        "lore": "Caçadores das sombras. Cresceram nas bordas do Bastião, aprendendo que sobreviver depende de nunca ser visto — e nunca errar.",
        "playstyle": "Runs rápidas e lucrativas graças à sorte elevada. Solo é eficiente e independente — entra, coleta o que há de melhor e sai. Em PT, potencializa o loot de todos.",
        "stats": {
            "hp_max": 120, "mana_max": 70, "attack": 38, "defense": 15,
            "spirituality": 10, "luck": 45, "carry_capacity": 8, "safe_slots": 2,
        },
    },
    "guerreiro": {
        "emoji": "🛡️",
        "name": "Guerreiro",
        "lore": "Brutos corajosos que jogam o próprio corpo entre os monstros e os aliados. Sua bravura não é estupidez — é o que mantém a PT viva.",
        "playstyle": "Força bruta que funciona em qualquer cenário. Solo destrói inimigos físicos com bravura e resiste a tudo. Em PT, seus buffs de coragem mudam o rumo das batalhas.",
        "stats": {
            "hp_max": 220, "mana_max": 60, "attack": 32, "defense": 50,
            "spirituality": 8, "luck": 18, "carry_capacity": 14, "safe_slots": 4,
        },
    },
    "bruxo": {
        "emoji": "🧙",
        "name": "Bruxo",
        "lore": "Estudiosos do colapso. Dominam os quatro elementos que destruíram o mundo — fogo, gelo, veneno e morte — e os devolvem com precisão cirúrgica.",
        "playstyle": "Mata antes de tomar dano — esse é o segredo do solo. Posicionamento e timing são tudo. Em PT, é o maior dano elemental do grupo, devastador em qualquer terreno.",
        "stats": {
            "hp_max": 100, "mana_max": 160, "attack": 18, "defense": 10,
            "spirituality": 55, "luck": 22, "carry_capacity": 6, "safe_slots": 2,
        },
    },
    "curandeiro": {
        "emoji": "✨",
        "name": "Curandeiro",
        "lore": "Guardiões da vida que insistem em existir num mundo que desistiu dela. Dominam a cura, o escudo e fragmentos dos elementos — únicos a carregar vida e destruição ao mesmo tempo.",
        "playstyle": "Escudo Sagrado e magias elementais tornam o solo viável e único. Quanto mais pressão recebe, mais letal se torna. Em PT, multiplica a sobrevivência de todos. Alto teto de habilidade.",
        "stats": {
            "hp_max": 140, "mana_max": 150, "attack": 14, "defense": 22,
            "spirituality": 52, "luck": 22, "carry_capacity": 8, "safe_slots": 3,
        },
    },
}

# Bônus de PT (Vínculo do Bastião), por tamanho do grupo
PARTY_BONUS = {
    2: {"luck_pct": 10, "hp_pct": 5,  "mana_pct": 0,  "attack_pct": 0},
    3: {"luck_pct": 20, "hp_pct": 10, "mana_pct": 5,  "attack_pct": 0},
    4: {"luck_pct": 30, "hp_pct": 15, "mana_pct": 10, "attack_pct": 5},
}

HEALER_ELEMENTAL_DEBUFF = 0.35
SACRED_SHIELD = {
    "capacity_multiplier": 0.80,
    "explosion_pct": 1.00,
    "expire_explosion_pct": 0.20,
    "cooldown_rounds": 3,
    "mana_cost": 30,
}

# Chance de perder cada equipamento ao morrer. Bolso seguro nunca perde;
# item com is_bound=True (Amuleto de Vínculo) zera a chance.
EQUIPMENT_LOSS_CHANCE = {
    "common":    0.60,
    "uncommon":  0.40,
    "rare":      0.25,
    "epic":      0.10,
    "legendary": 0.03,
}

# Durabilidade 0 = item perde os bônus (não some, precisa reparar)
DURABILITY = {
    "common":    {"max": 30,  "loss_per_run": 3},
    "uncommon":  {"max": 50,  "loss_per_run": 3},
    "rare":      {"max": 80,  "loss_per_run": 2},
    "epic":      {"max": 120, "loss_per_run": 2},
    "legendary": {"max": 200, "loss_per_run": 1},
}

TERRAINS = {
    "lava": {
        "emoji": "🌋", "name": "Terras de Lava", "element": "fire",
        "description": "Planícies de rocha derretida onde o chão nunca esfria. Dano de fogo constante. Criaturas forjadas no calor do fim do mundo.",
    },
    "glacial": {
        "emoji": "❄️", "name": "Wasteland Glacial", "element": "ice",
        "description": "Um inverno que nunca terminou. Frio que paralisa equipamentos e lentifica movimentos. A morte aqui chega devagar — e silenciosa.",
    },
    "chemical": {
        "emoji": "☠️", "name": "Nuvem Química", "element": "poison",
        "description": "Névoa densa de origem desconhecida que corrói tudo. Inimigos mutados por anos de exposição são imprevisíveis e resistentes.",
    },
    "giants": {
        "emoji": "🗿", "name": "Vale dos Gigantes", "element": "physical",
        "description": "Criaturas colossais que sobreviveram ao apocalipse ficando maiores. Dano físico catastrófico. Os maiores drops do jogo. Para os mais insanos.",
    },
}

# Multiplicador de dano mágico por elemento em cada terreno.
# Fogo em terra de lava rende pouco; gelo em terra de lava rende muito.
TERRAIN_MODIFIERS = {
    "lava":     {"fire": 0.60, "ice": 1.40, "poison": 1.00, "physical": 1.00, "holy": 1.00, "arcane": 1.00, "void": 1.00},
    "glacial":  {"fire": 1.40, "ice": 0.60, "poison": 1.00, "physical": 1.00, "holy": 1.00, "arcane": 1.00, "void": 1.00},
    "chemical": {"fire": 1.00, "ice": 1.00, "poison": 1.00, "physical": 1.30, "holy": 0.70, "arcane": 1.00, "void": 1.00},
    "giants":   {"fire": 1.00, "ice": 1.00, "poison": 1.35, "physical": 0.70, "holy": 1.00, "arcane": 1.00, "void": 1.00},
}

BLESSINGS = {
    "retorno": {
        "emoji": "🌿", "name": "Bênção do Retorno", "tier": 1, "cost": 50,
        "description": "Ao ser derrotado em PvP, reduz o custo de fuga para 5% máximo.",
    },
    "martir": {
        "emoji": "🛡️", "name": "Bênção do Mártir", "tier": 2, "cost": 150,
        "description": "Ao ser derrotado em PvP, preserva 1 slot de loot além dos bolsos seguros.",
    },
    "sobrevivente": {
        "emoji": "✨", "name": "Bênção do Sobrevivente", "tier": 3, "cost": 350,
        "description": "Ao ser derrotado em PvP, permanece na dungeon com 1 HP — sem loot normal, mas ainda com chance de extrair.",
    },
}

# PvP: handicap (dano%, defesa%) entre tiers e janelas de encontro por rodada
PVP_HANDICAP = {
    (1, 2): (25, 15), (1, 3): (40, 25), (1, 4): (55, 30),
    (2, 3): (15, 10), (2, 4): (30, 20), (3, 4): (10, 8),
}

PVP_WINDOWS = {
    (1, 3): None,
    (4, 6): 2,
    (7, 999): 4,
}

RARITY_EMOJI = {
    "common":    "⬜",
    "uncommon":  "🟩",
    "rare":      "🟦",
    "epic":      "🟪",
    "legendary": "🟨",
}

RARITY_NAME = {
    "common":    "Comum",
    "uncommon":  "Incomum",
    "rare":      "Raro",
    "epic":      "Épico",
    "legendary": "Lendário",
}

EQUIP_SLOTS = {
    "weapon":     "⚔️ Arma",
    "armor":      "🛡️ Armadura",
    "accessory":  "💍 Acessório",
    "ammunition": "🏹 Munição",
}
# fmt: on


def get_flee_cost(round_number: int) -> int:
    """Percentual do ouro da run perdido ao fugir; cresce com as batalhas vencidas."""
    if round_number <= 4:
        return 5
    if round_number <= 8:
        return 5 + int((round_number - 4) * 1.75)
    return 20
