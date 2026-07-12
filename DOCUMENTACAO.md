# Documentação de Implementação

Este arquivo registra o estado atual dos requisitos RF01 a RF04 do Assistente Acadêmico UNOIA.

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

Portanto, a comunicação entre Python, LangChain e o Ollama local foi validada. O próximo passo é integrar essa geração ao fluxo do endpoint `/perguntar`, usando os documentos recuperados no RF03 como contexto.
