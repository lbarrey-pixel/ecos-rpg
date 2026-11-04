"""Criaturas do Wasteland Glacial."""

# fmt: off
NORMAIS = {

    "lobo_permafrost": {
        "name": "Lobo do Permafrost", "terrain": "glacial", "type": "normal", "element": "ice",
        "abilities": [{"type": "freeze", "chance": 0.25}, {"type": "multi_hit", "chance": 0.30}],
        "loot": ["presa_gelo", "pelo_glacial"],
        "tiers": {
            1: {"hp": 50,  "damage": 14, "defense": 3,  "xp": 19, "gold": (12, 30),  "flavor": "Caça em silêncio. O frio que te atinge antecede o bote."},
            2: {"hp": 110, "damage": 30, "defense": 7,  "xp": 42, "gold": (35, 72),  "flavor": "Um alfa. Não está sozinho — mas ataca primeiro."},
            3: {"hp": 240, "damage": 58, "defense": 14, "xp": 92, "gold": (80, 155), "flavor": "Um lobo espectral. Seus dentes atravessam armaduras como névoa."},
        },
    },
    "elemental_gelo_menor": {
        "name": "Elemental de Gelo", "terrain": "glacial", "type": "normal", "element": "ice",
        "abilities": [{"type": "freeze", "chance": 0.40}, {"type": "mana_drain", "chance": 0.35, "value": 10}],
        "loot": ["nucleo_gelo", "shard_glacial"],
        "tiers": {
            1: {"hp": 48,  "damage": 13, "defense": 5,  "xp": 20, "gold": (14, 32),  "flavor": "Inteligência rudimentar. Congela tudo que toca."},
            2: {"hp": 105, "damage": 28, "defense": 11, "xp": 44, "gold": (38, 76),  "flavor": "Ganhou consciência. Agora escolhe seus alvos."},
            3: {"hp": 230, "damage": 54, "defense": 20, "xp": 96, "gold": (86, 158), "flavor": "Um elemental pleno. Seu núcleo pulsa com frio absoluto."},
        },
    },
    "banshee_congelada": {
        "name": "Banshee Congelada", "terrain": "glacial", "type": "normal", "element": "ice",
        "abilities": [{"type": "mana_drain", "chance": 0.60, "value": 15}, {"type": "freeze", "chance": 0.20}],
        "loot": ["eco_espectral", "cristal_lamento"],
        "tiers": {
            1: {"hp": 38,  "damage": 17, "defense": 2,  "xp": 22, "gold": (16, 36),  "flavor": "Um grito congelado no tempo. Drena a vontade de lutar."},
            2: {"hp": 84,  "damage": 36, "defense": 5,  "xp": 48, "gold": (42, 82),  "flavor": "Seu choro ressoa pela tundra. A mana some ao ouvi-la."},
            3: {"hp": 185, "damage": 70, "defense": 10, "xp": 104,"gold": (95, 170), "flavor": "Uma rainha banshee. Aqueles que a ouvem raramente retornam."},
        },
    },
    "urso_glacial": {
        "name": "Urso Glacial", "terrain": "glacial", "type": "normal", "element": "ice",
        "abilities": [{"type": "stun", "chance": 0.25}, {"type": "armor_break", "chance": 0.20, "value": 2}],
        "loot": ["garra_gelo", "couro_glacial"],
        "tiers": {
            1: {"hp": 85,  "damage": 15, "defense": 7,  "xp": 23, "gold": (18, 38),  "flavor": "Enorme. Lento. Um golpe suficiente para quebrar ossos."},
            2: {"hp": 185, "damage": 32, "defense": 15, "xp": 50, "gold": (48, 92),  "flavor": "Coberto por cristais de gelo naturais. Armadura viva."},
            3: {"hp": 400, "damage": 62, "defense": 28, "xp": 108,"gold": (108,185), "flavor": "Um ancestral. A tundra inteira o reverencia como um deus."},
        },
    },
    "sombra_blizzard": {
        "name": "Sombra do Blizzard", "terrain": "glacial", "type": "normal", "element": "ice",
        "abilities": [{"type": "freeze", "chance": 0.45}, {"type": "burn", "chance": 0.0}],
        "loot": ["sombra_glacial", "vento_cristalizado"],
        "tiers": {
            1: {"hp": 42,  "damage": 16, "defense": 3,  "xp": 21, "gold": (14, 33),  "flavor": "Uma sombra dentro do blizzard. Difícil de mirar, fácil de sentir."},
            2: {"hp": 93,  "damage": 34, "defense": 7,  "xp": 46, "gold": (40, 79),  "flavor": "A sombra ganhou massa. Seu toque paralisa."},
            3: {"hp": 204, "damage": 66, "defense": 14, "xp": 100,"gold": (90, 162), "flavor": "Um blizzard com intenção. Ela não persegue — ela espera."},
        },
    },
}

MINIBOSSES = {

    "urso_permafrost": {
        "name": "Urso do Permafrost", "terrain": "glacial", "type": "miniboss", "element": "ice",
        "abilities": [
            {"type": "freeze",   "chance": 0.45},
            {"type": "stun",     "chance": 0.40},
            {"type": "armor_break","chance": 0.35, "value": 4},
        ],
        "loot": ["garra_permafrost", "couro_glacial_raro", "cristal_gelo_puro"],
        "tiers": {
            1: {"hp": 300, "damage": 30, "defense": 14, "xp": 108, "gold": (88, 162),
                "flavor": "🐻 *Urso do Permafrost — Faminto* te fareja.\n_\"Não te viu em meses. Está com muita fome.\"_"},
            2: {"hp": 648, "damage": 62, "defense": 29, "xp": 236, "gold": (195,355),
                "flavor": "🐻 *Urso do Permafrost — Enfurecido* ruge.\n_\"Cristais de gelo crescem do pelo. Cada pancada congela.\"_"},
            3: {"hp": 1400,"damage": 118,"defense": 55, "xp": 512, "gold": (410,710),
                "flavor": "🐻 *Urso do Permafrost — Amaldiçoado* aparece na neblina.\n_\"Uma maldição o mantém vivo além do natural. E ele sabe disso.\"_"},
        },
    },
    "elemental_gelo_boss": {
        "name": "Elemental de Gelo", "terrain": "glacial", "type": "miniboss", "element": "ice",
        "abilities": [
            {"type": "freeze",   "chance": 0.65},
            {"type": "mana_drain","chance": 0.55, "value": 22},
            {"type": "shield",   "value": 0.20},
        ],
        "loot": ["nucleo_gelo_puro", "shard_absoluto", "essencia_blizzard"],
        "tiers": {
            1: {"hp": 240, "damage": 26, "defense": 16, "xp": 112, "gold": (90, 168),
                "flavor": "❄️ *Elemental de Gelo — Instável* materializa.\n_\"Forma ainda incerta. Mas frio suficiente para matar.\"_"},
            2: {"hp": 518, "damage": 54, "defense": 32, "xp": 244, "gold": (200,360),
                "flavor": "❄️ *Elemental de Gelo — Cristalizado* assume forma definitiva.\n_\"Perfeito. Simétrico. Absolutamente letal.\"_"},
            3: {"hp": 1120,"damage": 104,"defense": 60, "xp": 528, "gold": (420,720),
                "flavor": "❄️ *Elemental Absoluto* — temperatura zero personalificada.\n_\"Não é frio. É a ausência de calor. É o fim.\"_"},
        },
    },
    "cavaleiro_congelado": {
        "name": "Cavaleiro Congelado", "terrain": "glacial", "type": "miniboss", "element": "ice",
        "abilities": [
            {"type": "freeze",    "chance": 0.40},
            {"type": "armor_break","chance": 0.45, "value": 4},
            {"type": "lifesteal", "chance": 0.30, "value": 0.15},
        ],
        "loot": ["armadura_gelo", "espada_congelada", "alma_cavaleiro"],
        "tiers": {
            1: {"hp": 270, "damage": 34, "defense": 20, "xp": 115, "gold": (92, 170),
                "flavor": "⚔️ *Cavaleiro Congelado — Esquecido* bloqueia o caminho.\n_\"Era humano. Agora é um aviso.\"_"},
            2: {"hp": 583, "damage": 70, "defense": 40, "xp": 250, "gold": (210,375),
                "flavor": "⚔️ *Cavaleiro Congelado — Eterno* avança sem hesitar.\n_\"Dois séculos de batalha tornaram cada movimento perfeito.\"_"},
            3: {"hp": 1260,"damage": 134,"defense": 76, "xp": 540, "gold": (430,740),
                "flavor": "⚔️ *Cavaleiro Soberano do Gelo* — a lenda era real.\n_\"Jurou proteger o que não existe mais. Ainda assim, protege.\"_"},
        },
    },
}
# fmt: on
