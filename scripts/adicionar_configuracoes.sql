-- Adiciona as configurações dinâmicas do UnoAssist em um banco já existente.
-- O script é idempotente e preserva valores que já tenham sido personalizados.

BEGIN;

CREATE TABLE IF NOT EXISTS configuracoes (
    id BIGSERIAL PRIMARY KEY,
    chave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    datahoraalt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO configuracoes (chave, valor, descricao) VALUES
    ('telefone_suporte_whatsapp', '554935512034', 'Número do suporte com código do país e DDD'),
    ('mensagem_fora_escopo', 'Não encontrei informações sobre esse assunto na base de conhecimento institucional. Entre em contato com o suporte pelo WhatsApp: {telefone}', 'Mensagem usada quando não existe fonte confiável'),
    ('similaridade_minima_embeddings', '0.65', 'Similaridade mínima aceita entre 0 e 1'),
    ('limite_fontes', '3', 'Quantidade máxima de fontes enviadas ao modelo')
ON CONFLICT (chave) DO NOTHING;

CREATE OR REPLACE FUNCTION atualizar_datahoraalt() RETURNS TRIGGER AS $$
BEGIN
    NEW.datahoraalt = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_configuracoes_datahoraalt ON configuracoes;
CREATE TRIGGER tr_configuracoes_datahoraalt
BEFORE UPDATE ON configuracoes
FOR EACH ROW EXECUTE FUNCTION atualizar_datahoraalt();

CREATE INDEX IF NOT EXISTS idx_configuracoes_chave ON configuracoes (chave);

COMMIT;
