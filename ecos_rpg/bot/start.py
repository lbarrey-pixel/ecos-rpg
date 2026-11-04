"""Criação de personagem: escolha de classe, nome e confirmação."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from ..config import CLASSES
from ..db.personagens import create_character, get_character, get_or_create_player
from .contexto import pool_de
from .telas import escapar

CHOOSING_CLASS, VIEWING_CLASS, TYPING_NAME, CONFIRMING = range(4)


def _teclado_classes() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"{c['emoji']} {c['name']}", callback_data=f"class_{k}")]
            for k, c in CLASSES.items()
        ]
    )


def _teclado_detalhe(class_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Escolher esta classe",
                    callback_data=f"confirm_class_{class_key}",
                )
            ],
            [InlineKeyboardButton("◀️ Voltar às classes", callback_data="back_to_classes")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pool = pool_de(context)
    await get_or_create_player(pool, user.id, user.username or user.first_name)
    char = await get_character(pool, user.id)

    if char:
        cls = CLASSES[char["class"]]
        await update.message.reply_text(
            f"🌑 *{char['name']} retorna às sombras do Bastião.*\n\n"
            f"{cls['emoji']} {cls['name']} — veterano das ruínas\n"
            f"❤️ {char['hp_current']}/{char['hp_max']} HP  "
            f"💧 {char['mana_current']}/{char['mana_max']} Mana\n"
            f"💰 {char['gold']} moedas no bolso\n\n"
            f"A superfície não vai esperar.\n\n"
            f"/dungeon — Entrar na superfície\n"
            f"/bastiao — O Último Bastião\n"
            f"/status — Ver atributos",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🌑 *ECOS DO FIM*\n\n"
        "A era medieval não terminou com glória.\n"
        "Terminou com silêncio.\n\n"
        "O que restou da humanidade desceu fundo — escavou, construiu, sobreviveu.\n"
        "Hoje vivem em *O Último Bastião*, cidade cravada nas entranhas da terra.\n"
        "Fria. Escura. Mas ainda viva.\n\n"
        "A superfície existe. Hostil, mutada, implacável.\n"
        "Mas lá em cima estão os recursos que o Bastião precisa para não apagar.\n\n"
        "Os *Extratores* são os poucos insanos o suficiente para subir.\n"
        "Entram nas ruínas. Coletam o que podem. Tentam voltar.\n"
        "Nem todos conseguem.\n\n"
        "Escolha quem você será:",
        parse_mode="Markdown",
        reply_markup=_teclado_classes(),
    )
    return CHOOSING_CLASS


async def choose_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    class_key = query.data.removeprefix("class_")
    if class_key not in CLASSES:
        return CHOOSING_CLASS
    cls = CLASSES[class_key]
    context.user_data["chosen_class"] = class_key

    s = cls["stats"]
    await query.edit_message_text(
        f"{cls['emoji']} *{cls['name']}*\n"
        f"_{cls['lore']}_\n\n"
        f"〔 Atributos base 〕\n"
        f"❤️ {s['hp_max']} HP   💧 {s['mana_max']} Mana\n"
        f"⚔️ {s['attack']} Atq   🛡️ {s['defense']} Def\n"
        f"✨ {s['spirituality']} Espirit   🍀 {s['luck']} Sorte\n"
        f"🎒 {s['carry_capacity']} slots de carga   🔒 {s['safe_slots']} bolsos seguros\n\n"
        f"_{cls['playstyle']}_",
        parse_mode="Markdown",
        reply_markup=_teclado_detalhe(class_key),
    )
    return VIEWING_CLASS


async def back_to_classes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Escolha quem você será:", reply_markup=_teclado_classes())
    return CHOOSING_CLASS


async def confirm_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    class_key = query.data.removeprefix("confirm_class_")
    if class_key not in CLASSES:
        return VIEWING_CLASS
    context.user_data["chosen_class"] = class_key
    cls = CLASSES[class_key]
    await query.edit_message_text(
        f"{cls['emoji']} *{cls['name']}* — escolha feita.\n\n"
        "Como te chamarão nas ruínas, Extrator?",
        parse_mode="Markdown",
    )
    return TYPING_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not 2 <= len(name) <= 24:
        await update.message.reply_text(
            "❌ Nomes no Bastião têm entre 2 e 24 caracteres.\n"
            "Até os mortos merecem um nome decente. Tente novamente:"
        )
        return TYPING_NAME

    context.user_data["chosen_name"] = name
    cls = CLASSES[context.user_data["chosen_class"]]
    teclado = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚔️ Confirmar — entrar no Bastião", callback_data="confirm_yes")],
            [InlineKeyboardButton("🔄 Reconsiderar", callback_data="confirm_no")],
        ]
    )
    await update.message.reply_text(
        f"📜 *Registro de Extrator*\n\n"
        f"*Nome:* {escapar(name)}\n"
        f"*Classe:* {cls['emoji']} {cls['name']}\n\n"
        f"_Uma vez registrado, seu nome ecoa pelas pedras do Bastião.\n"
        f"Tem certeza?_",
        parse_mode="Markdown",
        reply_markup=teclado,
    )
    return CONFIRMING


async def confirm_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_no":
        await query.edit_message_text(
            "As pedras do Bastião guardam segredos de quem hesitou.\nEscolha novamente:"
        )
        await query.message.reply_text("Escolha sua classe:", reply_markup=_teclado_classes())
        return CHOOSING_CLASS

    user = update.effective_user
    class_key = context.user_data["chosen_class"]
    name = context.user_data["chosen_name"]
    cls = CLASSES[class_key]
    await create_character(pool_de(context), user.id, name, class_key, cls["stats"])

    await query.edit_message_text(
        f"🌑 *{escapar(name)} desperta no ventre da terra.*\n\n"
        f"O cheiro de pedra úmida e fumaça de tocha envolve tudo.\n"
        f"Ao redor, o burburinho de *O Último Bastião* — "
        f"a única centelha de humanidade que restou.\n\n"
        f"Você é um {cls['emoji']} *{cls['name']}*.\n"
        f"O Bastião precisa do que só a superfície pode dar.\n"
        f"E a superfície não vai entregar por vontade própria.\n\n"
        f"_Que os ecos da sua passagem durem mais que você._\n\n"
        f"/dungeon — Sua primeira run\n"
        f"/bastiao — Conheça o Bastião\n"
        f"/status — Seus atributos",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌑 _O silêncio do Bastião te engole novamente._\nUse /start quando estiver pronto.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


def get_character_creation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CLASS: [CallbackQueryHandler(choose_class, pattern="^class_")],
            VIEWING_CLASS: [
                CallbackQueryHandler(confirm_class, pattern="^confirm_class_"),
                CallbackQueryHandler(back_to_classes, pattern="^back_to_classes$"),
            ],
            TYPING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            CONFIRMING: [CallbackQueryHandler(confirm_character, pattern="^confirm_(yes|no)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
    )
