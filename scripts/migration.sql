-- Schema e atualização incremental do banco CHATIA (PostgreSQL 14+).
-- Pode ser executado novamente: preserva os registros existentes.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Campos-padrão de todas as tabelas do projeto:
-- chave (identificador público), ativo, id e datahoraalt.
CREATE TABLE IF NOT EXISTS usuarios (
    chave UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id BIGSERIAL PRIMARY KEY,
    datahoraalt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    datahoracad TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    codigo_aluno VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS conhecimento (
    chave UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id BIGSERIAL PRIMARY KEY,
    datahoraalt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    search_document TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(categoria, '') || ' ' || coalesce(conteudo, ''))
    ) STORED
);

CREATE TABLE IF NOT EXISTS logs_perguntas (
    chave UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id BIGSERIAL PRIMARY KEY,
    datahoraalt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    codigo_aluno VARCHAR(50) NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT,
    encontrada BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'respondida',
    erro_detalhe TEXT,
    tempo_processamento_ms INTEGER NOT NULL CHECK (tempo_processamento_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_logs_perguntas_status CHECK (status IN ('respondida', 'sem_resposta', 'erro')),
    CONSTRAINT ck_logs_perguntas_resposta CHECK ((status = 'respondida' AND resposta IS NOT NULL) OR status IN ('sem_resposta', 'erro'))
);

CREATE TABLE IF NOT EXISTS logs_perguntas_conhecimento (
    chave UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id BIGSERIAL PRIMARY KEY,
    datahoraalt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_pergunta_id BIGINT NOT NULL,
    conhecimento_id BIGINT NOT NULL,
    relevancia NUMERIC(5,4),
    CONSTRAINT uq_logs_perguntas_conhecimento UNIQUE (log_pergunta_id, conhecimento_id),
    CONSTRAINT fk_logs_perguntas_conhecimento_log FOREIGN KEY (log_pergunta_id) REFERENCES logs_perguntas (id) ON DELETE CASCADE,
    CONSTRAINT fk_logs_perguntas_conhecimento_conhecimento FOREIGN KEY (conhecimento_id) REFERENCES conhecimento (id) ON DELETE RESTRICT,
    CONSTRAINT ck_logs_perguntas_conhecimento_relevancia CHECK (relevancia IS NULL OR relevancia BETWEEN 0 AND 1)
);

-- Atualiza bancos criados com a versão inicial da migração.
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS chave UUID;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS datahoraalt TIMESTAMPTZ;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS datahoracad TIMESTAMPTZ;
UPDATE usuarios SET chave = gen_random_uuid() WHERE chave IS NULL;
UPDATE usuarios SET datahoraalt = COALESCE(datahoraalt, CURRENT_TIMESTAMP) WHERE datahoraalt IS NULL;
UPDATE usuarios SET datahoracad = COALESCE(datahoracad, CURRENT_TIMESTAMP) WHERE datahoracad IS NULL;
ALTER TABLE usuarios ALTER COLUMN chave SET DEFAULT gen_random_uuid();
ALTER TABLE usuarios ALTER COLUMN chave SET NOT NULL;
ALTER TABLE usuarios ALTER COLUMN datahoraalt SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE usuarios ALTER COLUMN datahoraalt SET NOT NULL;
ALTER TABLE usuarios ALTER COLUMN datahoracad SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE usuarios ALTER COLUMN datahoracad SET NOT NULL;

ALTER TABLE conhecimento ADD COLUMN IF NOT EXISTS chave UUID;
ALTER TABLE conhecimento ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE conhecimento ADD COLUMN IF NOT EXISTS datahoraalt TIMESTAMPTZ;
UPDATE conhecimento SET chave = gen_random_uuid() WHERE chave IS NULL;
UPDATE conhecimento SET datahoraalt = COALESCE(datahoraalt, CURRENT_TIMESTAMP) WHERE datahoraalt IS NULL;
ALTER TABLE conhecimento ALTER COLUMN chave SET DEFAULT gen_random_uuid();
ALTER TABLE conhecimento ALTER COLUMN chave SET NOT NULL;
ALTER TABLE conhecimento ALTER COLUMN datahoraalt SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE conhecimento ALTER COLUMN datahoraalt SET NOT NULL;

ALTER TABLE logs_perguntas ADD COLUMN IF NOT EXISTS chave UUID;
ALTER TABLE logs_perguntas ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE logs_perguntas ADD COLUMN IF NOT EXISTS datahoraalt TIMESTAMPTZ;
UPDATE logs_perguntas SET chave = gen_random_uuid() WHERE chave IS NULL;
UPDATE logs_perguntas SET datahoraalt = COALESCE(datahoraalt, CURRENT_TIMESTAMP) WHERE datahoraalt IS NULL;
ALTER TABLE logs_perguntas ALTER COLUMN chave SET DEFAULT gen_random_uuid();
ALTER TABLE logs_perguntas ALTER COLUMN chave SET NOT NULL;
ALTER TABLE logs_perguntas ALTER COLUMN datahoraalt SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE logs_perguntas ALTER COLUMN datahoraalt SET NOT NULL;

ALTER TABLE logs_perguntas_conhecimento ADD COLUMN IF NOT EXISTS chave UUID;
ALTER TABLE logs_perguntas_conhecimento ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE logs_perguntas_conhecimento ADD COLUMN IF NOT EXISTS id BIGSERIAL;
ALTER TABLE logs_perguntas_conhecimento ADD COLUMN IF NOT EXISTS datahoraalt TIMESTAMPTZ;
UPDATE logs_perguntas_conhecimento SET chave = gen_random_uuid() WHERE chave IS NULL;
UPDATE logs_perguntas_conhecimento SET datahoraalt = COALESCE(datahoraalt, CURRENT_TIMESTAMP) WHERE datahoraalt IS NULL;
ALTER TABLE logs_perguntas_conhecimento ALTER COLUMN chave SET DEFAULT gen_random_uuid();
ALTER TABLE logs_perguntas_conhecimento ALTER COLUMN chave SET NOT NULL;
ALTER TABLE logs_perguntas_conhecimento ALTER COLUMN datahoraalt SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE logs_perguntas_conhecimento ALTER COLUMN datahoraalt SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_usuarios_chave') THEN ALTER TABLE usuarios ADD CONSTRAINT uq_usuarios_chave UNIQUE (chave); END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_conhecimento_chave') THEN ALTER TABLE conhecimento ADD CONSTRAINT uq_conhecimento_chave UNIQUE (chave); END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_logs_perguntas_chave') THEN ALTER TABLE logs_perguntas ADD CONSTRAINT uq_logs_perguntas_chave UNIQUE (chave); END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_logs_perguntas_conhecimento_chave') THEN ALTER TABLE logs_perguntas_conhecimento ADD CONSTRAINT uq_logs_perguntas_conhecimento_chave UNIQUE (chave); END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_logs_perguntas_conhecimento_id') THEN ALTER TABLE logs_perguntas_conhecimento ADD CONSTRAINT uq_logs_perguntas_conhecimento_id UNIQUE (id); END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_logs_perguntas_usuario') THEN ALTER TABLE logs_perguntas ADD CONSTRAINT fk_logs_perguntas_usuario FOREIGN KEY (codigo_aluno) REFERENCES usuarios (codigo_aluno) ON UPDATE CASCADE ON DELETE RESTRICT; END IF;
END $$;

CREATE OR REPLACE FUNCTION atualizar_datahoraalt() RETURNS TRIGGER AS $$
BEGIN
    NEW.datahoraalt = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_usuarios_datahoraalt ON usuarios;
CREATE TRIGGER tr_usuarios_datahoraalt BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION atualizar_datahoraalt();
DROP TRIGGER IF EXISTS tr_conhecimento_datahoraalt ON conhecimento;
CREATE TRIGGER tr_conhecimento_datahoraalt BEFORE UPDATE ON conhecimento FOR EACH ROW EXECUTE FUNCTION atualizar_datahoraalt();
DROP TRIGGER IF EXISTS tr_logs_perguntas_datahoraalt ON logs_perguntas;
CREATE TRIGGER tr_logs_perguntas_datahoraalt BEFORE UPDATE ON logs_perguntas FOR EACH ROW EXECUTE FUNCTION atualizar_datahoraalt();
DROP TRIGGER IF EXISTS tr_logs_perguntas_conhecimento_datahoraalt ON logs_perguntas_conhecimento;
CREATE TRIGGER tr_logs_perguntas_conhecimento_datahoraalt BEFORE UPDATE ON logs_perguntas_conhecimento FOR EACH ROW EXECUTE FUNCTION atualizar_datahoraalt();

CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios (login);
CREATE INDEX IF NOT EXISTS idx_usuarios_codigo_aluno ON usuarios (codigo_aluno);
CREATE INDEX IF NOT EXISTS idx_conhecimento_categoria ON conhecimento (categoria);
CREATE INDEX IF NOT EXISTS idx_conhecimento_titulo_trgm ON conhecimento USING GIN (titulo gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_conhecimento_search_document ON conhecimento USING GIN (search_document);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_created_at ON logs_perguntas (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_codigo_aluno_created_at ON logs_perguntas (codigo_aluno, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_status_created_at ON logs_perguntas (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_conhecimento_conhecimento ON logs_perguntas_conhecimento (conhecimento_id);

COMMIT;
