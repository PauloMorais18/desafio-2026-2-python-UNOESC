# desafio-2026-2-python

CORRESPONDENTE AO EDITAL N. 21/UNOESC-R/2025

Desafio Programador I Unoesc

Este é o nosso desafio para a vaga de programador na Unoesc. Serão testadas as habilidades e qualidade de código ao transformar requisitos limitados em uma aplicação web.

**FAÇA O FORK DESTE REPOSITÓRIO E IMPLEMENTE O DESAFIO. O MANTENHA PÚBLICO, POIS QUEREMOS ACOMPANHAR SEUS COMMITS**

_Ao concluir o desafio, lembre de enviar um email para **recrutamentorh.jba@unoesc.edu.br, ti.coord@unoesc.edu.br e ti.dev@unoesc.edu.br**, com seu repositório. Lembre de incluir a documentação para que possamos rodar sua aplicação._

## PONTOS OBRIGATÓRIOS
* Python
* FastAPI
* REST
* Mysql/Postgres
* Git
* LangChain
* Documentação

## PONTOS DESEJÁVEIS
* Docker
* React
* LLM
* Ollama
* OpenAPI

## PONTOS DIFERENCIAIS
* Criar uma interface simples em Streamlit
* Emissão de relatórios de uso
* RAG e Embedding

## AVALIAÇÃO
O código será avaliado de acordo com os seguinte critérios:

* Documentação do processo necessário para rodar a aplicação;
* **Estrutura do projeto;**
* **Histórico do GIT;**
* Build e execução da aplicação;
* Completude das funcionalidades;
* Qualidade de código (design pattern, manutenibilidade, clareza);
* Boas práticas de UI;
* **Sentido e coerência nas respostas aos questionamentos na entrevista de apresentação do desafio realizada pelo candidato.**
 
**OBS: Plágios tendem a ser desclassificados. Atenção com o uso excessivo de IA.**

**IMPORTANTE: Estamos buscando desenvolvedores que topam desafios, então mesmo não cumprindo todo os requisitos abaixo, seu esforço será avaliado.**

## DESAFIO 

**Contexto**

Uma instituição de ensino deseja um assistente para responder dúvidas acadêmicas para os seus estudantes.
Para isso foi solicitado o desenvolvimento de uma API que comunique com o assistente, que por sua vez deverá basear suas respostas em conteúdos pré-definidos.
Cada mensagem recebida na API deverá consultar uma "base de conhecimento" alimentada previamente, sendo registros em tabela ou embeddings de documentos.
Em caso de questionamentos sobre assuntos que não sejam contemplados na "base de conhecimento", o assistente deve negar-se a responder.
Por questões de segurança e conformidade, todas as conversas devem ser registrada em tabelas de logs. Esses logs devem ser utilizados para que sejam criados paineis de acompanhamento.

**Requisitos Funcionais**

_RF01 – API Perguntar_ 

Endpoint /perguntar
Deve receber um body semelhante a:
{
   "codigoAluno":123
   "pergunta":"Como faço uma matrícula?"
}

_RF02 – Base de Conhecimento_

**Banco de dados - Utilizar uma tabela no banco contendo:**
* id
* titulo
* conteudo
* categoria

**Embedding - Realizar o armazenamento de documentos para servir como base de conhecimento (OPCIONAL)**

_RF03 – Busca_

Antes da IA responder, localizar os registros ou documentos (se usando embedding) mais relevantes.
A busca pode se balizar por LIKE, Full Text ou Embeddings (opcional).

_RF04 – Geração da resposta_

Utilizar LLMs. Caso possua chave de alguma API, pode utilizar, senão podes fazer uso de algum modelo disponível para Ollama local (especificar no projeto).

_RF05 – Histórico_

Para cada mensagem recebida e respondida, registrar:

* codigoAluno
* pergunta
* resposta
* data
* tempoProcessamento

_RF06 – API Estatísticas_

Endpoint /estatisticas que possibilite retornar:

* Perguntas realizadas no dia
* Perguntas por "codigoAluno"
* Perguntas sem resposta/erro no dia
* Tempo médio de resposta de todas as repostas armazenadas

_RF07 - Segurança_

Todos os endpoints existentes devem exigir a passagem de um Token JWT para seu funcionamento, o formato fica a sua escolha.

_RF08 – Dashboard_

Montar dashboard onde seja possível visualizar e analisar os dados do RF06.

_RF09 – Chat_

Montar tela para enviar mensagem e receber a resposta de acordo com a API do RF01.

**IMPORTANTE: Lembrando que a não completude de todos os pontos, não necessariamente é fator reprovatório, seu esforço será avaliado.**
