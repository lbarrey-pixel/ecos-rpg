"""Catálogo de cosméticos. Fonte única: o banco é sincronizado a partir daqui."""

# fmt: off
# key -> nome, tipo, exibição (texto do título ou emoji), preço em cristais (None = não vendável),
# se entra no sorteio VIP e se é exclusivo de fundador.
CATALOGO = {
    "title_implacavel":   {"name": "O Implacável",                "type": "title",    "display": "O Implacável",                "cost_crystals": 120,  "is_vip_pool": False, "is_founder": False},
    "title_amaldicoado":  {"name": "O Amaldiçoado",               "type": "title",    "display": "O Amaldiçoado",               "cost_crystals": 120,  "is_vip_pool": False, "is_founder": False},
    "title_escolhido":    {"name": "O Escolhido",                 "type": "title",    "display": "O Escolhido",                 "cost_crystals": 200,  "is_vip_pool": True,  "is_founder": False},
    "title_fantasma":     {"name": "O Fantasma",                  "type": "title",    "display": "O Fantasma",                  "cost_crystals": 200,  "is_vip_pool": True,  "is_founder": False},
    "title_ultimo":       {"name": "O Último",                    "type": "title",    "display": "O Último",                    "cost_crystals": 300,  "is_vip_pool": False, "is_founder": False},
    "title_devorador":    {"name": "O Devorador",                 "type": "title",    "display": "O Devorador",                 "cost_crystals": 300,  "is_vip_pool": False, "is_founder": False},
    "title_esquecido":    {"name": "O Esquecido",                 "type": "title",    "display": "O Esquecido",                 "cost_crystals": 150,  "is_vip_pool": True,  "is_founder": False},
    "title_sobrevivente": {"name": "Sobrevivente do Fim",         "type": "title",    "display": "Sobrevivente do Fim",         "cost_crystals": 500,  "is_vip_pool": False, "is_founder": False},
    "title_fundador":     {"name": "Sobrevivente do Primeiro Dia","type": "title",    "display": "Sobrevivente do Primeiro Dia","cost_crystals": None, "is_vip_pool": False, "is_founder": True},
    "insignia_caveira":   {"name": "Insígnia da Caveira",         "type": "insignia", "display": "💀",                          "cost_crystals": 80,   "is_vip_pool": False, "is_founder": False},
    "insignia_espada":    {"name": "Insígnia da Espada",          "type": "insignia", "display": "⚔️",                          "cost_crystals": 80,   "is_vip_pool": False, "is_founder": False},
    "insignia_escudo":    {"name": "Insígnia do Escudo",          "type": "insignia", "display": "🛡️",                          "cost_crystals": 80,   "is_vip_pool": False, "is_founder": False},
    "insignia_coroa":     {"name": "Insígnia da Coroa",           "type": "insignia", "display": "👑",                          "cost_crystals": 250,  "is_vip_pool": True,  "is_founder": False},
    "insignia_olho":      {"name": "Insígnia do Olho",            "type": "insignia", "display": "👁️",                          "cost_crystals": 150,  "is_vip_pool": True,  "is_founder": False},
    "insignia_fundador":  {"name": "Insígnia do Fundador",        "type": "insignia", "display": "🌑",                          "cost_crystals": None, "is_vip_pool": False, "is_founder": True},
    "aura_fogo":          {"name": "Aura de Fogo",                "type": "aura",     "display": "🔥",                          "cost_crystals": 100,  "is_vip_pool": False, "is_founder": False},
    "aura_gelo":          {"name": "Aura de Gelo",                "type": "aura",     "display": "❄️",                          "cost_crystals": 100,  "is_vip_pool": False, "is_founder": False},
    "aura_veneno":        {"name": "Aura de Veneno",              "type": "aura",     "display": "☠️",                          "cost_crystals": 100,  "is_vip_pool": False, "is_founder": False},
    "aura_raio":          {"name": "Aura de Raio",                "type": "aura",     "display": "⚡",                          "cost_crystals": 100,  "is_vip_pool": False, "is_founder": False},
    "aura_sombra":        {"name": "Aura de Sombra",              "type": "aura",     "display": "🌑",                          "cost_crystals": 180,  "is_vip_pool": True,  "is_founder": False},
    "aura_sagrado":       {"name": "Aura Sagrada",                "type": "aura",     "display": "✨",                          "cost_crystals": 180,  "is_vip_pool": True,  "is_founder": False},
    "aura_abismo":        {"name": "Aura do Abismo",              "type": "aura",     "display": "🕳️",                          "cost_crystals": 350,  "is_vip_pool": False, "is_founder": False},
    "frame_bronze":       {"name": "Moldura de Bronze",           "type": "frame",    "display": "🟫",                          "cost_crystals": 60,   "is_vip_pool": False, "is_founder": False},
    "frame_ferro":        {"name": "Moldura de Ferro",            "type": "frame",    "display": "⬛",                          "cost_crystals": 90,   "is_vip_pool": False, "is_founder": False},
}
# fmt: on

# tipo do cosmético -> coluna de characters que guarda o equipado.
# É a lista branca usada pelo repositório ao montar o UPDATE.
COLUNA_POR_TIPO = {
    "title": "cosmetic_title",
    "aura": "cosmetic_aura",
    "frame": "cosmetic_frame",
    "insignia": "cosmetic_insignia",
}


def nome_exibicao(char: dict) -> str:
    """Nome com cosméticos equipados. Ex.: ``🔥 *O Implacável* | Kael ⚔️``."""

    def visual(coluna: str) -> str:
        chave = char.get(coluna)
        return CATALOGO.get(chave, {}).get("display", "") if chave else ""

    partes = []
    if aura := visual("cosmetic_aura"):
        partes.append(aura)
    if titulo := visual("cosmetic_title"):
        partes.append(f"*{titulo}* |")
    partes.append(char.get("name", "?"))
    if insignia := visual("cosmetic_insignia"):
        partes.append(insignia)
    return " ".join(partes)
