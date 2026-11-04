"""Aplica ``migrations/*.sql`` em ordem, uma vez cada. Uso: ``python -m ecos_rpg.db.migrar``."""

import asyncio
from pathlib import Path

import asyncpg

from ..ambiente import carregar
from .economia import sincronizar_catalogo

PASTA = Path(__file__).parent / "migrations"


async def aplicar_migracoes(conn: asyncpg.Connection) -> list[str]:
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
    )
    feitas = {r["name"] for r in await conn.fetch("SELECT name FROM schema_migrations")}
    novas = []
    for arq in sorted(PASTA.glob("*.sql")):
        if arq.name in feitas:
            continue
        async with conn.transaction():
            await conn.execute(arq.read_text(encoding="utf-8"))
            await conn.execute("INSERT INTO schema_migrations (name) VALUES ($1)", arq.name)
        novas.append(arq.name)
    await sincronizar_catalogo(conn)
    return novas


async def _main() -> None:
    conn = await asyncpg.connect(carregar().database_url)
    try:
        novas = await aplicar_migracoes(conn)
    finally:
        await conn.close()
    print("migrações aplicadas:", ", ".join(novas) or "nenhuma")


if __name__ == "__main__":
    asyncio.run(_main())
