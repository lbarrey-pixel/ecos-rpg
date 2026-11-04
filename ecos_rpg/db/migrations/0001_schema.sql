-- Schema inicial. Cada coluna aqui é lida ou escrita por algum módulo de ecos_rpg/db.

CREATE TABLE players (
    id          BIGINT PRIMARY KEY,           -- id do usuário no Telegram
    username    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE characters (
    id               SERIAL PRIMARY KEY,
    player_id        BIGINT NOT NULL UNIQUE REFERENCES players (id) ON DELETE CASCADE,
    name             TEXT NOT NULL,
    class            TEXT NOT NULL
                     CHECK (class IN ('paladino', 'arqueiro', 'guerreiro', 'bruxo', 'curandeiro')),

    level            INTEGER NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 99),
    -- BIGINT: a curva de XP passa de 2^31 perto do nível 90
    experience       BIGINT  NOT NULL DEFAULT 0,
    experience_next  BIGINT  NOT NULL DEFAULT 100,
    status_points    INTEGER NOT NULL DEFAULT 0 CHECK (status_points >= 0),
    gold             INTEGER NOT NULL DEFAULT 100 CHECK (gold >= 0),
    crystals         INTEGER NOT NULL DEFAULT 0 CHECK (crystals >= 0),

    hp_max           INTEGER NOT NULL,
    hp_current       INTEGER NOT NULL,
    mana_max         INTEGER NOT NULL,
    mana_current     INTEGER NOT NULL,
    attack           INTEGER NOT NULL,
    defense          INTEGER NOT NULL,
    spirituality     INTEGER NOT NULL,
    luck             INTEGER NOT NULL,
    carry_capacity   INTEGER NOT NULL,
    safe_slots       INTEGER NOT NULL,

    -- pontos alocados por stat (ver engine.progressao.STAT_EFFECT)
    sp_vitalidade      INTEGER NOT NULL DEFAULT 0 CHECK (sp_vitalidade >= 0),
    sp_espirito        INTEGER NOT NULL DEFAULT 0 CHECK (sp_espirito >= 0),
    sp_forca           INTEGER NOT NULL DEFAULT 0 CHECK (sp_forca >= 0),
    sp_resistencia     INTEGER NOT NULL DEFAULT 0 CHECK (sp_resistencia >= 0),
    sp_sorte           INTEGER NOT NULL DEFAULT 0 CHECK (sp_sorte >= 0),
    sp_espiritualidade INTEGER NOT NULL DEFAULT 0 CHECK (sp_espiritualidade >= 0),

    blood_on_hands   INTEGER NOT NULL DEFAULT 0,
    active_blessing  TEXT CHECK (active_blessing IN ('retorno', 'martir', 'sobrevivente')),

    vip_expires_at   TIMESTAMPTZ,
    is_founder       BOOLEAN NOT NULL DEFAULT FALSE,
    cosmetic_title     TEXT,
    cosmetic_aura      TEXT,
    cosmetic_frame     TEXT,
    cosmetic_insignia  TEXT,
    war_cry          TEXT,
    epitaph          TEXT,

    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- location: onde o item está. 'mochila' e 'bolso_seguro' valem só durante a run.
CREATE TABLE inventory (
    id                  SERIAL PRIMARY KEY,
    character_id        INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    item_name           TEXT NOT NULL,
    item_type           TEXT NOT NULL
                        CHECK (item_type IN ('material', 'weapon', 'armor', 'accessory',
                                             'consumable', 'artifact')),
    element             TEXT,
    rarity              TEXT NOT NULL DEFAULT 'common'
                        CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')),
    quantity            INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    location            TEXT NOT NULL DEFAULT 'bau'
                        CHECK (location IN ('bau', 'mochila', 'bolso_seguro', 'equipado')),
    equip_slot          TEXT CHECK (equip_slot IN ('weapon', 'armor', 'accessory', 'ammunition')),
    durability_current  INTEGER,
    durability_max      INTEGER,
    is_bound            BOOLEAN NOT NULL DEFAULT FALSE,   -- vínculo: nunca se perde na morte
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_inventory_character ON inventory (character_id, location);
-- um item equipado por slot e personagem
CREATE UNIQUE INDEX uq_inventory_equipado
    ON inventory (character_id, equip_slot) WHERE location = 'equipado';

CREATE TABLE dungeons (
    id          SERIAL PRIMARY KEY,
    terrain     TEXT NOT NULL CHECK (terrain IN ('lava', 'glacial', 'chemical', 'giants')),
    mode        TEXT NOT NULL CHECK (mode IN ('solo', 'party')),
    status      TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'finished')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_dungeons_abertas ON dungeons (mode, created_at DESC) WHERE status = 'active';

CREATE TABLE parties (
    id          SERIAL PRIMARY KEY,
    leader_id   INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    status      TEXT NOT NULL DEFAULT 'forming'
                CHECK (status IN ('forming', 'in_dungeon', 'disbanded')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE party_members (
    id            SERIAL PRIMARY KEY,
    party_id      INTEGER NOT NULL REFERENCES parties (id) ON DELETE CASCADE,
    character_id  INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    joined_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (party_id, character_id)
);

-- Um estado de combate por jogador, mesmo em instância compartilhada (ver ADR 0001).
CREATE TABLE dungeon_members (
    id             SERIAL PRIMARY KEY,
    dungeon_id     INTEGER NOT NULL REFERENCES dungeons (id) ON DELETE CASCADE,
    character_id   INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    party_id       INTEGER REFERENCES parties (id) ON DELETE SET NULL,
    hp_current     INTEGER NOT NULL,
    mana_current   INTEGER NOT NULL,
    member_status  TEXT NOT NULL DEFAULT 'active'
                   CHECK (member_status IN ('active', 'extracted', 'dead')),
    combat_state   JSONB NOT NULL DEFAULT '{}'::jsonb,
    joined_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_updated   TIMESTAMPTZ NOT NULL DEFAULT now(),
    exited_at      TIMESTAMPTZ
);
-- o mesmo personagem pode voltar à instância depois de sair, mas só uma run ativa por vez
CREATE UNIQUE INDEX uq_membro_ativo ON dungeon_members (character_id) WHERE member_status = 'active';
CREATE INDEX idx_dungeon_members_dungeon ON dungeon_members (dungeon_id, member_status);

CREATE TABLE crystal_transactions (
    id            BIGSERIAL PRIMARY KEY,
    character_id  INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    amount        INTEGER NOT NULL,          -- negativo = gasto
    reason        TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_crystal_tx_character ON crystal_transactions (character_id, created_at DESC);

-- Catálogo sincronizado a partir de engine/cosmeticos.py (db.economia.sincronizar_catalogo)
CREATE TABLE cosmetics_catalog (
    key            TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    type           TEXT NOT NULL CHECK (type IN ('title', 'aura', 'frame', 'insignia')),
    cost_crystals  INTEGER CHECK (cost_crystals > 0),   -- NULL = não está à venda
    is_vip_pool    BOOLEAN NOT NULL DEFAULT FALSE,
    is_founder     BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE character_cosmetics (
    character_id  INTEGER NOT NULL REFERENCES characters (id) ON DELETE CASCADE,
    cosmetic_key  TEXT NOT NULL REFERENCES cosmetics_catalog (key),
    acquired_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (character_id, cosmetic_key)
);
