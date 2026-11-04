"""Um turno completo do jogador: efeitos, ação escolhida, reação do inimigo e buffs.

A ordem espelha o que o jogador vê na tela: dano de efeitos primeiro, depois a ação,
depois o inimigo. Toda decisão sobre *o que acontece* fica aqui; o bot só mostra.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import combate, fluxo, habilidades
from .estado import EstadoCombate


@dataclass
class ResultadoTurno:
    hp: int
    mana: int
    msgs: list[str] = field(default_factory=list)
    # continua | inimigo_morto | jogador_morto | fugiu | escolha | invalida | sem_inimigo
    desfecho: str = "continua"
    ouro_perdido: int = 0


def _validar(acao: str, char: dict, estado: EstadoCombate, mana: int) -> str | None:
    if acao.startswith("sk_"):
        return habilidades.validar(acao[3:], estado, mana, char.get("class"))
    if acao.startswith("imbue_"):
        ok = estado.await_imbue and acao[6:] in habilidades.ELEMENTOS_ESCOLHA
        return None if ok else "❌ Nada para imbuir agora."
    if acao.startswith("elem_"):
        ok = estado.await_elem is not None and acao[5:] in habilidades.ELEMENTOS_ESCOLHA
        return None if ok else "❌ Nenhuma magia aguardando elemento."
    if acao not in ("attack", "flee"):
        return "❌ Ação desconhecida."
    return None


def resolver_turno(
    char: dict,
    estado: EstadoCombate,
    hp: int,
    mana: int,
    acao: str,
    rng: random.Random | None = None,
) -> ResultadoTurno:
    rng = rng or random
    if not estado.inimigo_vivo():
        return ResultadoTurno(hp, mana, ["Não há inimigo!"], "sem_inimigo")
    if erro := _validar(acao, char, estado, mana):
        return ResultadoTurno(hp, mana, [erro], "invalida")

    hp, msgs = combate.tick_efeitos_jogador(estado, hp, char["hp_max"])
    res = ResultadoTurno(hp, mana, msgs)
    if hp <= 0:
        res.desfecho = "jogador_morto"
        return res

    # congelado/atordoado perde a ação, mas ainda pode tentar fugir
    if estado.bloqueado() and acao != "flee":
        res.msgs.append("⚡ Você não pode agir este turno!")
        _reacao_inimigo(res, estado, rng, com_efeitos=False)
        return res

    inimigo_ja_agiu = False
    if acao == "attack":
        dano = combate.ferir_inimigo(estado, combate.dano_fisico(char, estado.enemy, estado))
        res.msgs.append(f"⚔️ Você ataca: {dano} de dano físico!")

    elif acao.startswith("sk_"):
        res.hp, res.mana, m = habilidades.executar(
            acao[3:], char, estado, res.hp, res.mana, rng=rng
        )
        res.msgs += m
        if estado.await_imbue or estado.await_elem:
            res.desfecho = "escolha"
            return res

    elif acao.startswith("imbue_"):
        res.mana, m = habilidades.imbuir(estado, acao[6:], res.mana)
        res.msgs += m

    elif acao.startswith("elem_"):
        res.hp, res.mana, m = habilidades.escolher_elemento(
            estado, char, acao[5:], res.hp, res.mana, rng=rng
        )
        res.msgs += m

    elif acao == "flee":
        sorte = combate.sorte_efetiva(char)
        fuga = fluxo.tentar_fuga(estado, sorte, rng)
        if fuga.ok:
            res.desfecho, res.ouro_perdido = "fugiu", fuga.ouro_perdido
            return res
        res.msgs.append(f"❌ Fuga falhou! ({int(fuga.chance * 100)}% de chance)")
        res.hp, res.mana, m = combate.turno_inimigo(estado, res.hp, res.mana, rng)
        res.msgs += m
        inimigo_ja_agiu = True

    if not estado.inimigo_vivo():
        res.desfecho = "inimigo_morto"
        return res
    if not inimigo_ja_agiu:
        _reacao_inimigo(res, estado, rng, com_efeitos=True)
        if res.desfecho == "inimigo_morto":
            return res

    combate.tick_buffs(estado)
    if res.hp <= 0:
        res.desfecho = "jogador_morto"
    return res


def _reacao_inimigo(
    res: ResultadoTurno, estado: EstadoCombate, rng: random.Random, com_efeitos: bool
) -> None:
    if com_efeitos:
        _, m = combate.tick_efeitos_inimigo(estado)
        res.msgs += m
        if not estado.inimigo_vivo():
            res.desfecho = "inimigo_morto"
            return
    res.hp, res.mana, m = combate.turno_inimigo(estado, res.hp, res.mana, rng)
    res.msgs += m
    if res.hp <= 0:
        res.desfecho = "jogador_morto"
