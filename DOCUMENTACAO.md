# UnoAssist — Documentação

## Aplicação online

O projeto está publicado em uma VPS e pode ser acessado em:

**[https://unoassist.brassertech.com.br/](https://unoassist.brassertech.com.br/)**

## Início rápido

### 1. Configuração

Na raiz do projeto, copie o arquivo de ambiente:

```bash
cp .env.example .env
```

No Windows PowerShell, use `Copy-Item .env.example .env`. Depois, ajuste no `.env` as credenciais do PostgreSQL e o `JWT_SECRET`.

### 2. Banco e modelos

```bash
psql -U postgres -c "CREATE DATABASE \"CHATIA\";"
psql -U postgres -d CHATIA -f scripts/migration.sql
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

Se o banco já existir, execute apenas a migration.

### 3. Dependências

```bash
python -m venv .venv
```

Ative o ambiente virtual:

- Windows: `.\.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Depois, instale as dependências:

```bash
pip install -r requirements.txt
cd frontend
npm ci
cd ..
```

### 4. Executar

Com PostgreSQL e Ollama ativos:

```bash
python run.py
```

- Aplicação: `http://127.0.0.1:5173`
- API/Swagger: `http://127.0.0.1:8000/docs`

Na primeira utilização, selecione **Criar conta**. Para encerrar os serviços, pressione `Ctrl+C`.

## Fluxo de resposta

1. O aluno envia uma pergunta autenticada.
2. A aplicação considera o histórico da conversa e identifica a intenção.
3. A base institucional é consultada pelos modos de busca disponíveis.
4. O modelo responde somente com as fontes recuperadas.
5. Sem fonte confiável, o bot orienta o contato com o suporte.
6. Pergunta, resposta, status e tempo são registrados para o dashboard.

## Endpoints principais

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/cadastro` | Criar conta |
| POST | `/login` | Obter token JWT |
| POST | `/perguntar` | Enviar pergunta |
| GET/DELETE | `/conversas` | Consultar ou excluir histórico |
| GET/POST/DELETE | `/contexto/documentos` e `/contexto/upload` | Gerenciar a base documental |
| GET | `/estatisticas` | Consultar indicadores |
| GET/PUT | `/configuracoes` | Consultar ou alterar configurações |

A lista completa, schemas e exemplos ficam disponíveis no Swagger em `/docs` e na opção **Documentação** da interface.

## Problemas comuns

- **Interface desatualizada:** use `Ctrl+F5` para limpar o cache do PWA.
