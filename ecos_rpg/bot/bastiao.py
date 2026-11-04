"""Hub do Bastião: inventário e as lojas que ainda estão em construção."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from ..config import EQUIP_SLOTS, RARITY_EMOJI
from ..db.inventario import get_inventory, get_inventory_count
from ..db.personagens import get_character
from .contexto import pool_de
from .telas import escapar

# callback -> texto da loja. Nenhuma tem lógica ainda; o dado separa o roteiro do handler.
LOJAS = {
    "b_traversador": (
        "🏪 *O Atravessador*\n\n"
        '_"Ei, ei — olha quem voltou vivo.\n'
        'Não que eu duvidasse, claro. Bom... talvez um pouco."_\n\n'
        "Um homem miúdo de olhos espertos te observa de trás de uma bancada "
        "repleta de bugigangas, frascos e ferramentas de origem duvidosa.\n\n"
        "🚧 _Abrindo o estoque em breve..._"
    ),
    "b_sabio": (
        "📜 *O Sábio*\n\n"
        '_"O conhecimento é a única coisa que não apodrece.\n'
        'Venha, jovem Extrator. Tenho pergaminhos que fariam um morto se levantar."_\n\n'
        "Um ancião de barba longa e olhos que viram o fim do mundo "
        "te observa com interesse calculado.\n\n"
        "🚧 _Organizando os pergaminhos..._"
    ),
    "b_ferreiro": (
        "⚒️ *O Ferreiro*\n\n"
        '_"Traz o que tá quebrado. Eu conserto.\n'
        "Não pergunta como, não pergunta de onde veio o material.\n"
        'A gente tem um acordo tácito aqui."_\n\n'
        "O barulho de martelo no metal ecoa pela caverna.\n\n"
        "🚧 _Acendendo a forja..._"
    ),
    "b_templo": (
        "🕯️ *Templo das Bênçãos*\n\n"
        '_"A superfície não tem misericórdia.\nMas nós temos. Por um preço justo."_\n\n'
        "Velas iluminam rostos cansados em oração.\n\n"
        "🚧 _Preparando as bênçãos..._"
    ),
    "b_mercado": (
        "🔄 *Mercado do Bastião*\n\n"
        "Barracas improvisadas, vozes disputando preço,\n"
        "o cheiro de coisa rara misturado com coisa suspeita.\n\n"
        "🚧 _Montando as barracas..._"
    ),
    "b_banco": (
        "🏦 *Banco do Bastião*\n\n"
        '_"Seu ouro fica seguro aqui.\nMais seguro do que você na superfície, pelo menos."_\n\n'
        "🚧 _Contando as moedas..._"
    ),
}


def _teclado_bastiao() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏪 O Atravessador", callback_data="b_traversador"),
                InlineKeyboardButton("🎒 Inventário", callback_data="b_inventario"),
            ],
            [
                InlineKeyboardButton("📜 O Sábio", callback_data="b_sabio"),
                InlineKeyboardButton("⚒️ Ferreiro", callback_data="b_ferreiro"),
            ],
            [
                InlineKeyboardButton("🕯️ Templo das Bênçãos", callback_data="b_templo"),
                InlineKeyboardButton("🔄 Mercado", callback_data="b_mercado"),
            ],
            [InlineKeyboardButton("🏦 Banco", callback_data="b_banco")],
        ]
    )


def _voltar() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("◀️ Voltar ao Bastião", callback_data="b_main")]]
    )


def _teclado_inventario() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏦 Baú do Bastião", callback_data="b_inv_bau"),
                InlineKeyboardButton("🎒 Mochila de Run", callback_data="b_inv_mochila"),
            ],
            [InlineKeyboardButton("⚔️ Equipamentos", callback_data="b_inv_equipado")],
            [InlineKeyboardButton("◀️ Voltar ao Bastião", callback_data="b_main")],
        ]
    )


def _linha_item(item, com_durabilidade: bool = False) -> str:
    emoji = RARITY_EMOJI.get(item["rarity"], "⬜")
    dur = ""
    if com_durabilidade and item["durability_max"]:
        dur = f" [{item['durability_current']}/{item['durability_max']}]"
    return f"{emoji} {item['item_name']} x{item['quantity']}{dur}\n"


async def _resumo(pool, char) -> str:
    inv = await get_inventory_count(pool, char["id"])
    slots = inv["mochila"] + inv["bolso_seguro"]
    return (
        f"💰 {char['gold']} moedas  "
        f"📦 {inv['bau']} itens no baú  "
        f"🎒 {slots}/{char['carry_capacity']} slots de run"
    )


async def bastiao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = pool_de(context)
    char = await get_character(pool, update.effective_user.id)
    if not char:
        await update.message.reply_text("Você ainda não tem um personagem. Use /start para criar.")
        return
    await update.message.reply_text(
        "🏰 *O Último Bastião*\n\n"
        "O cheiro de fumaça de tocha e ferro fundido te recebe.\n"
        "Ao redor, sobreviventes que apostaram tudo neste buraco escuro.\n"
        "É feio. É barulhento. É o único lar que resta.\n\n"
        f"{await _resumo(pool, char)}\n\nPara onde você vai?",
        parse_mode="Markdown",
        reply_markup=_teclado_bastiao(),
    )


async def _inventario(query, pool, char, destino: str) -> None:
    if destino == "b_inventario":
        inv = await get_inventory_count(pool, char["id"])
        loot = inv["mochila"] + inv["bolso_seguro"]
        texto = (
            f"🎒 *Inventário de {escapar(char['name'])}*\n\n"
            f"🏦 Baú do Bastião: *{inv['bau']} itens* guardados\n"
            f"🎒 Mochila de Run: *{loot}/{char['carry_capacity']}* slots\n"
            f"🔒 Bolsos seguros: *{inv['bolso_seguro']}/{char['safe_slots']}* usados\n"
            f"⚔️ Equipamentos: *{inv['equipado']}* itens equipados\n\n"
            "_Itens no baú ficam seguros no Bastião.\n"
            "Itens na mochila vão com você — e podem ser perdidos._"
        )
    elif destino == "b_inv_bau":
        itens = await get_inventory(pool, char["id"], "bau")
        texto = "🏦 *Baú do Bastião*\n\n"
        texto += (
            "".join(_linha_item(i, True) for i in itens)
            if itens
            else "_O baú está vazio.\nVá à superfície e traga algo de volta._"
        )
    elif destino == "b_inv_mochila":
        mochila = await get_inventory(pool, char["id"], "mochila")
        seguros = await get_inventory(pool, char["id"], "bolso_seguro")
        total = len(mochila) + len(seguros)
        texto = f"🎒 *Mochila de Run* ({total}/{char['carry_capacity']} slots)\n\n"
        texto += f"*Slots normais* ({len(mochila)}):\n"
        texto += "".join(_linha_item(i) for i in mochila) or "_Vazio_\n"
        texto += f"\n*🔒 Bolsos seguros* ({len(seguros)}/{char['safe_slots']}):\n"
        texto += "".join(f"🔒 {i['item_name']} x{i['quantity']}\n" for i in seguros) or (
            "_Nenhum item protegido_\n"
        )
        texto += "\n_Slots normais são perdidos ao morrer.\nBolsos seguros são sempre preservados._"
    else:  # b_inv_equipado
        equipados = {i["equip_slot"]: i for i in await get_inventory(pool, char["id"], "equipado")}
        texto = f"⚔️ *Equipamentos de {escapar(char['name'])}*\n\n"
        for chave, nome in EQUIP_SLOTS.items():
            item = equipados.get(chave)
            if not item:
                texto += f"{nome}: _— vazio —_\n"
                continue
            dur = ""
            if item["durability_max"]:
                pct = int(item["durability_current"] / item["durability_max"] * 100)
                farol = "🟢" if pct > 60 else "🟡" if pct > 25 else "🔴"
                dur = f" {farol} {item['durability_current']}/{item['durability_max']}"
            emoji = RARITY_EMOJI.get(item["rarity"], "⬜")
            texto += f"{nome}: {emoji} *{item['item_name']}*{dur}\n"
        texto += (
            "\n_Equipamentos não ocupam slots de loot.\n"
            "Podem ser perdidos ao morrer (chance por raridade)._"
        )
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=_teclado_inventario())


async def bastiao_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = pool_de(context)
    char = await get_character(pool, update.effective_user.id)
    if not char:
        await query.edit_message_text("Use /start para criar seu personagem.")
        return
    dados = query.data

    if dados == "b_main":
        await query.edit_message_text(
            f"🏰 *O Último Bastião*\n\n{await _resumo(pool, char)}\n\nPara onde você vai?",
            parse_mode="Markdown",
            reply_markup=_teclado_bastiao(),
        )
    elif dados == "b_inventario" or dados.startswith("b_inv_"):
        await _inventario(query, pool, char, dados)
    elif dados in LOJAS:
        await query.edit_message_text(LOJAS[dados], parse_mode="Markdown", reply_markup=_voltar())


def get_bastiao_handlers():
    return [
        CommandHandler("bastiao", bastiao),
        CallbackQueryHandler(bastiao_callback, pattern="^b_"),
    ]
