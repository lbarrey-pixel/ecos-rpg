# 0001 — Estado de combate em JSONB, um por membro

## Contexto

Uma dungeon pode ser compartilhada: vários jogadores entram na mesma instância (terreno),
mas cada um enfrenta a própria sequência de salas, com o próprio inimigo, efeitos de status,
cooldowns e buffs. O estado de um turno tem cerca de trinta campos, vários aninhados
(`p_effects`, `e_effects`, `skill_cds`, o inimigo inteiro com habilidades) e muda a cada clique.

## Decisão

O estado vive em `dungeon_members.combat_state` (JSONB), uma linha por jogador e run.
O código o enxerga como o dataclass `EstadoCombate`, que sabe se serializar (`encode`) e ler
(`decode`) e que descarta chaves desconhecidas e converte nomes antigos. A instância
(`dungeons`) guarda só o que é realmente compartilhado: terreno, modo e status.

Um índice único parcial (`character_id WHERE member_status = 'active'`) garante uma run
ativa por personagem e deixa o mesmo personagem voltar à instância depois de sair.

## Consequências

- Ler e gravar o turno é uma linha, sem junções nem lock entre jogadores da mesma instância.
- Adicionar um campo ao estado não exige migração: o `decode` preenche o padrão.
- Não dá para consultar "quem está com veneno" com SQL puro e índice; se algum dia for
  preciso, o campo sai do JSON para uma coluna.
- O JSON não é validado pelo banco; a validação mora no `decode` e nos testes de ida e volta.
- Dois cliques simultâneos do mesmo jogador seriam duas leituras do mesmo estado. O bot
  serializa as ações por personagem com um lock em memória (suficiente para um processo
  de polling; com vários processos seria `SELECT ... FOR UPDATE` na linha do membro).
