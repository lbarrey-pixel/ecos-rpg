"""Criaturas das Terras de Lava."""

# fmt: off
NORMAIS = {

    "salamandra": {
        "name": "Salamandra", "terrain": "lava", "type": "normal", "element": "fire",
        "abilities": [{"type": "burn", "chance": 0.40, "value": 0.05}],
        "loot": ["escama_flamejante", "cristal_fogo"],
        "tiers": {
            1: {"hp": 55,  "damage": 12, "defense": 4,  "xp": 18, "gold": (15, 35),  "flavor": "Uma lagartixa do tamanho de um cachorro, com escamas em brasa."},
            2: {"hp": 120, "damage": 26, "defense": 9,  "xp": 40, "gold": (40, 80),  "flavor": "A salamandra cresceu. O cheiro de carne queimada te precede."},
            3: {"hp": 260, "damage": 52, "defense": 18, "xp": 90, "gold": (90, 160), "flavor": "Uma salamandra ancestral. Seus passos derretem a pedra."},
        },
    },
    "escorpiao_brasa": {
        "name": "Escorpião de Brasa", "terrain": "lava", "type": "normal", "element": "fire",
        "abilities": [{"type": "poison", "chance": 0.35, "value": 0.04}, {"type": "burn", "chance": 0.25, "value": 0.03}],
        "loot": ["ferrão_toxico", "quitina_brasa"],
        "tiers": {
            1: {"hp": 45,  "damage": 14, "defense": 6,  "xp": 20, "gold": (12, 30),  "flavor": "Um escorpião com cauda em chamas. O veneno queima por dentro."},
            2: {"hp": 100, "damage": 30, "defense": 13, "xp": 44, "gold": (35, 75),  "flavor": "Maior, mais agressivo. O veneno agora corroe armaduras."},
            3: {"hp": 220, "damage": 58, "defense": 24, "xp": 95, "gold": (80, 150), "flavor": "Uma abominação. Metade escorpião, metade lava viva."},
        },
    },
    "golem_fragmentado": {
        "name": "Golem Fragmentado", "terrain": "lava", "type": "normal", "element": "fire",
        "abilities": [{"type": "shield", "value": 0.15}],
        "loot": ["nucleo_magma", "pedra_fundida"],
        "tiers": {
            1: {"hp": 80,  "damage": 10, "defense": 10, "xp": 22, "gold": (20, 40),  "flavor": "Um golem quebrado, mas ainda funcional. Resistente a golpes físicos."},
            2: {"hp": 175, "damage": 22, "defense": 20, "xp": 48, "gold": (50, 95),  "flavor": "Reconstruído por alguma força obscura. Mais duro que aço."},
            3: {"hp": 380, "damage": 44, "defense": 38, "xp": 105,"gold": (110,190), "flavor": "Um golem perfeito. Cada peça fundida no calor do núcleo da Terra."},
        },
    },
    "espectro_flamejante": {
        "name": "Espectro Flamejante", "terrain": "lava", "type": "normal", "element": "fire",
        "abilities": [{"type": "mana_drain", "chance": 0.50, "value": 12}, {"type": "burn", "chance": 0.55, "value": 0.04}],
        "loot": ["essencia_fogo", "cinza_espectral"],
        "tiers": {
            1: {"hp": 40,  "damage": 16, "defense": 3,  "xp": 24, "gold": (18, 38),  "flavor": "Uma chama que não deveria ter consciência. Drena sua energia."},
            2: {"hp": 88,  "damage": 34, "defense": 7,  "xp": 52, "gold": (45, 85),  "flavor": "O espectro ganhou forma. Seu toque apaga a magia."},
            3: {"hp": 195, "damage": 66, "defense": 14, "xp": 112,"gold": (100,175), "flavor": "Uma alma consumida pelo fogo eterno. Imune a magias de fogo."},
        },
    },
    "caranguejo_lava": {
        "name": "Caranguejo de Lava", "terrain": "lava", "type": "normal", "element": "fire",
        "abilities": [{"type": "armor_break", "chance": 0.30, "value": 2}, {"type": "multi_hit", "chance": 0.25}],
        "loot": ["pinça_fundida", "casca_lava"],
        "tiers": {
            1: {"hp": 65,  "damage": 13, "defense": 8,  "xp": 21, "gold": (14, 32),  "flavor": "Pinças que quebram pedra com facilidade. Tenta fazer o mesmo com você."},
            2: {"hp": 142, "damage": 28, "defense": 17, "xp": 46, "gold": (38, 78),  "flavor": "Um caranguejo veterano. Suas pinças já destruíram armaduras completas."},
            3: {"hp": 310, "damage": 55, "defense": 32, "xp": 100,"gold": (85, 165), "flavor": "O rei dos caranguejos. Seu exoesqueleto resiste a espadas como se fossem galhos."},
        },
    },
}

MINIBOSSES = {

    "salamandra_colossal": {
        "name": "Salamandra Colossal", "terrain": "lava", "type": "miniboss", "element": "fire",
        "abilities": [
            {"type": "burn",     "chance": 0.70, "value": 0.06},
            {"type": "multi_hit","chance": 0.40},
            {"type": "armor_break","chance": 0.30, "value": 3},
        ],
        "loot": ["escama_colossal", "nucleo_infernal", "cristal_fogo_raro"],
        "tiers": {
            1: {"hp": 250, "damage": 28, "defense": 12, "xp": 100, "gold": (80, 150),
                "flavor": "🔥 *Salamandra Colossal* desperta das profundezas.\n_\"O chão racha sob seu peso. Suas escamas brilham como metal derretido.\"_"},
            2: {"hp": 540, "damage": 58, "defense": 24, "xp": 220, "gold": (180,320),
                "flavor": "🔥 *Salamandra Colossal — Incandescente* emerge da lava.\n_\"Não há mais escamas. Só fogo com forma.\"_"},
            3: {"hp": 1150,"damage": 112,"defense": 46, "xp": 480, "gold": (380,640),
                "flavor": "🔥 *Salamandra Primordial* — a primeira. A última.\n_\"Existia antes do fim. Existirá depois de você.\"_"},
        },
    },
    "golem_magma": {
        "name": "Golem de Magma", "terrain": "lava", "type": "miniboss", "element": "fire",
        "abilities": [
            {"type": "shield",   "value": 0.25},
            {"type": "burn",     "chance": 0.80, "value": 0.05},
            {"type": "stun",     "chance": 0.35},
        ],
        "loot": ["nucleo_magma_puro", "fragmento_golem", "essencia_vulcao"],
        "tiers": {
            1: {"hp": 320, "damage": 22, "defense": 22, "xp": 110, "gold": (90, 165),
                "flavor": "⛰️ *Golem de Magma — Fragmentado* toma forma.\n_\"Pedaços de rocha fundida se unem com vontade própria.\"_"},
            2: {"hp": 690, "damage": 46, "defense": 44, "xp": 240, "gold": (195,350),
                "flavor": "⛰️ *Golem de Magma — Fundido* avança.\n_\"Completamente sólido. Nenhuma fratura visível. Nenhuma fraqueza.\"_"},
            3: {"hp": 1480,"damage": 88, "defense": 84, "xp": 520, "gold": (415,720),
                "flavor": "⛰️ *Golem Eterno* — construído pelo próprio vulcão.\n_\"Não foi criado. Nasceu da raiva da Terra.\"_"},
        },
    },
    "wyvern_brasas": {
        "name": "Wyvern das Brasas", "terrain": "lava", "type": "miniboss", "element": "fire",
        "abilities": [
            {"type": "burn",     "chance": 0.90, "value": 0.07},
            {"type": "multi_hit","chance": 0.50},
            {"type": "mana_drain","chance": 0.40, "value": 20},
        ],
        "loot": ["asa_wyvern", "dente_infernal", "cristal_fogo_raro"],
        "tiers": {
            1: {"hp": 220, "damage": 32, "defense": 10, "xp": 105, "gold": (85, 160),
                "flavor": "🐉 *Wyvern das Brasas — Filhote* pousa na sua frente.\n_\"Pequena para os padrões dela. Mortífera para os seus.\"_"},
            2: {"hp": 475, "damage": 66, "defense": 21, "xp": 230, "gold": (190,340),
                "flavor": "🐉 *Wyvern das Brasas — Adulta* abre as asas.\n_\"A sombra dela cobre você completamente.\"_"},
            3: {"hp": 1020,"damage": 128,"defense": 40, "xp": 500, "gold": (400,680),
                "flavor": "🐉 *Wyvern Anciã* — sobrevivente do apocalipse.\n_\"Viu cidades ruírem. Quer ver você também.\"_"},
        },
    },
}
# fmt: on
