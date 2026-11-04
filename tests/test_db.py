"""Testes de integração: aplicam a migração num schema descartável do Postgres.

``TEST_DATABASE_URL`` aponta para um servidor (o job de CI e o docker-compose usam
``postgresql://ecos:ecos@localhost:5432/ecos``). Sem servidor, os testes são pulados.
"""

import asyncpg
import pytest

from ecos_rpg.config import CLASSES
from ecos_rpg.db import dungeon as dg
from ecos_rpg.db import economia, grupos, inventario, personagens
from ecos_rpg.db.migrar import aplicar_migracoes
from ecos_rpg.engine import progressao
from ecos_rpg.engine.estado import EstadoCombate


async def _personagem(pool, telegram_id=1, classe="guerreiro"):
    await personagens.get_or_create_player(pool, telegram_id, f"jogador{telegram_id}")
    return await personagens.create_character(
        pool, telegram_id, f"Heroi{telegram_id}", classe, CLASSES[classe]["stats"]
    )


async def test_migracao_e_idempotente(pool):
    async with pool.acquire() as conn:
        assert await aplicar_migracoes(conn) == []
        assert await conn.fetchval("SELECT count(*) FROM cosmetics_catalog") > 0


async def test_criar_personagem_add_item_e_equipar(pool):
    char = await _personagem(pool)
    assert char["level"] == 1 and char["experience_next"] == 100 and char["gold"] == 100
    assert char["hp_current"] == char["hp_max"] == CLASSES["guerreiro"]["stats"]["hp_max"]

    espada = await inventario.add_item(
        pool,
        char["id"],
        "Espada de Ferro",
        "weapon",
        element="physical",
        location="mochila",
        equip_slot="weapon",
        durability_max=30,
    )
    assert espada["durability_current"] == espada["durability_max"] == 30

    await inventario.transfer_loot_to_bau(pool, char["id"])
    equipada = await inventario.equip_item(pool, char["id"], espada["id"], "weapon")
    assert equipada["location"] == "equipado"

    outra = await inventario.add_item(
        pool, char["id"], "Espada de Aço", "weapon", equip_slot="weapon"
    )
    await inventario.equip_item(pool, char["id"], outra["id"], "weapon")
    equipados = await inventario.get_equipped_items(pool, char["id"])
    assert [i["item_name"] for i in equipados] == ["Espada de Aço"]
    assert (await inventario.get_inventory_count(pool, char["id"])) == {
        "bau": 1,
        "mochila": 0,
        "bolso_seguro": 0,
        "equipado": 1,
    }


async def test_equipar_nao_mexe_no_equipamento_de_outro_personagem(pool):
    a, b = await _personagem(pool, 1), await _personagem(pool, 2)
    item_a = await inventario.add_item(pool, a["id"], "Arco Curto", "weapon", equip_slot="weapon")
    item_b = await inventario.add_item(pool, b["id"], "Arco Longo", "weapon", equip_slot="weapon")
    await inventario.equip_item(pool, a["id"], item_a["id"], "weapon")
    await inventario.equip_item(pool, b["id"], item_b["id"], "weapon")
    assert len(await inventario.get_equipped_items(pool, a["id"])) == 1
    # tentar equipar o item de outro jogador não faz nada
    assert await inventario.equip_item(pool, a["id"], item_b["id"], "weapon") is None
    assert await inventario.equip_item(pool, a["id"], item_a["id"], "slot_inexistente") is None


async def test_consumiveis_empilham_e_remocao_parcial(pool):
    char = await _personagem(pool)
    await inventario.add_item(pool, char["id"], "Antídoto", "consumable")
    pilha = await inventario.add_item(pool, char["id"], "Antídoto", "consumable", quantity=2)
    assert pilha["quantity"] == 3
    await inventario.remove_item(pool, pilha["id"], 2)
    assert (await inventario.get_inventory(pool, char["id"]))[0]["quantity"] == 1
    await inventario.remove_item(pool, pilha["id"], 1)
    assert await inventario.get_inventory(pool, char["id"]) == []


async def test_morte_apaga_mochila_e_preserva_bolso_seguro(pool):
    char = await _personagem(pool)
    await inventario.add_item(pool, char["id"], "Ácido Puro", "material", location="mochila")
    await inventario.add_item(
        pool, char["id"], "Colar de Sorte", "accessory", location="bolso_seguro"
    )
    await inventario.clear_run_loot(pool, char["id"])
    restantes = await inventario.get_inventory(pool, char["id"])
    assert [i["location"] for i in restantes] == ["bolso_seguro"]


async def test_xp_sobe_nivel_e_aplica_bonus(pool):
    char = await _personagem(pool)
    r = await personagens.add_experience(pool, char["id"], 250)
    assert r["leveled_up"] and r["level"] == 2 and r["points_gained"] == 3
    novo = await personagens.get_character(pool, 1)
    assert novo["experience"] == 150 and novo["experience_next"] == progressao.xp_para_proximo(2)
    assert novo["hp_max"] == char["hp_max"] + 4 and novo["status_points"] == 3
    assert novo["attack"] == char["attack"] + 1
    assert "error" in await personagens.add_experience(pool, 9999, 10)


async def test_alocar_e_resetar_pontos(pool):
    char = await _personagem(pool)
    await personagens.add_experience(pool, char["id"], 250)
    assert "error" in await personagens.allocate_stat(pool, char["id"], "inexistente")
    assert "error" in await personagens.allocate_stat(pool, char["id"], "forca", 99)
    r = await personagens.allocate_stat(pool, char["id"], "forca", 2)
    assert r["new_value"] == char["attack"] + 1 + 4 and r["points_left"] == 1

    # sem ouro suficiente
    assert "Ouro insuficiente" in (await personagens.reset_stat_points(pool, char["id"]))["error"]
    await personagens.update_gold(pool, char["id"], progressao.CUSTO_RESET_OURO)
    r = await personagens.reset_stat_points(pool, char["id"])
    assert r["points_back"] == 2 and r["paid_with"] == "gold"
    depois = await personagens.get_character(pool, 1)
    assert depois["attack"] == char["attack"] + 1 and depois["sp_forca"] == 0
    assert depois["status_points"] == 3
    assert depois["gold"] == char["gold"]
    await economia.update_crystals(pool, char["id"], 60, "teste")
    assert (
        "não tem pontos" in (await personagens.reset_stat_points(pool, char["id"], True))["error"]
    )


async def test_reset_com_cristais_registra_transacao(pool):
    char = await _personagem(pool)
    await personagens.add_experience(pool, char["id"], 250)
    await personagens.allocate_stat(pool, char["id"], "sorte")
    await economia.update_crystals(pool, char["id"], 60, "compra")
    r = await personagens.reset_stat_points(pool, char["id"], use_crystals=True)
    assert r["paid_with"] == "crystals"
    historico = await economia.get_crystal_history(pool, char["id"])
    assert [(h["amount"], h["reason"]) for h in historico] == [(-50, "stat_reset"), (60, "compra")]


async def test_cristais_nunca_ficam_negativos(pool):
    char = await _personagem(pool)
    assert (await economia.update_crystals(pool, char["id"], 10, "bonus"))["balance"] == 10
    assert (
        "insuficientes" in (await economia.update_crystals(pool, char["id"], -11, "gasto"))["error"]
    )
    assert (await personagens.get_character(pool, 1))["crystals"] == 10


async def test_cosmeticos_desbloquear_equipar_e_remover(pool):
    char = await _personagem(pool)
    assert "error" in await economia.equip_cosmetic(pool, char["id"], "aura_fogo")
    assert "error" in await economia.unlock_cosmetic(pool, char["id"], "nao_existe")
    assert (await economia.unlock_cosmetic(pool, char["id"], "aura_fogo"))["success"]
    assert "já possui" in (await economia.unlock_cosmetic(pool, char["id"], "aura_fogo"))["error"]
    assert (await economia.equip_cosmetic(pool, char["id"], "aura_fogo"))["slot"] == "aura"
    assert (await personagens.get_character(pool, 1))["cosmetic_aura"] == "aura_fogo"
    assert [
        c["cosmetic_key"] for c in await economia.get_character_cosmetics(pool, char["id"])
    ] == ["aura_fogo"]
    await economia.unequip_cosmetic(pool, char["id"], "aura")
    assert (await personagens.get_character(pool, 1))["cosmetic_aura"] is None
    assert "error" in await economia.unequip_cosmetic(pool, char["id"], "capa")


async def test_vip_acumula_dias_e_textos_tem_limite(pool):
    char = await _personagem(pool)
    primeiro = await economia.activate_vip(pool, char["id"], 30)
    segundo = await economia.activate_vip(pool, char["id"], 30, is_founder=True)
    assert (segundo["expires_at"] - primeiro["expires_at"]).days == 30 and segundo["is_founder"]
    assert (await economia.set_war_cry(pool, char["id"], "  Pela luz!  "))["success"]
    assert (await personagens.get_character(pool, 1))["war_cry"] == "Pela luz!"
    assert "error" in await economia.set_epitaph(pool, char["id"], "x" * 81)


async def test_estado_de_combate_vai_e_volta_pelo_jsonb(pool):
    char = await _personagem(pool)
    inst = await dg.create_instance(pool, "lava", "solo")
    estado = EstadoCombate(terrain="lava", room=2)
    estado.definir_inimigo({"name": "Teste", "hp": 50})
    estado.skill_cds = {"cura": 2}
    await dg.join_instance(pool, inst["id"], char["id"], 100, 50, estado)

    estado.room, estado.shield = 3, 12
    await dg.save_member(pool, char["id"], 80, 40, estado)
    membro = await dg.get_active_member(pool, char["id"])
    assert (membro["hp_current"], membro["mana_current"], membro["terrain"]) == (80, 40, "lava")
    volta = EstadoCombate.decode(membro["combat_state"])
    assert volta == estado


async def test_so_uma_run_ativa_por_personagem_e_pode_voltar_depois(pool):
    char = await _personagem(pool)
    inst = await dg.create_instance(pool, "giants", "solo")
    await dg.join_instance(pool, inst["id"], char["id"], 1, 1, EstadoCombate())
    with pytest.raises(asyncpg.UniqueViolationError):
        await dg.join_instance(pool, inst["id"], char["id"], 1, 1, EstadoCombate())

    outro = await _personagem(pool, 2)
    await dg.join_instance(pool, inst["id"], outro["id"], 1, 1, EstadoCombate())
    await dg.exit_member(pool, char["id"], "extracted")
    await dg.close_if_empty(pool, inst["id"])
    assert (await dg.get_instance(pool, inst["id"]))["status"] == "active"  # o outro segue lá
    assert await dg.get_active_member(pool, char["id"]) is None

    await dg.join_instance(pool, inst["id"], char["id"], 1, 1, EstadoCombate())  # volta
    for c in (char, outro):
        await dg.exit_member(pool, c["id"], "dead")
    await dg.close_if_empty(pool, inst["id"])
    assert (await dg.get_instance(pool, inst["id"]))["status"] == "finished"
    assert await dg.find_open_instance(pool, "solo") is None


async def test_instancia_aberta_mais_recente(pool):
    await dg.create_instance(pool, "lava", "solo")
    ultima = await dg.create_instance(pool, "glacial", "solo")
    assert (await dg.find_open_instance(pool, "solo"))["id"] == ultima["id"]
    assert await dg.find_open_instance(pool, "party") is None


async def test_grupo_tem_no_maximo_quatro(pool):
    chars = [await _personagem(pool, n) for n in range(1, 6)]
    grupo = await grupos.create_party(pool, chars[0]["id"])
    for c in chars[1:4]:
        assert await grupos.join_party(pool, grupo["id"], c["id"])
    assert await grupos.join_party(pool, grupo["id"], chars[4]["id"]) is None
    assert len(await grupos.get_party_members(pool, grupo["id"])) == 4
    assert (await grupos.get_party_of_character(pool, chars[2]["id"]))["id"] == grupo["id"]
    await grupos.disband_party(pool, grupo["id"])
    assert await grupos.get_party_of_character(pool, chars[2]["id"]) is None


async def test_check_de_bencao_aceita_so_as_do_jogo(pool):
    from ecos_rpg.config import BLESSINGS

    char = await _personagem(pool)
    for chave in BLESSINGS:
        await pool.execute(
            "UPDATE characters SET active_blessing = $1 WHERE id = $2", chave, char["id"]
        )
    with pytest.raises(asyncpg.CheckViolationError):
        await pool.execute(
            "UPDATE characters SET active_blessing = 'pacto' WHERE id = $1", char["id"]
        )
