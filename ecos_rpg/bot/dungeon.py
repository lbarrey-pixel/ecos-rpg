"""Handlers da dungeon. A regra está em ``engine``; aqui só carregamos o estado,
chamamos o motor, gravamos o resultado e escolhemos a tela."""

from __future__ import annotations

import asyncio
import random

import asyncpg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from ..config import CLASSES, DURABILITY, RARITY_EMOJI, TERRAINS
from ..db import dungeon as repo_dg
from ..db.inventario import (
    add_item,
    clear_run_loot,
    get_equipped_items,
    remove_item,
    transfer_loot_to_bau,
)
from ..db.personagens import add_experience, get_character, restore_hp_mana, update_gold
from ..engine import fluxo
from ..engine.combate import sorte_efetiva
from ..engine.estado import EstadoCombate
from ..engine.loot import EQUIPAVEIS, generate_loot
from ..engine.turno import resolver_turno
from .contexto import pool_de, trava_do_personagem
from .telas import (
    TERRAIN_EMOJI,
    TERRAIN_NAME,
    barra_hp,
    kb_combate,
    kb_elemento,
    kb_extracao,
    kb_skills,
    kb_voltar_bastiao,
    rodape_jogador,
    texto_inimigo,
    texto_resultado,
)

MODOS = ("solo",)  # "party" entra quando o comando de grupo existir
PAUSA_ENTRE_TELAS = 1.5
PAUSA_ENTRADA = 1.2


async def _pausa(segundos: float) -> None:
    await asyncio.sleep(segundos)


# ── carga e gravação ─────────────────────────────────────────
async def _carregar(pool, char: dict):
    membro = await repo_dg.get_active_member(pool, char["id"])
    if not membro:
        return None
    estado = EstadoCombate.decode(membro["combat_state"])
    estado.terrain = membro["terrain"]
    return membro, estado, membro["hp_current"], membro["mana_current"]


async def _salvar(pool, char: dict, hp: int, mana: int, estado: EstadoCombate) -> None:
    await repo_dg.save_member(pool, char["id"], hp, mana, estado)


async def _editar(query, texto: str, teclado=None) -> None:
    try:
        await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=teclado)
    except BadRequest as exc:
        if "not modified" not in str(exc).lower():  # clique repetido na mesma tela
            raise


# ── telas da run ─────────────────────────────────────────────
async def _mostrar_sala(query, pool, char, estado, hp, mana) -> None:
    tipo = fluxo.iniciar_sala(estado, char["level"])
    if tipo is None:
        return
    await _salvar(pool, char, hp, mana, estado)
    if tipo == "miniboss":
        titulo = f"*💀 MINI BOSS — Seção {estado.section}*"
    else:
        titulo = f"*Sala {estado.room}/{fluxo.SALAS_POR_SECAO} — Seção {estado.section}*"
    await _editar(
        query,
        texto_inimigo(titulo, estado.terrain, char, estado, hp, mana),
        kb_combate(),
    )


async def _mostrar_extracao(query, char, estado, hp, mana, secao: int) -> None:
    await _editar(
        query,
        f"{TERRAIN_EMOJI[estado.terrain]} *🚪 JANELA DE EXTRAÇÃO — Seção {secao}*\n\n"
        "_Um portal de retorno pulsa diante de você._\n\n"
        "Você sobreviveu até aqui — isso já é mais do que a maioria.\n"
        "Pode extrair agora e garantir o loot, ou continuar e arriscar tudo.\n\n"
        f"💰 Ouro acumulado: *{estado.gold_earned} 🪙*\n"
        f"❤️ {hp}/{char['hp_max']}  🔷 {mana}/{char['mana_max']}",
        kb_extracao(secao),
    )


async def _mostrar_boss(query, pool, char, estado, hp, mana) -> None:
    especial = fluxo.iniciar_boss(estado, char["level"])
    await _salvar(pool, char, hp, mana, estado)
    if especial:
        teclado = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⚔️ Enfrentar O Fim", callback_data="dg_boss_fight")],
                [InlineKeyboardButton("🏃 Fugir (grátis)", callback_data="dg_extract")],
            ]
        )
        await _editar(query, estado.enemy.get("flavor") or "🌑 *O Fim* emerge.", teclado)
        return
    await _editar(
        query,
        texto_inimigo("*👹 BOSS FINAL*", estado.terrain, char, estado, hp, mana),
        kb_combate(),
    )


# ── ações de combate ─────────────────────────────────────────
async def _processar_acao(query, pool, char: dict, acao: str) -> None:
    carga = await _carregar(pool, char)
    if not carga:
        await query.answer("Você não está em uma dungeon ativa.", show_alert=True)
        return
    membro, estado, hp, mana = carga

    res = resolver_turno(char, estado, hp, mana, acao)
    if res.desfecho in ("invalida", "sem_inimigo"):
        await query.answer(res.msgs[0], show_alert=True)
        return
    hp, mana = res.hp, res.mana

    if res.desfecho == "jogador_morto":
        await _morrer(query, pool, char, membro["dungeon_id"], estado)
    elif res.desfecho == "fugiu":
        await _salvar(pool, char, hp, mana, estado)
        await _extrair(
            query,
            pool,
            char,
            membro["dungeon_id"],
            estado,
            fugiu=True,
            perdido=res.ouro_perdido,
        )
    elif res.desfecho == "escolha":
        await _salvar(pool, char, hp, mana, estado)
        if estado.await_imbue:
            await _editar(query, "🏹 *Embeber Flecha — escolha o elemento:*", kb_elemento("imbue"))
        else:
            await _editar(query, "🌀 *Magia Elemental — escolha o elemento:*", kb_elemento("elem"))
    elif res.desfecho == "inimigo_morto":
        await _inimigo_morto(query, pool, char, membro["dungeon_id"], estado, hp, mana, res.msgs)
    else:
        await _salvar(pool, char, hp, mana, estado)
        await _editar(
            query,
            texto_resultado(char, estado, hp, mana, estado.terrain, res.msgs),
            kb_combate(),
        )


async def _inimigo_morto(query, pool, char, dungeon_id, estado, hp, mana, msgs) -> None:
    inimigo = dict(estado.enemy)
    vitoria = fluxo.registrar_vitoria(estado)
    msgs += ["", f"☠️ *{inimigo['name']} derrotado!*", f"💰 +{vitoria.ouro} 🪙"]

    prog = await add_experience(pool, char["id"], inimigo["xp"])
    msgs.append(f"✨ +{inimigo['xp']} XP")
    if prog.get("leveled_up"):
        msgs.append(f"⬆️ *Nível {prog['level']}!* +{prog['points_gained']} pontos de status")

    for item in generate_loot(inimigo, char["class"], sorte_efetiva(char)):
        dur = DURABILITY[item["rarity"]]["max"] if item["type"] in EQUIPAVEIS else None
        await add_item(
            pool,
            char["id"],
            item["name"],
            item["type"],
            rarity=item["rarity"],
            element=item["element"],
            location="mochila",
            equip_slot=item["equip_slot"],
            durability_max=dur,
        )
        msgs.append(f"{RARITY_EMOJI.get(item['rarity'], '⬜')} {item['name']}")

    if vitoria.bonus:
        msgs.append(f"🏆 *+{vitoria.bonus} 🪙 bônus de completar até o boss!*")
    await _salvar(pool, char, hp, mana, estado)

    texto = "\n".join(msgs)
    if vitoria.destino == "sala":
        teclado = InlineKeyboardMarkup(
            [[InlineKeyboardButton("➡️ Próxima sala", callback_data="dg_next")]]
        )
        await _editar(query, texto, teclado)
        return
    await _editar(query, texto)
    await _pausa(PAUSA_ENTRE_TELAS)
    if vitoria.destino == "extracao":
        await _mostrar_extracao(query, char, estado, hp, mana, vitoria.secao)
    else:
        await _extrair(query, pool, char, dungeon_id, estado)


# ── saída da run ─────────────────────────────────────────────
async def _extrair(query, pool, char, dungeon_id, estado, fugiu=False, perdido=0) -> None:
    async with pool.acquire() as conn, conn.transaction():
        await update_gold(conn, char["id"], estado.gold_earned)
        await transfer_loot_to_bau(conn, char["id"])
        await restore_hp_mana(conn, char["id"])
        await repo_dg.exit_member(conn, char["id"], "extracted")
        await repo_dg.close_if_empty(conn, dungeon_id)

    aviso = f"⚠️ Você fugiu. Perdeu {perdido} 🪙 na fuga.\n\n" if fugiu else ""
    await _editar(
        query,
        f"{TERRAIN_EMOJI.get(estado.terrain, '🌑')} "
        f"*{'Fuga bem-sucedida' if fugiu else 'Extração bem-sucedida'}!*\n\n"
        f"{aviso}Você voltou para o Bastião com vida.\n\n"
        f"💰 +{estado.gold_earned} 🪙 adicionados\n"
        "📦 Loot transferido para o Baú\n"
        "❤️ HP e Mana restaurados\n\n"
        "_Use /bastiao para ver o inventário._",
        kb_voltar_bastiao(),
    )


async def _morrer(query, pool, char, dungeon_id, estado) -> None:
    async with pool.acquire() as conn, conn.transaction():
        await clear_run_loot(conn, char["id"])
        equipados = [dict(i) for i in await get_equipped_items(conn, char["id"])]
        perdidos = set(fluxo.equipamentos_perdidos(equipados))
        nomes = []
        for item in equipados:
            if item["id"] in perdidos:
                await remove_item(conn, item["id"])
                nomes.append(f"{RARITY_EMOJI.get(item['rarity'], '⬜')} {item['item_name']}")
        await restore_hp_mana(conn, char["id"])
        await repo_dg.exit_member(conn, char["id"], "dead")
        await repo_dg.close_if_empty(conn, dungeon_id)

    perdas = ("\n❌ Perdeu: " + ", ".join(nomes)) if nomes else ""
    await _editar(
        query,
        f"{TERRAIN_EMOJI.get(estado.terrain, '🌑')} *Você morreu.*\n\n"
        "_A superfície levou mais um Extrator._\n\n"
        "❌ Loot da mochila: perdido\n"
        f"❌ Ouro coletado: perdido{perdas}\n"
        "✅ Bolsos seguros: preservados\n"
        "✅ HP e Mana: restaurados\n\n"
        "_O Bastião ainda precisa de você. Volte mais forte._",
        kb_voltar_bastiao(),
    )


# ── comando e roteamento ─────────────────────────────────────
async def dungeon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = pool_de(context)
    char = await get_character(pool, update.effective_user.id)
    if not char:
        await update.message.reply_text("Use /start para criar seu personagem.")
        return
    if await repo_dg.get_active_member(pool, char["id"]):
        await update.message.reply_text(
            "⚠️ Você já está em uma dungeon!\nUse os botões da mensagem de combate para continuar."
        )
        return

    teclado = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚔️ Entrar na Fila (Solo)", callback_data="dg_enter_solo")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="dg_cancel")],
        ]
    )
    await update.message.reply_text(
        "🌑 *Portal de Saída — O Bastião*\n\n"
        "O ar do lado de fora cheira a cinzas e possibilidade.\n"
        "Cada Extrator que sobe aposta tudo — e nem todos voltam.\n\n"
        f"❤️ {char['hp_current']}/{char['hp_max']}  🔷 {char['mana_current']}/{char['mana_max']}\n"
        f"🎒 Classe: *{CLASSES[char['class']]['name']}*\n\n"
        "_O terreno será sorteado ao entrar._",
        parse_mode="Markdown",
        reply_markup=teclado,
    )


async def _entrar(query, pool, char, modo: str) -> None:
    if modo not in MODOS:
        return
    if await repo_dg.get_active_member(pool, char["id"]):
        await query.answer("Você já está em uma dungeon.", show_alert=True)
        return
    instancia = await repo_dg.find_open_instance(pool, modo)
    if not instancia:
        instancia = await repo_dg.create_instance(pool, random.choice(list(TERRAINS)), modo)
    terreno = instancia["terrain"]
    estado = EstadoCombate(terrain=terreno)
    try:
        await repo_dg.join_instance(
            pool,
            instancia["id"],
            char["id"],
            char["hp_current"],
            char["mana_current"],
            estado,
        )
    except asyncpg.UniqueViolationError:
        await query.answer("Você já está em uma dungeon.", show_alert=True)
        return
    await _editar(
        query,
        f"{TERRAIN_EMOJI[terreno]} *Você entra em: {TERRAIN_NAME[terreno]}*\n\n_Prepare-se..._",
    )
    await _pausa(PAUSA_ENTRADA)
    await _mostrar_sala(query, pool, char, estado, char["hp_current"], char["mana_current"])


async def _navegar(query, pool, char, dados: str) -> None:
    """Botões que mudam de tela sem gastar turno."""
    carga = await _carregar(pool, char)
    if not carga:
        await query.answer("Você não está em uma dungeon ativa.", show_alert=True)
        return
    membro, estado, hp, mana = carga
    fase, em_combate = estado.phase, estado.in_combat

    if dados == "dg_skills" and em_combate:
        await _editar(query, "✨ *Skills disponíveis:*", kb_skills(char["class"], estado))
    elif dados == "dg_back" and estado.enemy:
        estado.await_imbue, estado.await_elem = (
            False,
            None,
        )  # cancelou a segunda escolha
        await _salvar(pool, char, hp, mana, estado)
        await _editar(
            query,
            texto_resultado(char, estado, hp, mana, estado.terrain, []),
            kb_combate(),
        )
    elif dados == "dg_next" and fase == "combat" and not em_combate:
        await _mostrar_sala(query, pool, char, estado, hp, mana)
    elif dados == "dg_cont_s2" and fase == "extraction_1":
        fluxo.continuar_secao_2(estado)
        await _mostrar_sala(query, pool, char, estado, hp, mana)
    elif dados == "dg_cont_boss" and fase == "extraction_2":
        await _mostrar_boss(query, pool, char, estado, hp, mana)
    elif dados == "dg_boss_fight" and fase == "boss" and estado.enemy and not em_combate:
        estado.in_combat = True
        await _salvar(pool, char, hp, mana, estado)
        e = estado.enemy
        await _editar(
            query,
            f"{TERRAIN_EMOJI[estado.terrain]} *👹 O FIM*\n\n"
            f"❤️ {barra_hp(e['hp'], estado.inimigo_hp_max())}\n"
            f"{rodape_jogador(char, hp, mana)}",
            kb_combate(),
        )
    elif dados == "dg_extract" and (
        fase in ("extraction_1", "extraction_2") or (fase == "boss" and not em_combate)
    ):
        # só nas janelas de extração ou diante de O Fim; em combate o caminho é a fuga
        await _extrair(query, pool, char, membro["dungeon_id"], estado)


ACOES_DE_TURNO = {"dg_attack": "attack", "dg_flee": "flee"}
NAVEGACAO = {
    "dg_skills",
    "dg_back",
    "dg_next",
    "dg_cont_s2",
    "dg_cont_boss",
    "dg_boss_fight",
    "dg_extract",
}


async def dungeon_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pool = pool_de(context)
    registro = await get_character(pool, update.effective_user.id)
    if not registro:
        await query.edit_message_text("Use /start para criar seu personagem.")
        return
    char = dict(registro)
    dados = query.data

    if dados == "dg_cancel":
        await query.edit_message_text("Cancelado. Use /dungeon para tentar novamente.")
        return

    async with trava_do_personagem(context, char["id"]):
        if dados.startswith("dg_enter_"):
            await _entrar(query, pool, char, dados.removeprefix("dg_enter_"))
        elif dados in ACOES_DE_TURNO:
            await _processar_acao(query, pool, char, ACOES_DE_TURNO[dados])
        elif dados.startswith(("dg_sk_", "dg_imbue_", "dg_elem_")):
            await _processar_acao(query, pool, char, dados.removeprefix("dg_"))
        elif dados == "dg_item":
            await query.answer("🎒 Sistema de itens em breve!", show_alert=True)
        elif dados in NAVEGACAO:
            await _navegar(query, pool, char, dados)


def get_dungeon_handlers():
    return [
        CommandHandler("dungeon", dungeon_command),
        CallbackQueryHandler(dungeon_callback, pattern="^dg_"),
    ]
