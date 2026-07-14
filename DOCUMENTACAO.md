# Documentação de Implementação

Este arquivo registra o estado atual dos requisitos RF01 a RF04 do Assistente Acadêmico UnoAssist.

## RF01 — API Perguntar

O endpoint `POST /perguntar` foi criado para receber o JSON abaixo:

```json
{
  "codigoAluno": 123,
  "pergunta": "Como faço uma matrícula?"
}
```

Antes de processar a pergunta, a API valida o token JWT do aluno e confirma que o `codigoAluno` informado corresponde ao usuário autenticado. O login e o cadastro usam código de aluno e senha, com senhas armazenadas de forma segura por hash.

Cada pergunta é registrada no banco de dados e o JSON recebido também é exibido no terminal da API. No navegador, a requisição e sua resposta são registradas no console para facilitar a verificação durante o desenvolvimento.

Principais endpoints relacionados:

- `POST /cadastro`
- `POST /login`
- `GET /perfil`
- `POST /perguntar`

## RF02 — Base de Conhecimento

A tabela `conhecimento` está presente na migration e atende aos campos solicitados pelo requisito:

- `id`
- `titulo`
- `conteudo`
- `categoria`

Ela também possui os campos padrão do projeto, como chave UUID, indicador de ativo e data de alteração. A migration cria índices para apoiar as buscas.

Também foi implementado o gerenciamento de documentos de contexto em `contexto/documentos`. O usuário autenticado pode enviar, listar, visualizar e excluir documentos pelos endpoints:

- `POST /contexto/upload`
- `GET /contexto/documentos`
- `GET /contexto/documentos/{id}`
- `DELETE /contexto/documentos/{id}`

O upload agora extrai o texto de arquivos PDF, TXT, Markdown e DOCX, divide o
conteúdo em trechos sobrepostos e grava cada trecho na tabela `conhecimento`.
Os registros recebem `documento_origem` e `indice_trecho`, permitindo rastrear
a fonte usada pela IA. Ao excluir um documento, seus trechos são desativados e
deixam de participar das buscas, sem remover referências de logs anteriores.

Para indexar arquivos que já estavam em `contexto/documentos` antes dessa
funcionalidade, execute uma vez, com um token JWT:

```text
POST /contexto/reindexar
Authorization: Bearer <token>
```

Antes de usar a ingestão em um banco já existente, execute novamente
`scripts/migration.sql`; a migração é incremental e adiciona as colunas de
origem sem apagar os dados atuais. PDFs compostos somente por imagens precisam
passar por OCR antes do envio.

O nome original do arquivo é preservado no armazenamento, evitando confusão na listagem. A camada de embeddings permanece opcional e ainda não foi adicionada.

## RF03 — Busca

Antes de montar a resposta, a API consulta a base `conhecimento` e retorna os conteúdos mais relevantes. Há três modos disponíveis na interface de configurações:

- **LIKE**: modo padrão; procura termos no título e no conteúdo.
- **Full Text**: usa busca textual do PostgreSQL com `tsvector`, índice GIN e idioma português.
- **Embeddings**: por enquanto utiliza o mesmo mecanismo de Full Text como alternativa, pois uma base vetorial ainda não foi configurada.

O modo de busca selecionado é enviado na requisição de pergunta como `modoBusca`. Os resultados encontrados são associados ao log da pergunta na tabela `logs_perguntas_conhecimento`, mantendo a rastreabilidade das fontes usadas.

## RF04 — Geração da resposta com Ollama

Foi criado um teste isolado em `tests/test_ollama.py`, sem FastAPI, banco de dados ou Chains do LangChain. O teste utiliza `langchain-ollama` e `ChatOllama` para conectar ao Ollama local:

- URL: `http://localhost:11434`
- Modelo: `qwen2.5:3b`

O projeto utiliza o modelo **Qwen2.5:3B** executado localmente através do Ollama.

A escolha deste modelo foi motivada pelos seguintes fatores:

- execução local sem necessidade de APIs pagas;
- boa capacidade de compreensão do idioma português;
- baixo consumo de memória em comparação com modelos maiores;
- respostas rápidas para consultas acadêmicas;
- integração nativa com LangChain através da biblioteca `langchain-ollama`;
- atende ao requisito do desafio de utilização de um LLM local.

O comando executado foi:

```bash
python tests/test_ollama.py
```

Resultado obtido:

```text
=== TESTE OLLAMA ===

Modelo:
qwen2.5:3b

Resposta:
OK
```

Portanto, a comunicação entre Python, LangChain e o Ollama local foi validada.

A geração foi integrada ao fluxo do endpoint `/perguntar`. Após o RF03 recuperar os conteúdos mais relevantes, eles são enviados como contexto para o `ChatOllama`. O prompt instrui o modelo a responder apenas com base nesse contexto institucional e a não inventar informações.

O modelo e o endereço do Ollama são configuráveis no `.env`:

```env
OLLAMA_URL=http://localhost:11434
MODEL_NAME=qwen2.5:3b
```

Quando não houver conteúdo correspondente na base, o modelo ainda responde normalmente a conversas gerais, como saudações. Para dúvidas institucionais sem contexto suficiente, ele informa essa limitação sem inventar dados. Se o Ollama estiver indisponível ou retornar erro, a API devolve uma mensagem segura ao aluno e registra o detalhe técnico no log da pergunta.

## RF05 — Histórico de conversas

O histórico persistente foi implementado com duas tabelas relacionadas:

- `conversas`: identifica a conversa por `chave` UUID, associa-a ao aluno e armazena como título a primeira pergunta enviada.
- `historico`: registra cada mensagem da conversa com `chaveconversa`, `codigo_aluno`, conteúdo, data e tempo de processamento.

Em `historico`, o campo `tipo` identifica a origem da mensagem:

- `1`: pergunta enviada pelo aluno;
- `2`: resposta gerada pela IA.

As duas tabelas possuem os campos padrão `chave`, `ativo`, `id` e `datahoraalt`. A relação composta entre `chaveconversa` e `codigo_aluno` garante que uma mensagem só possa ser vinculada a uma conversa do mesmo aluno.

O endpoint `POST /perguntar` cria uma conversa na primeira mensagem e devolve `chaveConversa`. Nas próximas mensagens, essa chave é enviada novamente pelo frontend. Também estão disponíveis:

- `GET /conversas`: lista os chats do aluno autenticado;
- `GET /conversas/{chaveConversa}/historico`: retorna as mensagens de um chat autenticado.

### Validação do RF05

Foi executado um teste de integração com uma conta temporária no banco. O teste enviou uma pergunta ao endpoint `/perguntar`, consultou a conversa retornada e leu seu histórico pelos endpoints de conversa. O resultado confirmou:

- criação da conversa e retorno de `chaveConversa`;
- persistência da pergunta como `tipo = 1`;
- persistência da resposta da IA como `tipo = 2`;
- preenchimento de `tempoProcessamentoMs` na resposta;
- recuperação correta pelos endpoints de histórico.

Os registros e a conta usados no teste foram removidos ao final da validação.

## RF06 — Estatísticas

As estatísticas são calculadas a partir da tabela `logs_perguntas` e disponibilizadas por endpoints específicos:

- `GET /estatisticas/perguntas-do-dia`: perguntas realizadas no dia.
- `GET /estatisticas/perguntas-por-aluno`: perguntas agrupadas por `codigoAluno`.
- `GET /estatisticas/sem-resposta-ou-erro-do-dia`: quantidade diária com status `sem_resposta` ou `erro`.
- `GET /estatisticas/tempo-medio-resposta`: tempo médio de processamento de todas as respostas armazenadas.

Exemplos de retorno:

```json
{
  "data": "2026-07-12",
  "totalPerguntas": 9
}
```

```json
{
  "alunos": [
    { "codigoAluno": "400754", "totalPerguntas": 9 }
  ]
}
```

No menu hamburger, a tela **Estatísticas** apresenta indicadores do dia, tempo médio e um gráfico de barras de perguntas por aluno.

### Como testar o RF06 no Postman

Com a aplicação em execução (`python run.py`), configure o método **GET** no Postman e informe o header abaixo:

```text
Authorization: Bearer <seu_token_jwt>
```

| Indicador | URL para o Postman | Retorno principal |
|---|---|---|
| Perguntas realizadas no dia | `http://127.0.0.1:8000/estatisticas/perguntas-do-dia` | `data`, `totalPerguntas` |
| Perguntas por aluno | `http://127.0.0.1:8000/estatisticas/perguntas-por-aluno` | Lista `alunos` com `codigoAluno` e `totalPerguntas` |
| Sem resposta ou erro no dia | `http://127.0.0.1:8000/estatisticas/sem-resposta-ou-erro-do-dia` | `data`, `totalSemRespostaOuErro` |
| Tempo médio das respostas | `http://127.0.0.1:8000/estatisticas/tempo-medio-resposta` | `tempoMedioRespostaMs` |

Exemplos completos de retorno:

```json
// GET /estatisticas/perguntas-do-dia
{
  "data": "2026-07-12",
  "totalPerguntas": 9
}
```

```json
// GET /estatisticas/perguntas-por-aluno
{
  "alunos": [
    {
      "codigoAluno": "400754",
      "totalPerguntas": 9
    }
  ]
}
```

```json
// GET /estatisticas/sem-resposta-ou-erro-do-dia
{
  "data": "2026-07-12",
  "totalSemRespostaOuErro": 5
}
```

```json
// GET /estatisticas/tempo-medio-resposta
{
  "tempoMedioRespostaMs": 591.22
}
```

## Documentação da API na interface

A opção **Documentação** do menu hamburger consulta `/openapi.json` e mostra todos os endpoints expostos pela API, com método HTTP, caminho, descrição e categoria. A lista é dinâmica: novos endpoints registrados no FastAPI aparecerão automaticamente na página. A tela também disponibiliza acesso ao Swagger em `/docs` para testar requisições e visualizar os schemas completos.

## RF07 — Segurança JWT

Os endpoints funcionais exigem um token JWT no header HTTP:

```text
Authorization: Bearer <seu_token_jwt>
```

O token é retornado por `POST /login` ou `POST /cadastro` e identifica o `codigoAluno` autenticado. Sem token, com token inválido ou expirado, a API retorna `401 Unauthorized`.

As únicas exceções são `POST /login` e `POST /cadastro`, necessários para obter o primeiro token, além de `/docs` e `/openapi.json`, que permanecem públicos para consulta da documentação. O dashboard envia o token JWT automaticamente ao consultar as estatísticas.

## Dashboard RF06

O dashboard de estatísticas foi desenvolvido em React com a biblioteca Recharts e preserva a identidade visual do UnoAssist. Ele contém cabeçalho com período disponível, atualização manual, menu rápido e indicadores de total de perguntas, respondidas, sem resposta/erro e tempo médio.

Os componentes reutilizáveis criados são:

- `DashboardHeader`: cabeçalho, período e ações do dashboard;
- `StatisticCard`: cartão de indicador com ícone, valor e descrição;
- `ChartCard`: contêiner padronizado para gráficos e estados vazios;
- `StatisticsDashboard`: composição das linhas, atalhos e gráficos do RF06.

Os gráficos com dados fornecidos pelos endpoints atuais mostram perguntas do dia, perguntas por aluno e taxa de sucesso. Os gráficos de categoria, frequência de perguntas, horários, tempo por categoria e evolução semanal exibem um estado vazio explicativo enquanto a API não fornecer essas métricas. Assim, o dashboard não apresenta dados fictícios.
