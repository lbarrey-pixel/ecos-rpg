"""Acesso ao pool e trava por personagem, guardados no ``bot_data`` da aplicação."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from telegram.ext import ContextTypes


def pool_de(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["pool"]


@asynccontextmanager
async def trava_do_personagem(context: ContextTypes.DEFAULT_TYPE, character_id: int):
    """Serializa ações do mesmo personagem (duplo clique em botão não processa duas vezes)."""
    travas = context.application.bot_data.setdefault("travas", {})
    trava = travas.setdefault(character_id, asyncio.Lock())
    async with trava:
        yield
