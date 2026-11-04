"""Criaturas da Nuvem Química."""

# fmt: off
NORMAIS = {

    "fungo_ambulante": {
        "name": "Fungo Ambulante", "terrain": "chemical", "type": "normal", "element": "poison",
        "abilities": [{"type": "poison", "chance": 0.60, "value": 0.04}, {"type": "regen", "value": 0.04}],
        "loot": ["esporo_toxico", "micelio_corrosivo"],
        "tiers": {
            1: {"hp": 60,  "damage": 9,  "defense": 4,  "xp": 17, "gold": (10, 28),  "flavor": "Lento, mas o esporo que libera envenena o ar ao redor."},
            2: {"hp": 132, "damage": 20, "defense": 9,  "xp": 38, "gold": (30, 65),  "flavor": "Desenvolveu mobilidade e agressividade. O veneno agora paralisa."},
            3: {"hp": 288, "damage": 40, "defense": 18, "xp": 85, "gold": (70, 135), "flavor": "Uma colônia em forma humana. Mata o hospedeiro, vira o fungo."},
        },
    },
    "enxame_corrosivo": {
        "name": "Enxame Corrosivo", "terrain": "chemical", "type": "normal", "element": "poison",
        "abilities": [{"type": "armor_break", "chance": 0.50, "value": 3}, {"type": "poison", "chance": 0.45, "value": 0.03}],
        "loot": ["acido_concentrado", "asa_corrosiva"],
        "tiers": {
            1: {"hp": 35,  "damage": 18, "defense": 1,  "xp": 20, "gold": (12, 30),  "flavor": "Milhares de insetos ácidos. Individualmente fracos. Juntos, letais."},
            2: {"hp": 77,  "damage": 38, "defense": 3,  "xp": 44, "gold": (34, 70),  "flavor": "O ácido evoluiu. Corrói metal em segundos."},
            3: {"hp": 168, "damage": 74, "defense": 6,  "xp": 95, "gold": (78, 145), "flavor": "O enxame se tornou consciente. Coordenado. Implacável."},
        },
    },
    "serpente_toxica": {
        "name": "Serpente Tóxica", "terrain": "chemical", "type": "normal", "element": "poison",
        "abilities": [{"type": "poison", "chance": 0.70, "value": 0.05}, {"type": "multi_hit", "chance": 0.25}],
        "loot": ["veneno_puro", "escama_toxica"],
        "tiers": {
            1: {"hp": 44,  "damage": 15, "defense": 3,  "xp": 21, "gold": (15, 33),  "flavor": "Rápida. Um único mordida e o veneno começa o trabalho."},
            2: {"hp": 97,  "damage": 32, "defense": 7,  "xp": 46, "gold": (40, 80),  "flavor": "Três cabeças. Cada uma com veneno diferente."},
            3: {"hp": 212, "damage": 62, "defense": 13, "xp": 100,"gold": (90, 160), "flavor": "Uma hidra em miniatura. O veneno não tem antídoto conhecido."},
        },
    },
    "espectro_venenoso": {
        "name": "Espectro Venenoso", "terrain": "chemical", "type": "normal", "element": "poison",
        "abilities": [{"type": "poison", "chance": 0.55, "value": 0.04}, {"type": "mana_drain", "chance": 0.40, "value": 12}],
        "loot": ["essencia_veneno", "plasma_toxico"],
        "tiers": {
            1: {"hp": 38,  "damage": 16, "defense": 2,  "xp": 22, "gold": (14, 34),  "flavor": "Uma nuvem que pensa. Sua presença envenena o ar."},
            2: {"hp": 84,  "damage": 34, "defense": 5,  "xp": 48, "gold": (38, 78),  "flavor": "Ganhou densidade. Agora pode segurar você enquanto envenena."},
            3: {"hp": 183, "damage": 66, "defense": 10, "xp": 104,"gold": (86, 158), "flavor": "Inteligente. Paciente. Espera você respirar fundo."},
        },
    },
    "carnical_mutante": {
        "name": "Carniçal Mutante", "terrain": "chemical", "type": "normal", "element": "poison",
        "abilities": [{"type": "lifesteal", "chance": 0.35, "value": 0.20}, {"type": "armor_break", "chance": 0.25, "value": 2}],
        "loot": ["carne_corrompida", "garra_mutante"],
        "tiers": {
            1: {"hp": 70,  "damage": 12, "defense": 5,  "xp": 19, "gold": (12, 30),  "flavor": "Um sobrevivente que não devia ter sobrevivido. Come qualquer coisa."},
            2: {"hp": 153, "damage": 26, "defense": 11, "xp": 42, "gold": (33, 68),  "flavor": "A mutação avançou. Se cura enquanto te devora."},
            3: {"hp": 334, "damage": 50, "defense": 20, "xp": 92, "gold": (75, 142), "flavor": "Irreconhecível como humano. Só resta o instinto de consumir."},
        },
    },
}

MINIBOSSES = {

    "quimera_toxica": {
        "name": "Quimera Tóxica", "terrain": "chemical", "type": "miniboss", "element": "poison",
        "abilities": [
            {"type": "poison",   "chance": 0.85, "value": 0.06},
            {"type": "multi_hit","chance": 0.45},
            {"type": "armor_break","chance": 0.35, "value": 4},
        ],
        "loot": ["veneno_quimera", "carne_mutante_rara", "glândula_toxico"],
        "tiers": {
            1: {"hp": 230, "damage": 29, "defense": 11, "xp": 106, "gold": (86, 158),
                "flavor": "☠️ *Quimera Tóxica — Mutante* surge da névoa.\n_\"Partes de três criaturas diferentes. Nenhuma delas amigável.\"_"},
            2: {"hp": 497, "damage": 60, "defense": 23, "xp": 232, "gold": (192,346),
                "flavor": "☠️ *Quimera Tóxica — Evoluída* exala vapor corrosivo.\n_\"A evolução acelerada resultou em algo que não deveria existir.\"_"},
            3: {"hp": 1074,"damage": 116,"defense": 44, "xp": 504, "gold": (404,696),
                "flavor": "☠️ *Quimera Perfeita* — a equação resolvida do veneno.\n_\"Cada parte otimizada para matar de uma forma diferente.\"_"},
        },
    },
    "hidra_corrosiva": {
        "name": "Hidra Corrosiva", "terrain": "chemical", "type": "miniboss", "element": "poison",
        "abilities": [
            {"type": "poison",   "chance": 0.75, "value": 0.05},
            {"type": "regen",    "value": 0.05},
            {"type": "multi_hit","chance": 0.60},
        ],
        "loot": ["cabeca_hidra", "veneno_hidra_puro", "escama_corrosiva"],
        "tiers": {
            1: {"hp": 280, "damage": 24, "defense": 9,  "xp": 110, "gold": (88, 165),
                "flavor": "🐍 *Hidra Corrosiva — Jovem* aparece, já com três cabeças.\n_\"Corte uma. Crescem duas. Você sabe disso, mas faz diferença?\"_"},
            2: {"hp": 604, "damage": 50, "defense": 19, "xp": 240, "gold": (196,355),
                "flavor": "🐍 *Hidra Corrosiva — Raivosa* com seis cabeças visíveis.\n_\"Cada cabeça tem veneno diferente. Todas querem você morto.\"_"},
            3: {"hp": 1304,"damage": 96, "defense": 36, "xp": 520, "gold": (412,712),
                "flavor": "🐍 *Hidra Imortal* — corpo ácido, regeneração constante.\n_\"Não se mata uma hidra. Negocia-se com ela. Você não tem o que ela quer.\"_"},
        },
    },
    "fungo_predador": {
        "name": "Fungo Predador", "terrain": "chemical", "type": "miniboss", "element": "poison",
        "abilities": [
            {"type": "poison",    "chance": 0.90, "value": 0.05},
            {"type": "mana_drain","chance": 0.50, "value": 18},
            {"type": "regen",     "value": 0.07},
        ],
        "loot": ["esporo_consciente", "micelio_rede", "capsula_toxico"],
        "tiers": {
            1: {"hp": 210, "damage": 20, "defense": 8,  "xp": 104, "gold": (82, 155),
                "flavor": "🍄 *Fungo Predador — Disperso* pulsa em ritmo lento.\n_\"Uma rede de esporos te cerca. O veneno já começou.\"_"},
            2: {"hp": 453, "damage": 42, "defense": 17, "xp": 228, "gold": (188,340),
                "flavor": "🍄 *Fungo Predador — Consciente* te observa com algo como olhos.\n_\"Aprendeu. Adaptou. Esperava por alguém como você.\"_"},
            3: {"hp": 978, "damage": 80, "defense": 32, "xp": 494, "gold": (396,682),
                "flavor": "🍄 *Fungo Hive Mind* — a floresta é ele.\n_\"Você não luta contra um fungo. Luta contra um ecossistema.\"_"},
        },
    },
}
# fmt: on
