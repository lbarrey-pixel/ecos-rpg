"""Criaturas do Vale dos Gigantes."""

# fmt: off
NORMAIS = {

    "ogro_menor": {
        "name": "Ogro Menor", "terrain": "giants", "type": "normal", "element": "physical",
        "abilities": [{"type": "stun", "chance": 0.30}, {"type": "armor_break", "chance": 0.25, "value": 2}],
        "loot": ["osso_gigante", "couro_grosso"],
        "tiers": {
            1: {"hp": 90,  "damage": 16, "defense": 6,  "xp": 20, "gold": (18, 40),  "flavor": "Menor que um ogro adulto. Não menos perigoso."},
            2: {"hp": 197, "damage": 34, "defense": 13, "xp": 44, "gold": (50, 95),  "flavor": "Cresceu. E ficou mais raivoso no processo."},
            3: {"hp": 430, "damage": 66, "defense": 24, "xp": 96, "gold": (112,190), "flavor": "Um ogro sem a palavra 'menor'. Puro músculo e raiva."},
        },
    },
    "troll_ruinas": {
        "name": "Troll das Ruínas", "terrain": "giants", "type": "normal", "element": "physical",
        "abilities": [{"type": "regen", "value": 0.06}, {"type": "stun", "chance": 0.20}],
        "loot": ["pedra_troll", "osso_petrificado"],
        "tiers": {
            1: {"hp": 100, "damage": 13, "defense": 8,  "xp": 21, "gold": (16, 38),  "flavor": "Se regenera lentamente. Matar rápido é a única estratégia."},
            2: {"hp": 218, "damage": 28, "defense": 17, "xp": 46, "gold": (44, 88),  "flavor": "A regeneração acelerou. Membros perdidos voltam em segundos."},
            3: {"hp": 476, "damage": 54, "defense": 32, "xp": 100,"gold": (100,172), "flavor": "Imortal por regeneração. Só fogo ou magia pode parar permanentemente."},
        },
    },
    "brutus_pedra": {
        "name": "Brutus de Pedra", "terrain": "giants", "type": "normal", "element": "physical",
        "abilities": [{"type": "shield", "value": 0.20}, {"type": "stun", "chance": 0.35}],
        "loot": ["mineral_duro", "fragmento_colossus"],
        "tiers": {
            1: {"hp": 95,  "damage": 14, "defense": 12, "xp": 22, "gold": (17, 38),  "flavor": "Pele de pedra. Lento. Cada golpe treme o chão."},
            2: {"hp": 207, "damage": 30, "defense": 25, "xp": 48, "gold": (46, 90),  "flavor": "A pele virou rocha completa. Armas lascam antes de penetrar."},
            3: {"hp": 452, "damage": 58, "defense": 46, "xp": 104,"gold": (104,178), "flavor": "Uma estátua que decide andar. Praticamente indestrutível."},
        },
    },
    "ciclope_jovem": {
        "name": "Ciclope Jovem", "terrain": "giants", "type": "normal", "element": "physical",
        "abilities": [{"type": "armor_break", "chance": 0.40, "value": 3}, {"type": "multi_hit", "chance": 0.20}],
        "loot": ["olho_ciclope", "clava_ossea"],
        "tiers": {
            1: {"hp": 80,  "damage": 18, "defense": 7,  "xp": 23, "gold": (20, 42),  "flavor": "Jovem, mas já maior que dois humanos adultos. Um olho, cem problemas."},
            2: {"hp": 174, "damage": 38, "defense": 15, "xp": 50, "gold": (52, 98),  "flavor": "Adulto. Caçador experiente. Sua visão única não perde nada."},
            3: {"hp": 380, "damage": 74, "defense": 28, "xp": 108,"gold": (116,196), "flavor": "Um ancião ciclope. Já viu o fim do mundo. Quer que você sinta o mesmo."},
        },
    },
    "colosso_dorminhoco": {
        "name": "Colosso Dorminhoco", "terrain": "giants", "type": "normal", "element": "physical",
        "abilities": [{"type": "stun", "chance": 0.45}, {"type": "armor_break", "chance": 0.35, "value": 4}],
        "loot": ["colosso_fragmento", "terra_sagrada"],
        "tiers": {
            1: {"hp": 110, "damage": 20, "defense": 9,  "xp": 24, "gold": (20, 44),  "flavor": "Parecia uma pedra. Não era. Agora está acordado e irritado."},
            2: {"hp": 240, "damage": 42, "defense": 19, "xp": 52, "gold": (55, 105), "flavor": "Dormia há séculos. Você o acordou. Parabéns."},
            3: {"hp": 524, "damage": 80, "defense": 36, "xp": 112,"gold": (122,202), "flavor": "O colosso original. Criado para destruir. Dormiu quando não havia mais nada."},
        },
    },

}

MINIBOSSES = {

    "ciclope_ruinas": {
        "name": "Ciclope das Ruínas", "terrain": "giants", "type": "miniboss", "element": "physical",
        "abilities": [
            {"type": "stun",      "chance": 0.50},
            {"type": "armor_break","chance": 0.45, "value": 5},
            {"type": "multi_hit", "chance": 0.30},
        ],
        "loot": ["olho_ciclope_antigo", "clava_colossus", "osso_titã"],
        "tiers": {
            1: {"hp": 350, "damage": 35, "defense": 15, "xp": 115, "gold": (95, 175),
                "flavor": "👁️ *Ciclope das Ruínas — Cego* avança guiado pelo olfato.\n_\"Não te vê. Te sente. É pior.\"_"},
            2: {"hp": 756, "damage": 72, "defense": 31, "xp": 250, "gold": (210,380),
                "flavor": "👁️ *Ciclope das Ruínas — Vigilante* te mirou de longe.\n_\"Um olho. Uma visão perfeita. Nenhum ponto cego.\"_"},
            3: {"hp": 1632,"damage": 138,"defense": 59, "xp": 540, "gold": (440,755),
                "flavor": "👁️ *Ciclope Onividente* — vê além do mundo físico.\n_\"Viu seu passado. Viu seu futuro. Não está impressionado.\"_"},
        },
    },
    "ogro_blindado": {
        "name": "Ogro Blindado", "terrain": "giants", "type": "miniboss", "element": "physical",
        "abilities": [
            {"type": "shield",    "value": 0.30},
            {"type": "stun",      "chance": 0.45},
            {"type": "armor_break","chance": 0.40, "value": 5},
        ],
        "loot": ["placa_ogro", "cinto_titã", "mineral_puro"],
        "tiers": {
            1: {"hp": 400, "damage": 30, "defense": 24, "xp": 118, "gold": (96, 178),
                "flavor": "🛡️ *Ogro Blindado — Rústico* usa restos de armadura como escudo.\n_\"Improvisado. Eficiente. Incômodo de remover.\"_"},
            2: {"hp": 864, "damage": 62, "defense": 49, "xp": 258, "gold": (215,390),
                "flavor": "🛡️ *Ogro Blindado — Reforçado* com armadura forjada.\n_\"Alguém investiu nisso. Você vai pagar o preço.\"_"},
            3: {"hp": 1866,"damage": 118,"defense": 93, "xp": 558, "gold": (446,768),
                "flavor": "🛡️ *Ogro Blindado Lendário* — uma fortaleza andando.\n_\"A armadura cresceu com ele. São uma coisa só agora.\"_"},
        },
    },
    "troll_regenerador": {
        "name": "Troll Regenerador", "terrain": "giants", "type": "miniboss", "element": "physical",
        "abilities": [
            {"type": "regen",     "value": 0.10},
            {"type": "lifesteal", "chance": 0.40, "value": 0.25},
            {"type": "stun",      "chance": 0.30},
        ],
        "loot": ["tecido_troll", "essencia_regeneracao", "sangue_troll"],
        "tiers": {
            1: {"hp": 380, "damage": 26, "defense": 12, "xp": 112, "gold": (90, 170),
                "flavor": "🔄 *Troll Regenerador — Lento* avança sem pressa.\n_\"Não tem pressa. Vai se curar de qualquer coisa que você faça.\"_"},
            2: {"hp": 820, "damage": 54, "defense": 25, "xp": 244, "gold": (200,365),
                "flavor": "🔄 *Troll Regenerador — Veloz* surpreende com rapidez.\n_\"Regeneração acelerou os reflexos também. Injusto.\"_"},
            3: {"hp": 1771,"damage": 104,"defense": 47, "xp": 528, "gold": (420,725),
                "flavor": "🔄 *Troll Imparável* — lenda viva do Vale.\n_\"Já tentaram de tudo. Fogo, magia, veneno. Sempre voltou.\"_"},
        },
    },
}
# fmt: on
