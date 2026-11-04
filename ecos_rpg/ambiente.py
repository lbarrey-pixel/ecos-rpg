"""Configuração de execução lida do ambiente (.env)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Ambiente:
    bot_token: str
    database_url: str


def carregar() -> Ambiente:
    return Ambiente(
        bot_token=os.getenv("BOT_TOKEN", ""),
        database_url=os.getenv("DATABASE_URL", "postgresql://ecos:ecos@localhost:5432/ecos"),
    )
