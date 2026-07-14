# Visão técnica do projeto

## Sobre o UnoAssist

O UnoAssist é um assistente acadêmico criado para responder dúvidas de alunos
usando informações fornecidas pela própria instituição. A ideia principal é que
a IA não responda somente com o conhecimento geral do modelo: antes de gerar
uma resposta, o sistema pesquisa a base de conhecimento e envia o conteúdo
encontrado como contexto para o Ollama.

O projeto possui uma API em Python, uma interface web em React, banco de dados
PostgreSQL e integração com um modelo de linguagem executado localmente.

## Tecnologias utilizadas

- Python e FastAPI na API.
- React e Vite na interface web.
- PostgreSQL para usuários, conhecimento, conversas e logs.
- SQLAlchemy para comunicação entre a aplicação e o banco.
- Pydantic para validar os dados recebidos e retornados pela API.
- JWT para autenticação dos alunos.
- LangChain e Ollama para geração das respostas.
- Docker para facilitar a execução da API e do PostgreSQL.
- Streamlit nos protótipos iniciais de chat e dashboard.

## Organização do projeto

O código principal do backend está dentro da pasta `app/` e foi separado por
responsabilidade:

- `app/api/`: rotas da API, como login, perguntas, histórico, documentos e
  estatísticas.
- `app/core/`: configurações gerais, conexão com o banco, segurança JWT e logs.
- `app/models/`: representação das tabelas do PostgreSQL no SQLAlchemy.
- `app/schemas/`: formatos de entrada e saída da API.
- `app/repositories/`: consultas e operações de acesso aos dados.
- `app/services/`: regras do sistema, como responder perguntas, autenticar
  usuários e processar documentos.
- `app/ai/`: arquivos relacionados à integração com a IA e aos prompts.
- `app/utils/`: funções auxiliares usadas em diferentes partes do projeto.

As outras pastas complementam a aplicação:

- `frontend/`: interface principal do UnoAssist desenvolvida em React.
- `contexto/documentos/`: arquivos usados como fonte de conhecimento.
- `scripts/`: estrutura do banco de dados PostgreSQL.
- `docker/`: arquivos usados para criar os containers da aplicação.
- `tests/`: testes dos componentes e integrações do projeto.
- `chat/` e `dashboard/`: protótipos criados em Streamlit durante o
  desenvolvimento da interface.

## Funcionamento da aplicação

### Autenticação

O aluno pode criar uma conta ou entrar usando seu código e senha. Depois do
login, a API retorna um token JWT. Esse token identifica o aluno e protege as
rotas que acessam perguntas, conversas, documentos e estatísticas.

As senhas não são armazenadas diretamente. O sistema salva apenas o hash
gerado com bcrypt.

### Perguntas e respostas

Quando uma pergunta é enviada para `/perguntar`, o sistema confere se o código
do aluno é o mesmo informado no token. Em seguida, pesquisa informações
relacionadas na tabela `conhecimento`.

Os trechos encontrados são enviados ao Ollama junto com a pergunta. O prompt
orienta o modelo a utilizar o contexto institucional e evitar informações que
não estejam disponíveis na base. A resposta, o tempo de processamento e as
fontes consultadas são registrados no banco.

### Documentos de contexto

A interface permite enviar arquivos PDF, TXT, MD e DOCX. No upload, o backend
extrai o texto, organiza o conteúdo em trechos menores e salva esses trechos na
tabela `conhecimento`.

Quando a API é iniciada, ela também verifica os documentos que já acompanham o
projeto. Se algum deles ainda não possuir trechos ativos na base, o conteúdo é
processado automaticamente. Essa verificação evita que o mesmo arquivo seja
inserido novamente a cada inicialização.

Essa divisão melhora a busca porque permite selecionar apenas as partes mais
relacionadas à pergunta. Cada trecho mantém o nome do documento de origem e sua
posição no arquivo. Quando um documento é excluído, seus trechos deixam de ser
usados nas próximas respostas, mas os registros antigos continuam preservados.

### Histórico e logs

As mensagens são agrupadas em conversas. Cada conversa pertence ao aluno que a
criou e possui um histórico com perguntas e respostas em ordem cronológica.

Além do histórico visível no chat, a tabela de logs registra o resultado do
processamento, o tempo da resposta, possíveis erros e os conteúdos da base de
conhecimento que foram utilizados. Esses dados também servem como fonte para o
dashboard.

### Estatísticas

A API calcula indicadores a partir dos logs armazenados, incluindo:

- quantidade de perguntas realizadas no dia;
- quantidade de perguntas por aluno;
- perguntas sem resposta ou com erro;
- tempo médio de processamento.

O dashboard em React consulta esses endpoints e apresenta os resultados em
cartões e gráficos.

## Banco de dados

O arquivo `scripts/migration.sql` concentra a estrutura do banco de dados. Nele
ficam as tabelas, relacionamentos, índices, validações e campos necessários para
o funcionamento do sistema.

As principais tabelas são:

- `usuarios`: contas e dados dos alunos;
- `conhecimento`: informações pesquisadas antes da resposta da IA;
- `conversas`: agrupamento dos chats de cada aluno;
- `historico`: mensagens enviadas e recebidas;
- `logs_perguntas`: auditoria das perguntas e respostas;
- `logs_perguntas_conhecimento`: ligação entre uma pergunta e as fontes usadas.

O projeto não utiliza Alembic. A definição e a evolução do banco foram mantidas
no arquivo de migration para deixar a estrutura centralizada e fácil de
consultar.

## Interface web

O frontend reúne o chat, autenticação, histórico, gerenciamento dos documentos,
dashboard e visualização da documentação da API. Ele se comunica com o FastAPI
por requisições HTTP e envia o token JWT nas operações protegidas.

O comando `python run.py` inicia a API e o frontend durante o desenvolvimento.
O script também organiza o encerramento dos dois processos quando a aplicação é
finalizada.

## Docker e configurações

A pasta `docker/` contém a imagem da API e o arquivo de composição dos serviços.
O Docker Compose descreve a comunicação entre o backend e o PostgreSQL, além do
volume usado para manter os dados do banco.

As configurações que mudam entre ambientes ficam no arquivo `.env`, como dados
de conexão, segredo do JWT, endereço do Ollama e nome do modelo utilizado. O
arquivo `.env.example` mostra as variáveis esperadas sem expor credenciais reais.

## Documentação da API

O FastAPI gera automaticamente o contrato OpenAPI do projeto. A tela de
documentação mostra as rotas disponíveis, e o Swagger permite visualizar os
schemas e testar as requisições da API.
