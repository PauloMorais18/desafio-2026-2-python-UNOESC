-- Schema do banco CHATIA (PostgreSQL 14+)
-- Execute este arquivo conectado ao banco de dados "CHATIA".

BEGIN;

-- Suporte à busca textual da base de conhecimento (RF03).
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Usuários que acessam a API autenticada (RF07).
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    codigo_aluno VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Conteúdos previamente cadastrados que fundamentam as respostas (RF02).
CREATE TABLE IF NOT EXISTS conhecimento (
    id BIGSERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    search_document TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'portuguese',
            coalesce(titulo, '') || ' ' || coalesce(categoria, '') || ' ' || coalesce(conteudo, '')
        )
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Auditoria de cada pergunta e resposta, incluindo erros e perguntas sem conteúdo encontrado (RF05).
CREATE TABLE IF NOT EXISTS logs_perguntas (
    id BIGSERIAL PRIMARY KEY,
    codigo_aluno VARCHAR(50) NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT,
    encontrada BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'respondida',
    erro_detalhe TEXT,
    tempo_processamento_ms INTEGER NOT NULL CHECK (tempo_processamento_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_logs_perguntas_status
        CHECK (status IN ('respondida', 'sem_resposta', 'erro')),
    CONSTRAINT ck_logs_perguntas_resposta
        CHECK (
            (status = 'respondida' AND resposta IS NOT NULL)
            OR status IN ('sem_resposta', 'erro')
        )
);

-- Cada registro de conversa pertence a um aluno cadastrado.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_logs_perguntas_usuario'
    ) THEN
        ALTER TABLE logs_perguntas
            ADD CONSTRAINT fk_logs_perguntas_usuario
            FOREIGN KEY (codigo_aluno)
            REFERENCES usuarios (codigo_aluno)
            ON UPDATE CASCADE
            ON DELETE RESTRICT;
    END IF;
END $$;

-- Rastreia quais conteúdos fundamentaram cada resposta (RF02, RF03 e RF05).
CREATE TABLE IF NOT EXISTS logs_perguntas_conhecimento (
    log_pergunta_id BIGINT NOT NULL,
    conhecimento_id BIGINT NOT NULL,
    relevancia NUMERIC(5,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_pergunta_id, conhecimento_id),
    CONSTRAINT fk_logs_perguntas_conhecimento_log
        FOREIGN KEY (log_pergunta_id)
        REFERENCES logs_perguntas (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_logs_perguntas_conhecimento_conhecimento
        FOREIGN KEY (conhecimento_id)
        REFERENCES conhecimento (id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_logs_perguntas_conhecimento_relevancia
        CHECK (relevancia IS NULL OR relevancia BETWEEN 0 AND 1)
);

-- Índices para autenticação, busca e indicadores do dashboard (RF03 e RF06).
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios (login);
CREATE INDEX IF NOT EXISTS idx_usuarios_codigo_aluno ON usuarios (codigo_aluno);

CREATE INDEX IF NOT EXISTS idx_conhecimento_categoria ON conhecimento (categoria);
CREATE INDEX IF NOT EXISTS idx_conhecimento_titulo_trgm ON conhecimento USING GIN (titulo gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_conhecimento_search_document ON conhecimento USING GIN (search_document);

CREATE INDEX IF NOT EXISTS idx_logs_perguntas_created_at ON logs_perguntas (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_codigo_aluno_created_at
    ON logs_perguntas (codigo_aluno, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_status_created_at
    ON logs_perguntas (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_conhecimento_conhecimento
    ON logs_perguntas_conhecimento (conhecimento_id);

COMMIT;
