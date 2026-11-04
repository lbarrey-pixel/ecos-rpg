"""Percorre os handlers da dungeon com um CallbackQuery falso e um Postgres real."""

import random
from types import SimpleNamespace

import pytest

from ecos_rpg.bot import dungeon as bot_dg
from ecos_rpg.config import CLASSES
from ecos_rpg.db import dungeon as repo_dg
from ecos_rpg.db import inventario, personagens


class QueryFalsa:
    def __init__(self, dados: str):
        self.data = dados
        self.textos: list[str] = []
        self.botoes: list[str] = []
        self.alertas: list[str] = []

    async def answer(self, texto=None, show_alert=False):
        if texto:
            self.alertas.append(texto)

    async def edit_message_text(self, texto, parse_mode=None, reply_markup=None):
        self.textos.append(texto)
        if reply_markup is not None:
            self.botoes = [b.callback_data for linha in reply_markup.inline_keyboard for b in linha]


async def _clicar(pool, telegram_id: int, dados: str) -> QueryFalsa:
    query = QueryFalsa(dados)
    update = SimpleNamespace(callback_query=query, effective_user=SimpleNamespace(id=telegram_id))
    context = SimpleNamespace(application=SimpleNamespace(bot_data={"pool": pool}))
    await bot_dg.dungeon_callback(update, context)
    return query


@pytest.fixture(autouse=True)
def sem_pausas(monkeypatch):
    async def nada(_):
        return None

    monkeypatch.setattr(bot_dg, "_pausa", nada)
    random.seed(20)


async def _heroi(pool, telegram_id=1, classe="guerreiro", **colunas):
    await personagens.get_or_create_player(pool, telegram_id, "jogador")
    char = await personagens.create_character(
        pool, telegram_id, "Heroi", classe, CLASSES[classe]["stats"]
    )
    for coluna, valor in colunas.items():
        await pool.execute(f"UPDATE characters SET {coluna} = $1 WHERE id = $2", valor, char["id"])
    return char


async def test_run_completa_de_ponta_a_ponta(pool):
    # ataque absurdo: cada golpe mata; vida absurda: nada mata o jogador
    char = await _heroi(pool, attack=100_000, hp_max=1_000_000, hp_current=1_000_000)
    q = await _clicar(pool, 1, "dg_enter_solo")
    assert "dg_attack" in q.botoes

    passos = 0
    while await repo_dg.get_active_member(pool, char["id"]):
        passos += 1
        assert passos < 100, "a run não terminou"
        if "dg_boss_fight" in q.botoes:
            q = await _clicar(pool, 1, "dg_boss_fight")
        elif "dg_cont_boss" in q.botoes:
            q = await _clicar(pool, 1, "dg_cont_boss")
        elif "dg_cont_s2" in q.botoes:
            q = await _clicar(pool, 1, "dg_cont_s2")
        elif "dg_next" in q.botoes:
            q = await _clicar(pool, 1, "dg_next")
        else:
            q = await _clicar(pool, 1, "dg_attack")

    final = await personagens.get_character(pool, 1)
    assert any("Extração bem-sucedida" in t for t in q.textos)
    assert final["gold"] > 100 and final["level"] > 1
    assert final["hp_current"] == final["hp_max"]
    inv = await inventario.get_inventory_count(pool, char["id"])
    assert inv["mochila"] == 0 and inv["bau"] > 0
    assert (await repo_dg.find_open_instance(pool, "solo")) is None


async def test_extrair_em_combate_e_recusado(pool):
    await _heroi(pool, attack=1, hp_max=10_000, hp_current=10_000)
    await _clicar(pool, 1, "dg_enter_solo")
    q = await _clicar(pool, 1, "dg_extract")
    assert q.textos == []  # nada acontece: em combate o caminho é fugir
    assert await repo_dg.get_active_member(pool, 1) is not None


async def test_botao_antigo_nao_pula_a_luta(pool):
    await _heroi(pool, attack=1, hp_max=10_000, hp_current=10_000)
    await _clicar(pool, 1, "dg_enter_solo")
    membro = await repo_dg.get_active_member(pool, 1)
    sala_antes = membro["combat_state"]
    await _clicar(pool, 1, "dg_next")
    assert (await repo_dg.get_active_member(pool, 1))["combat_state"] == sala_antes


async def test_morte_apaga_mochila_e_encerra_a_run(pool):
    char = await _heroi(pool, attack=1, defense=0, hp_max=5, hp_current=5)
    await inventario.add_item(pool, char["id"], "Ácido Puro", "material", location="mochila")
    await inventario.add_item(
        pool, char["id"], "Anel de Proteção", "accessory", location="bolso_seguro"
    )
    q = await _clicar(pool, 1, "dg_enter_solo")
    for _ in range(30):
        if await repo_dg.get_active_member(pool, 1) is None:
            break
        q = await _clicar(pool, 1, "dg_attack")
    assert any("Você morreu" in t for t in q.textos)
    restantes = await inventario.get_inventory(pool, char["id"])
    assert {i["location"] for i in restantes} == {"bolso_seguro"}
    assert (await personagens.get_character(pool, 1))["hp_current"] == 5  # restaurado


async def test_skill_sem_mana_vira_alerta_sem_perder_o_turno(pool):
    await _heroi(pool, mana_current=0, hp_max=10_000, hp_current=10_000)
    await _clicar(pool, 1, "dg_enter_solo")
    antes = (await repo_dg.get_active_member(pool, 1))["hp_current"]
    q = await _clicar(pool, 1, "dg_sk_investida")
    assert q.alertas and "Mana insuficiente" in q.alertas[-1]
    assert (await repo_dg.get_active_member(pool, 1))["hp_current"] == antes
