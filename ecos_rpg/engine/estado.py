"""Estado de combate de um membro da dungeon.

É o que vai para a coluna ``dungeon_members.combat_state`` (JSONB). Um estado por
jogador, mesmo em instância compartilhada: cada um enfrenta a própria sequência de
salas, então nada aqui precisa de lock entre membros.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Any

FASES = (
    "combat",
    "miniboss_1",
    "extraction_1",
    "miniboss_2",
    "extraction_2",
    "boss",
    "done",
)

# Chaves antigas (prefixo "_") gravadas por versões anteriores do bot.
_CHAVES_LEGADAS = {
    "_phase_shifted": "phase_shifted",
    "_enemy_enraged": "enemy_enraged",
    "_terrain": "terrain",
    "_player_armorbreak": "player_armorbreak",
    "_await_imbue": "await_imbue",
    "_await_elem": "await_elem",
}


@dataclass
class EstadoCombate:
    phase: str = "combat"
    section: int = 1
    room: int = 0
    battles_won: int = 0
    gold_earned: int = 0
    enemy: dict[str, Any] | None = None
    in_combat: bool = False
    # efeitos: {tipo: {"duration": n, "value": x}}
    p_effects: dict[str, dict[str, Any]] = field(default_factory=dict)
    e_effects: dict[str, dict[str, Any]] = field(default_factory=dict)
    shield: int = 0
    atk_buff: float = 0.0
    atk_buff_dur: int = 0
    def_buff: float = 0.0
    def_buff_dur: int = 0
    skill_cds: dict[str, int] = field(default_factory=dict)
    imbue_element: str | None = None
    imbue_dur: int = 0
    next_crit: bool = False
    used_minibosses: list[str] = field(default_factory=list)
    phase_shifted: bool = False
    enemy_enraged: bool = False
    terrain: str = "lava"
    player_armorbreak: int = 0
    await_imbue: bool = False
    await_elem: str | None = None

    # ── inimigo ──────────────────────────────────────────────
    def inimigo_vivo(self) -> bool:
        return bool(self.enemy) and self.enemy.get("hp", 0) > 0

    def inimigo_hp_max(self) -> int:
        if not self.enemy:
            return 1
        return self.enemy.get("max_hp", self.enemy["hp"])

    def definir_inimigo(self, inimigo: dict[str, Any]) -> None:
        inimigo = dict(inimigo)
        inimigo["max_hp"] = inimigo["hp"]
        self.enemy = inimigo
        self.in_combat = True
        self.e_effects = {}
        self.phase_shifted = False
        self.enemy_enraged = False

    def bloqueado(self) -> bool:
        """Jogador congelado ou atordoado não age (fuga continua permitida)."""
        return any(k in self.p_effects for k in ("stun", "freeze"))

    # ── (de)serialização ─────────────────────────────────────
    def encode(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def decode(cls, raw: str | bytes | dict | None) -> EstadoCombate:
        if not raw:
            return cls()
        try:
            dados = json.loads(raw) if isinstance(raw, str | bytes) else dict(raw)
        except (ValueError, TypeError):
            return cls()
        if not isinstance(dados, dict):
            return cls()
        for antiga, nova in _CHAVES_LEGADAS.items():
            if antiga in dados and nova not in dados:
                dados[nova] = dados.pop(antiga)
        conhecidos = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in dados.items() if k in conhecidos})
