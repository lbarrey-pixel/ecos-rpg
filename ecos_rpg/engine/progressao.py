"""Experiência, nível e pontos de status. Funções puras; a persistência fica em ``db``."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

PONTOS_POR_NIVEL = 3
NIVEL_MAX = 99
CUSTO_RESET_OURO = 80_000
CUSTO_RESET_CRISTAIS = 50
BONUS_OURO_VIP = 1.15

# Bônus por nível: pequeno de propósito, o grosso vem dos pontos alocados.
BONUS_NIVEL = {"hp_max": 4, "mana_max": 3, "attack": 1, "defense": 1}

# stat alocável -> (coluna afetada, ganho por ponto). As chaves também nomeiam as colunas
# ``sp_<stat>``; o repositório só monta SQL a partir desta tabela.
STAT_EFFECT = {
    "vitalidade": {"col": "hp_max", "value": 8},
    "espirito": {"col": "mana_max", "value": 6},
    "forca": {"col": "attack", "value": 2},
    "resistencia": {"col": "defense", "value": 2},
    "sorte": {"col": "luck", "value": 1},
    "espiritualidade": {"col": "spirituality", "value": 2},
}

STAT_LABELS = {
    "vitalidade": "❤️ Vitalidade (+8 HP máx)",
    "espirito": "💧 Espírito (+6 Mana máx)",
    "forca": "⚔️ Força (+2 Ataque)",
    "resistencia": "🛡️ Resistência (+2 Defesa)",
    "sorte": "🍀 Sorte (+1 Sorte)",
    "espiritualidade": "✨ Espiritualidade (+2 Espiritualidade)",
}


def xp_para_proximo(nivel: int) -> int:
    """XP para sair de ``nivel`` e ir ao seguinte. Crescimento de 15% ao nível."""
    return int(100 * nivel * (1.15 ** (nivel - 1)))


def xp_total_do_nivel(nivel_alvo: int) -> int:
    return sum(xp_para_proximo(n) for n in range(1, nivel_alvo))


@dataclass(frozen=True)
class ResultadoXp:
    xp: int
    xp_proximo: int
    nivel: int
    niveis_ganhos: int
    pontos_ganhos: int

    @property
    def subiu(self) -> bool:
        return self.niveis_ganhos > 0

    def bonus(self, coluna: str) -> int:
        return self.niveis_ganhos * BONUS_NIVEL[coluna]


def aplicar_xp(nivel: int, xp: int, xp_proximo: int, ganho: int) -> ResultadoXp:
    """Soma XP e processa quantos níveis forem necessários."""
    xp += ganho
    ganhos = 0
    while xp >= xp_proximo and nivel < NIVEL_MAX:
        xp -= xp_proximo
        nivel += 1
        ganhos += 1
        xp_proximo = xp_para_proximo(nivel)
    return ResultadoXp(xp, xp_proximo, nivel, ganhos, ganhos * PONTOS_POR_NIVEL)


def reembolso_de_pontos(char: dict) -> dict[str, int]:
    """Pontos alocados por stat (só os maiores que zero)."""
    return {s: char[f"sp_{s}"] for s in STAT_EFFECT if char.get(f"sp_{s}", 0) > 0}


def vip_ativo(expira_em: datetime | None, agora: datetime | None = None) -> bool:
    if expira_em is None:
        return False
    agora = agora or datetime.now(UTC)
    if expira_em.tzinfo is None:
        expira_em = expira_em.replace(tzinfo=UTC)
    return expira_em > agora


def multiplicador_ouro(expira_em: datetime | None, agora: datetime | None = None) -> float:
    return BONUS_OURO_VIP if vip_ativo(expira_em, agora) else 1.0


def barra_xp(atual: int, proximo: int, tamanho: int = 10) -> str:
    fracao = min(1.0, atual / proximo) if proximo else 0.0
    cheio = int(fracao * tamanho)
    return f"[{'█' * cheio}{'░' * (tamanho - cheio)}] {int(fracao * 100)}%"


def bloco_nivel(char: dict, agora: datetime | None = None) -> str:
    agora = agora or datetime.now(UTC)
    vip = ""
    expira = char.get("vip_expires_at")
    if vip_ativo(expira, agora):
        if expira.tzinfo is None:
            expira = expira.replace(tzinfo=UTC)
        fundador = " 🌑" if char.get("is_founder") else ""
        vip = f"\n👑 VIP ativo — {(expira - agora).days} dias restantes{fundador}"
    pontos = char.get("status_points", 0)
    pontos_txt = f"\n⭐ *{pontos} ponto(s) de status disponível(is)*" if pontos > 0 else ""
    return (
        f"⚔️ Nível *{char['level']}*  {barra_xp(char['experience'], char['experience_next'])}\n"
        f"✨ {char['experience']}/{char['experience_next']} XP{pontos_txt}{vip}"
    )
