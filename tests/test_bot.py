import re

import pytest
from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from ecos_rpg.bot import app as bot_app
from ecos_rpg.bot import telas
from ecos_rpg.engine.estado import EstadoCombate
from ecos_rpg.engine.habilidades import CLASS_SKILLS


def test_barra_de_hp_e_escape_de_markdown():
    assert telas.barra_hp(50, 100) == "[█████░░░░░] 50/100"
    assert telas.barra_hp(-5, 100).startswith("[░░░░░░░░░░]")
    assert telas.barra_hp(5, 0).startswith("[░")
    assert telas.escapar("a_b*c`d[e") == "a\\_b\\*c\\`d\\[e"


@pytest.fixture
def aplicacao():
    app = ApplicationBuilder().token("123456:TESTE").updater(None).build()
    bot_app.registrar_handlers(app)
    return app


def _padroes(app) -> list[re.Pattern]:
    return [
        h.pattern
        for grupo in app.handlers.values()
        for h in grupo
        if isinstance(h, CallbackQueryHandler)
    ]


def test_todo_botao_do_combate_tem_handler(aplicacao):
    padroes = _padroes(aplicacao)
    estado = EstadoCombate()
    teclados = [
        telas.kb_combate(),
        telas.kb_extracao(1),
        telas.kb_extracao(2),
        telas.kb_elemento("imbue"),
        telas.kb_elemento("elem"),
        telas.kb_voltar_bastiao(),
        *(telas.kb_skills(classe, estado) for classe in CLASS_SKILLS),
    ]
    for kb in teclados:
        for linha in kb.inline_keyboard:
            for botao in linha:
                assert any(p.search(botao.callback_data) for p in padroes), botao.callback_data


def test_comandos_registrados(aplicacao):
    comandos = {
        c
        for grupo in aplicacao.handlers.values()
        for h in grupo
        for c in getattr(h, "commands", [])
    }
    assert {"status", "bastiao", "dungeon"} <= comandos


def test_main_nao_inicia_polling_ao_importar():
    import main

    assert callable(main.main)


def test_sem_token_falha_com_mensagem_clara(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BOT_TOKEN"):
        bot_app.criar_aplicacao()
