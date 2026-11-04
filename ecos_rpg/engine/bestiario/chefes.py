"""Bosses finais de cada terreno e O Fim, boss especial que pode surgir em qualquer um."""

# fmt: off
CHEFES = {
    "o_inferno_vivo": {
        "name": "O Inferno Vivo", "terrain": "lava", "type": "boss", "element": "fire",
        "abilities": [
            {"type": "burn",      "chance": 1.00, "value": 0.08},
            {"type": "multi_hit", "chance": 0.55},
            {"type": "mana_drain","chance": 0.60, "value": 25},
            {"type": "phase_shift","hp_threshold": 0.50},
        ],
        "loot": ["coração_inferno", "essencia_vulcao_puro", "cristal_lendario_fogo"],
        "tiers": {
            1: {"hp": 700,  "damage": 45,  "defense": 20, "xp": 380, "gold": (280, 480),
                "flavor": "🌋 *O Inferno Vivo — Desperto* abre os olhos pela primeira vez em séculos.\n_\"O calor é tão intenso que o ar distorce. Você sente antes de ver.\"_\n\n⚠️ _Aos 50% de HP: entra em modo Fúria — dano +40%_"},
            2: {"hp": 1512, "damage": 92,  "defense": 40, "xp": 830, "gold": (600,980),
                "flavor": "🌋 *O Inferno Vivo — Furioso* — a lava obedece.\n_\"O terreno inteiro virou extensão dele. Cada passo queima.\"_\n\n⚠️ _Aos 50% de HP: lava inunda o campo — burn constante_"},
            3: {"hp": 3265, "damage": 178, "defense": 76, "xp": 1800,"gold": (1250,2000),
                "flavor": "🌋 *O Inferno Vivo — Transcendente* — não é mais um ser. É um evento.\n_\"O vulcão e ele são a mesma coisa agora.\"_\n\n⚠️ _Aos 50% de HP: absorve lava — cura 15% HP instantâneo_"},
        },
    },

    "o_silencio_eterno": {
        "name": "O Silêncio Eterno", "terrain": "glacial", "type": "boss", "element": "ice",
        "abilities": [
            {"type": "freeze",    "chance": 0.70},
            {"type": "mana_drain","chance": 0.75, "value": 30},
            {"type": "shield",    "value": 0.20},
            {"type": "phase_shift","hp_threshold": 0.50},
        ],
        "loot": ["cristal_silencio", "alma_congelada", "essencia_absoluta"],
        "tiers": {
            1: {"hp": 680,  "damage": 40,  "defense": 25, "xp": 370, "gold": (270, 465),
                "flavor": "❄️ *O Silêncio Eterno — Adormecido* começa a se mover.\n_\"Não há som. Nem vento. O silêncio em si te ataca.\"_\n\n⚠️ _Aos 50% de HP: campo congela — todos recebem freeze passivo_"},
            2: {"hp": 1469, "damage": 82,  "defense": 51, "xp": 808, "gold": (580,945),
                "flavor": "❄️ *O Silêncio Eterno — Desperto* expande o campo de gelo.\n_\"O que você ouvia antes era ruído. Agora há apenas silêncio.\"_\n\n⚠️ _Aos 50% de HP: drena toda mana restante_"},
            3: {"hp": 3174, "damage": 158, "defense": 98, "xp": 1750,"gold": (1200,1950),
                "flavor": "❄️ *O Silêncio Eterno — Absoluto* — a temperatura atinge zero absoluto.\n_\"Palavras congelam antes de sair da boca.\"_\n\n⚠️ _Aos 50% de HP: escudo de gelo absorve próximos 3 ataques_"},
        },
    },

    "a_nevoa_consciente": {
        "name": "A Névoa Consciente", "terrain": "chemical", "type": "boss", "element": "poison",
        "abilities": [
            {"type": "poison",    "chance": 1.00, "value": 0.07},
            {"type": "mana_drain","chance": 0.65, "value": 22},
            {"type": "lifesteal", "chance": 0.50, "value": 0.20},
            {"type": "phase_shift","hp_threshold": 0.50},
        ],
        "loot": ["essencia_nevoa", "veneno_consciente", "nucleo_quimico"],
        "tiers": {
            1: {"hp": 650,  "damage": 38,  "defense": 14, "xp": 365, "gold": (265, 455),
                "flavor": "☠️ *A Névoa Consciente — Fragmentada* te circunda lentamente.\n_\"Não há como não respirar. Não há como não envenenar.\"_\n\n⚠️ _Aos 50% de HP: se fragmenta — ataca 3x por rodada_"},
            2: {"hp": 1404, "damage": 78,  "defense": 29, "xp": 796, "gold": (565,920),
                "flavor": "☠️ *A Névoa Consciente — Unificada* assume forma densa.\n_\"Decidiu que prefere uma forma. A forma é aterrorizante.\"_\n\n⚠️ _Aos 50% de HP: veneno acumulado explode — dano em área_"},
            3: {"hp": 3031, "damage": 150, "defense": 55, "xp": 1720,"gold": (1160,1900),
                "flavor": "☠️ *A Névoa Onipresente* — está em todo lugar ao mesmo tempo.\n_\"Onde você respira, ela está. Onde você não respira, ela também.\"_\n\n⚠️ _Aos 50% de HP: cura total — acontece uma vez_"},
        },
    },

    "o_ultimo_gigante": {
        "name": "O Último Gigante", "terrain": "giants", "type": "boss", "element": "physical",
        "abilities": [
            {"type": "stun",      "chance": 0.60},
            {"type": "armor_break","chance": 0.55, "value": 6},
            {"type": "multi_hit", "chance": 0.40},
            {"type": "phase_shift","hp_threshold": 0.50},
        ],
        "loot": ["coração_gigante", "ossada_titã", "legado_colossus"],
        "tiers": {
            1: {"hp": 750,  "damage": 50,  "defense": 22, "xp": 390, "gold": (290, 495),
                "flavor": "🗿 *O Último Gigante — Caído* se levanta do chão.\n_\"Estava de joelhos. Não estava derrotado. Há diferença.\"_\n\n⚠️ _Aos 50% de HP: fúria — velocidade dobra_"},
            2: {"hp": 1620, "damage": 102, "defense": 45, "xp": 850, "gold": (615,1000),
                "flavor": "🗿 *O Último Gigante — Erguido* em toda sua escala.\n_\"A sombra dele cobre o campo de batalha inteiro.\"_\n\n⚠️ _Aos 50% de HP: bate no chão — stun garantido em todos_"},
            3: {"hp": 3500, "damage": 196, "defense": 85, "xp": 1900,"gold": (1300,2100),
                "flavor": "🗿 *O Último Gigante — Imortal* — o vale inteiro treme.\n_\"Não pode ser morto. Pode ser convencido a parar. Por enquanto.\"_\n\n⚠️ _Aos 50% de HP: regenera 20% HP — acontece uma vez_"},
        },
    },
}

ESPECIAIS = {
    "o_fim": {
        "name": "O Fim", "terrain": "all", "type": "boss_special", "element": "void",
        "abilities": [
            {"type": "phase_shift", "hp_threshold": 0.50},
            {"type": "void_drain",  "chance": 1.00, "value": 25},
            {"type": "fear",        "chance": 0.30},
            {"type": "undying",     "chance": 0.03},
            {"type": "burn",        "chance": 0.50, "value": 0.05},
            {"type": "freeze",      "chance": 0.50},
            {"type": "poison",      "chance": 0.50, "value": 0.05},
        ],
        "spawn_chance": {1: 0.005, 2: 0.010, 3: 0.020},  # 0.5%, 1%, 2%
        "loot": ["fragmento_do_fim", "eco_void", "memoria_perdida", "item_lendario_garantido"],
        "tiers": {
            1: {"hp": 1200, "damage": 80,  "defense": 35, "xp": 1500, "gold": (600, 1000),
                "flavor": (
                    "🌑 *O Fim* emerge do nada.\n\n"
                    "_O chão para de existir por um momento.\n"
                    "O silêncio engole tudo — o barulho das suas armaduras, seu próprio coração.\n"
                    "Algo que não devia estar aqui está aqui._\n\n"
                    "⚠️ **AVISO:** Fuga gratuita disponível agora. Uma vez que o combate começar, não há retorno.\n"
                    "⚠️ _Tier 1: morte quase garantida em solo. PT recomendado._"
                )},
            2: {"hp": 2600, "damage": 155, "defense": 65, "xp": 3200, "gold": (1200,2000),
                "flavor": (
                    "🌑 *O Fim — Desperto* te reconhece.\n\n"
                    "_Desta vez é diferente. Ele sabe seu nome.\n"
                    "Sabe quantas vezes você quase morreu.\n"
                    "E sorri — se é que isso é um sorriso._\n\n"
                    "⚠️ **AVISO:** Fuga gratuita disponível agora.\n"
                    "⚠️ _Tier 2: sobrevivência em solo exige build perfeita e recursos completos._"
                )},
            3: {"hp": 5600, "damage": 290, "defense": 120, "xp": 7000, "gold": (2500,4000),
                "flavor": (
                    "🌑 *O Fim — Transcendente* desce.\n\n"
                    "_Não há palavras para o que você está vendo.\n"
                    "Os registros dizem que sobreviventes tentaram descrever.\n"
                    "Os registros estão em branco a partir daí._\n\n"
                    "⚠️ **AVISO:** Fuga gratuita disponível agora.\n"
                    "⚠️ _Tier 3: o maior desafio do jogo. Recompensa lendária garantida._"
                )},
        },
    },
}
# fmt: on
