# Guia de desenvolvimento

## Visão geral

O Assistente Acadêmico é uma base inicial para uma API preparada para autenticação,
busca de conhecimento e respostas assistidas por LLM local. Esta etapa não contém
regras de negócio: os endpoints retornam dados mockados.

## Arquitetura

O projeto adota uma organização inspirada em Clean Architecture:

- `api/`: entrega HTTP e dependências do FastAPI.
- `core/`: configuração, banco, segurança, logs e exceções.
- `ai/`: futura integração com LLM local, RAG e prompts.
- `schemas/`: contratos Pydantic de entrada e saída.
- `models/`: representações ORM das tabelas.
- `repositories/`: futura camada de acesso a dados.
- `services/`: futuros casos de uso.
- `utils/`: utilitários pequenos e reutilizáveis.

## Estrutura complementar

- `contexto/`: fontes da futura base de conhecimento.
- `scripts/`: schema e dados fictícios do PostgreSQL.
- `dashboard/` e `chat/`: interfaces Streamlit iniciais.
- `docker/`: imagem da API e orquestração local.
- `tests/`: local para a futura suíte de testes.

## Tecnologias

Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL, Pydantic, JWT, LangChain,
Docker, Docker Compose e Streamlit.

## Pré-requisitos e configuração

Instale Python 3.12, Docker (opcional) e PostgreSQL (opcional). Em seguida:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
```

Atualize as variáveis do arquivo `.env` para o ambiente desejado.

## Execução local

Com o ambiente virtual ativado, inicie a API Python e o frontend React com um único comando:

```bash
python run.py
```

O frontend abre em `http://127.0.0.1:5173` e a documentação da API fica em
`http://127.0.0.1:8000/docs`. Na primeira execução, o comando instala automaticamente
as dependências do React.

Para iniciar sem abrir o navegador automaticamente:

```bash
python run.py --no-browser
```

Elas ainda não consomem a API; essa integração está marcada como TODO.

## Banco de dados

Sem Alembic, o schema vive unicamente em `scripts/migration.sql`. Crie o banco
`chatia`, configure o `DATABASE_URL` no arquivo `.env` e execute a migração no
PostgreSQL configurado. Os conteúdos da base de conhecimento devem ser
cadastrados pela aplicação ou diretamente na tabela `conhecimento`.

## Docker

Crie `.env` a partir do exemplo e execute:

```bash
docker compose -f docker/docker-compose.yml up --build
```

O Compose sobe a API e o PostgreSQL; os scripts SQL são executados na
inicialização do volume do banco.

## Endpoints existentes

| Método | Rota | Estado |
| --- | --- | --- |
| GET | `/health` | mockado |
| POST | `/login` | mockado |
| POST | `/perguntar` | mockado |
| GET | `/estatisticas` | mockado |

## Roadmap

1. Implementar autenticação, hashing de senha e JWT.
2. Implementar repositórios, transações e regras de negócio.
3. Carregar documentos de `contexto/documentos/` com LangChain.
4. Criar embeddings e configurar armazenamento vetorial.
5. Integrar Ollama e o fluxo RAG para respostas locais.
6. Conectar os aplicativos Streamlit à API e adicionar testes.

A integração com LangChain, Ollama, RAG e embeddings possui pontos de extensão
documentados em `app/ai/`. Nenhuma dessas funcionalidades foi implementada nesta
estrutura inicial.
