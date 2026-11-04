import os
import random
import uuid

import asyncpg
import pytest

from ecos_rpg.db.migrar import aplicar_migracoes
from ecos_rpg.engine.estado import EstadoCombate


class RngFixo(random.Random):
    """random() sempre devolve o mesmo valor: 0.0 faz todo teste de chance passar."""

    def __init__(self, valor: float = 0.0):
        super().__init__(0)
        self.valor = valor

    def random(self) -> float:
        return self.valor


@pytest.fixture
def bruxo() -> dict:
    return {
        "class": "bruxo",
        "level": 10,
        "attack": 18,
        "defense": 10,
        "spirituality": 55,
        "luck": 22,
        "hp_max": 100,
        "mana_max": 160,
    }


@pytest.fixture
def guerreiro() -> dict:
    return {
        "class": "guerreiro",
        "level": 5,
        "attack": 32,
        "defense": 50,
        "spirituality": 8,
        "luck": 18,
        "hp_max": 220,
        "mana_max": 60,
    }


def inimigo(**kw) -> dict:
    base = {
        "key": "teste",
        "name": "Teste",
        "hp": 100,
        "damage": 20,
        "defense": 0,
        "abilities": [],
        "terrain": "lava",
        "type": "normal",
        "xp": 10,
        "gold_min": 5,
        "gold_max": 5,
    }
    return base | kw


@pytest.fixture
def estado():
    est = EstadoCombate(terrain="lava")
    est.definir_inimigo(inimigo())
    return est


DSN = os.getenv("TEST_DATABASE_URL", "postgresql://ecos:ecos@localhost:5432/ecos")


@pytest.fixture
async def pool():
    schema = f"teste_{uuid.uuid4().hex[:10]}"
    try:
        admin = await asyncpg.connect(DSN, timeout=3)
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(f"Postgres indisponível: {exc}")
    await admin.execute(f"CREATE SCHEMA {schema}")
    pool = await asyncpg.create_pool(
        DSN, min_size=1, max_size=4, server_settings={"search_path": schema}
    )
    try:
        async with pool.acquire() as conn:
            assert await aplicar_migracoes(conn) == ["0001_schema.sql"]
        yield pool
    finally:
        await pool.close()
        await admin.execute(f"DROP SCHEMA {schema} CASCADE")
        await admin.close()
