-- Fictional development data for the future knowledge retrieval workflow.
INSERT INTO conhecimento (titulo, conteudo, categoria)
VALUES
    ('Calendário acadêmico', 'Conteúdo fictício para a estrutura inicial do projeto.', 'calendario'),
    ('Biblioteca', 'Conteúdo fictício sobre serviços acadêmicos.', 'servicos'),
    ('Atendimento', 'Conteúdo fictício sobre canais de atendimento.', 'suporte')
ON CONFLICT DO NOTHING;

