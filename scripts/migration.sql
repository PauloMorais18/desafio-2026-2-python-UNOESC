
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conhecimento (
    id BIGSERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_perguntas (
    id BIGSERIAL PRIMARY KEY,
    codigo_aluno VARCHAR(50) NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    encontrada BOOLEAN NOT NULL DEFAULT FALSE,
    tempo_processamento_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios (login);

CREATE INDEX IF NOT EXISTS idx_conhecimento_categoria ON conhecimento (categoria);
CREATE INDEX IF NOT EXISTS idx_conhecimento_titulo ON conhecimento (titulo);

CREATE INDEX IF NOT EXISTS idx_logs_perguntas_codigo_aluno ON logs_perguntas (codigo_aluno);
CREATE INDEX IF NOT EXISTS idx_logs_perguntas_created_at ON logs_perguntas (created_at);

