# Estrutura do banco CHATIA

## usuarios

- `id` — identificador interno do usuário (chave primária).
- `codigo_aluno` — código acadêmico do aluno (único).
- `nome` — nome completo.
- `email` — e-mail do aluno (único, opcional).
- `login` — credencial de acesso (única).
- `senha_hash` — hash da senha; nunca armazena a senha em texto puro.
- `ativo` — indica se o acesso está habilitado.
- `created_at` — data de criação.
- `updated_at` — data da última atualização.

## conhecimento

- `id` — identificador do conteúdo (chave primária).
- `titulo` — título do conteúdo.
- `conteudo` — texto que embasa as respostas do assistente.
- `categoria` — classificação do conteúdo.
- `ativo` — indica se o conteúdo pode ser consultado.
- `search_document` — vetor de busca textual gerado a partir de título, categoria e conteúdo.
- `created_at` — data de criação.
- `updated_at` — data da última atualização.

## logs_perguntas

- `id` — identificador do registro (chave primária).
- `codigo_aluno` — aluno que fez a pergunta (chave estrangeira para `usuarios.codigo_aluno`).
- `pergunta` — mensagem enviada pelo aluno.
- `resposta` — resposta retornada pelo assistente; pode ser nula em erro ou ausência de conteúdo.
- `encontrada` — informa se houve conteúdo relevante na base de conhecimento.
- `status` — resultado do processamento: `respondida`, `sem_resposta` ou `erro`.
- `erro_detalhe` — detalhe técnico do erro, quando existir.
- `tempo_processamento_ms` — duração do processamento em milissegundos.
- `created_at` — data e hora da pergunta.

## Relacionamento

```text
usuarios
  codigo_aluno (único)
        │ 1
        │
        └──── N logs_perguntas.codigo_aluno
```

Um aluno pode possuir muitas perguntas registradas. Cada pergunta pertence a um único aluno.

`conhecimento` é independente: seus registros são pesquisados para fundamentar as respostas, mas não pertencem a um aluno específico.

## Índices principais

- `conhecimento.search_document`: busca full-text em português.
- `conhecimento.titulo`: busca aproximada por título.
- `logs_perguntas.created_at`, `codigo_aluno + created_at` e `status + created_at`: indicadores diários e dashboard.
