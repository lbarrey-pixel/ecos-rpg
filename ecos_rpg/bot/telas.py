"""Textos e teclados do combate. Sem acesso a banco."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..engine.combate import ICONES_EFEITO
from ..engine.estado import EstadoCombate
from ..engine.habilidades import CLASS_SKILLS, SKILLS

TERRAIN_EMOJI = {"lava": "🌋", "glacial": "❄️", "chemical": "☠️", "giants": "🗿"}
TERRAIN_NAME = {
    "lava": "Terras de Lava",
    "glacial": "Wasteland Glacial",
    "chemical": "Nuvem Química",
    "giants": "Vale dos Gigantes",
}
LINHA = "—" * 22


def escapar(texto: str) -> str:
    """Escapa o que o Markdown legado do Telegram interpretaria em texto vindo do usuário."""
    for c in ("_", "*", "`", "["):
        texto = texto.replace(c, "\\" + c)
    return texto


def barra_hp(hp: int, hp_max: int) -> str:
    pct = max(0.0, min(1.0, hp / hp_max)) if hp_max > 0 else 0.0
    cheio = int(pct * 10)
    return f"[{'█' * cheio}{'░' * (10 - cheio)}] {hp}/{hp_max}"


def efeitos_str(efeitos: dict) -> str:
    return "  ".join(
        f"{ICONES_EFEITO.get(e, '•')}{e}({d['duration']}t)" for e, d in efeitos.items()
    )


def rodape_jogador(char: dict, hp: int, mana: int) -> str:
    return f"{LINHA}\n*Você:* ❤️ {hp}/{char['hp_max']}  🔷 {mana}/{char['mana_max']}"


def kb_combate() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⚔️ Atacar", callback_data="dg_attack"),
                InlineKeyboardButton("✨ Skills", callback_data="dg_skills"),
            ],
            [
                InlineKeyboardButton("🎒 Item", callback_data="dg_item"),
                InlineKeyboardButton("🏃 Fugir", callback_data="dg_flee"),
            ],
        ]
    )


def kb_skills(classe: str, estado: EstadoCombate) -> InlineKeyboardMarkup:
    linhas = []
    for chave in CLASS_SKILLS.get(classe, []):
        sk = SKILLS[chave]
        cd = estado.skill_cds.get(chave, 0)
        rotulo = sk["name"]
        if sk["mana"] > 0:
            rotulo += f" ({sk['mana']}🔷)"
        if cd > 0:
            rotulo += f" ⏳{cd}"
        linhas.append([InlineKeyboardButton(rotulo, callback_data=f"dg_sk_{chave}")])
    linhas.append([InlineKeyboardButton("◀️ Voltar", callback_data="dg_back")])
    return InlineKeyboardMarkup(linhas)


def kb_elemento(prefixo: str) -> InlineKeyboardMarkup:
    """``prefixo``: 'imbue' (Embeber Flecha) ou 'elem' (Magia Elemental)."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔥 Fogo", callback_data=f"dg_{prefixo}_fire"),
                InlineKeyboardButton("🧊 Gelo", callback_data=f"dg_{prefixo}_ice"),
            ],
            [InlineKeyboardButton("☠️ Veneno", callback_data=f"dg_{prefixo}_poison")],
            [InlineKeyboardButton("◀️ Cancelar", callback_data="dg_back")],
        ]
    )


def kb_extracao(secao: int) -> InlineKeyboardMarkup:
    destino = "dg_cont_s2" if secao == 1 else "dg_cont_boss"
    rotulo = "➡️ Continuar (Seção 2)" if secao == 1 else "🗡️ Enfrentar o Boss"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚪 Extrair Agora", callback_data="dg_extract")],
            [InlineKeyboardButton(rotulo, callback_data=destino)],
        ]
    )


def kb_voltar_bastiao() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏰 Voltar ao Bastião", callback_data="b_main")]]
    )


def texto_inimigo(
    titulo: str, terreno: str, char: dict, estado: EstadoCombate, hp: int, mana: int
) -> str:
    e = estado.enemy
    txt = (
        f"{TERRAIN_EMOJI[terreno]} {titulo}\n\n"
        f"👹 *{e['name']}*\n"
        f"_{e.get('flavor', '')}_\n\n"
        f"❤️ {barra_hp(e['hp'], estado.inimigo_hp_max())}\n"
        f"{rodape_jogador(char, hp, mana)}"
    )
    if efx := efeitos_str(estado.p_effects):
        txt += f"\n{efx}"
    return txt


def texto_resultado(
    char: dict, estado: EstadoCombate, hp: int, mana: int, terreno: str, msgs: list[str]
) -> str:
    e = estado.enemy or {}
    barra = barra_hp(e["hp"], estado.inimigo_hp_max()) if e else "—"
    corpo = "\n".join(msgs) if msgs else "_Sem eventos._"
    txt = (
        f"{TERRAIN_EMOJI.get(terreno, '🌑')} *Combate*\n\n"
        f"{corpo}\n\n"
        f"👹 *{e.get('name', '?')}*: {barra}\n"
        f"{rodape_jogador(char, hp, mana)}"
    )
    if efx := efeitos_str(estado.p_effects):
        txt += f"\n_{efx}_"
    return txt
