# 0002 — Catálogos orientados a dados

## Contexto

O jogo tem cinco classes, 25 habilidades, dezenas de inimigos em três tiers, tabelas de loot
por tipo de inimigo e um catálogo de cosméticos. Balancear é mexer em números o tempo todo;
a lógica quase não muda.

## Decisão

Classes, terrenos, bênçãos, raridades (`config.py`), habilidades (`SKILLS`), inimigos
(`engine/bestiario/`, um módulo por terreno), loot (`engine/loot.py`) e cosméticos
(`engine/cosmeticos.py`) são dicionários puros. O código que os interpreta é pequeno e
genérico: `habilidades.executar` despacha por `type`, `combate.turno_inimigo` por tipo de
habilidade do inimigo, `inimigos.get_enemy_stats` escala qualquer entrada.

O contrato entre catálogo e motor é testado: todo tipo de habilidade usado no bestiário
precisa estar em `HABILIDADES_CONHECIDAS`, todo inimigo tem os três tiers, todo terreno tem
pool de minibosses suficiente para duas seções. Uma entrada nova que o motor não entende
quebra o teste, não o jogador.

O catálogo de cosméticos também é copiado para o banco (`cosmetics_catalog`) no `migrar`,
com upsert, porque `character_cosmetics` precisa de chave estrangeira. A fonte continua
sendo o código.

## Consequências

- Rebalancear é um diff de números, revisável e sem tocar na lógica.
- O catálogo versiona junto com o código; não há tela de administração.
- Dois lugares guardam cosméticos (código e tabela). A sincronização é idempotente e roda
  em toda subida; remover uma chave do código não a remove do banco.
