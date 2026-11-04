"""Monta a Application do Telegram: handlers e ciclo de vida do pool."""

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from ..ambiente import carregar
from ..db.migrar import aplicar_migracoes
from ..db.pool import criar_pool
from .bastiao import get_bastiao_handlers
from .dungeon import get_dungeon_handlers
from .start import get_character_creation_handler
from .status import status


async def _ao_iniciar(app: Application) -> None:
    pool = await criar_pool(carregar().database_url)
    async with pool.acquire() as conn:
        await aplicar_migracoes(conn)
    app.bot_data["pool"] = pool


async def _ao_encerrar(app: Application) -> None:
    pool = app.bot_data.get("pool")
    if pool:
        await pool.close()


def registrar_handlers(app: Application) -> None:
    app.add_handler(get_character_creation_handler())
    app.add_handler(CommandHandler("status", status))
    for handler in (*get_bastiao_handlers(), *get_dungeon_handlers()):
        app.add_handler(handler)


def criar_aplicacao() -> Application:
    token = carregar().bot_token
    if not token:
        raise ValueError("BOT_TOKEN não definido (veja .env.example)")
    app = (
        ApplicationBuilder().token(token).post_init(_ao_iniciar).post_shutdown(_ao_encerrar).build()
    )
    registrar_handlers(app)
    return app
