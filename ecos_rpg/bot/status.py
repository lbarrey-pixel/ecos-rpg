from telegram import Update
from telegram.ext import ContextTypes

from ..config import BLESSINGS, CLASSES
from ..db.personagens import get_character
from ..engine.progressao import bloco_nivel
from .contexto import pool_de
from .telas import escapar


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    char = await get_character(pool_de(context), update.effective_user.id)
    if not char:
        await update.message.reply_text("Você ainda não tem um personagem. Use /start para criar.")
        return

    cls = CLASSES[char["class"]]
    bencao = BLESSINGS.get(char["active_blessing"]) if char["active_blessing"] else None
    sangue = char["blood_on_hands"]

    sangue_txt = ""
    if sangue > 0:
        alerta = "⚠️ Alto risco de ser caçado" if sangue >= 5 else ""
        sangue_txt = f"\n🩸 Sangue nas Mãos: {sangue} {alerta}"
    bencao_txt = (
        f"\n{bencao['emoji']} Bênção: {bencao['name']}" if bencao else "\n🕯️ Bênção: Nenhuma"
    )

    await update.message.reply_text(
        f"📜 *{escapar(char['name'])}* — {cls['emoji']} {cls['name']}\n"
        f"{bloco_nivel(dict(char))}\n"
        f"💰 Ouro: {char['gold']}\n\n"
        f"❤️ HP: {char['hp_current']}/{char['hp_max']}\n"
        f"💧 Mana: {char['mana_current']}/{char['mana_max']}\n\n"
        f"⚔️ Ataque: {char['attack']}\n"
        f"🛡️ Defesa: {char['defense']}\n"
        f"✨ Espiritualidade: {char['spirituality']}\n"
        f"🍀 Sorte: {char['luck']}\n"
        f"🎒 Capacidade de carga: {char['carry_capacity']} slots\n"
        f"🔒 Bolsos seguros: {char['safe_slots']} slots"
        f"{bencao_txt}"
        f"{sangue_txt}",
        parse_mode="Markdown",
    )
