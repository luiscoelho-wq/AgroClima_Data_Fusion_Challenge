# Arquitetura do AgroClima Inteligente

## 1. Visão geral

O AgroClima Inteligente é uma aplicação que consulta informações climáticas por meio da API Open-Meteo, armazena os dados em diferentes bancos de dados e disponibiliza as informações por meio de uma interface web.

## 2. Tecnologias utilizadas

- Python e Flask: desenvolvimento da API e integração dos dados.
- Open-Meteo: fornecimento dos dados meteorológicos.
- MongoDB: armazenamento das respostas originais da API.
- SQLite: armazenamento temporário dos dados climáticos por horário.
- Apache Hop: transformação e consolidação dos dados.
- MySQL: armazenamento dos dados climáticos consolidados.
- React: interface para consulta e visualização das informações.

## 3. Fluxo de integração

1. O usuário informa uma cidade pela interface React.
2. O frontend envia a solicitação para a API Flask.
3. O backend consulta a API externa Open-Meteo.
4. A resposta original é armazenada no MongoDB.
5. Os registros climáticos por horário são armazenados no SQLite.
6. O script Python exporta os dados do SQLite para um arquivo CSV.
7. O Apache Hop lê o CSV, seleciona os campos necessários e grava os dados consolidados no MySQL.
8. O frontend consulta a API Flask para apresentar o histórico, as condições atuais e os dados consolidados.

## 4. Responsabilidade dos bancos de dados

| Banco | Responsabilidade |
|---|---|
| MongoDB | Armazenar a resposta original da API externa. |
| SQLite | Armazenar temporariamente os registros climáticos por horário. |
| MySQL | Armazenar as informações das cidades, consultas e previsões consolidadas. |

## 5. Processo ETL

O processo ETL é realizado pelo Apache Hop por meio do pipeline `etl_clima.hpl`.

O pipeline possui três etapas:

- Entrada via arquivo CSV: recebe os dados exportados do SQLite.
- Selecione valores: organiza os campos que serão utilizados.
- Gravar clima no MySQL: insere os dados consolidados na tabela `clima_consolidado`.

Atualmente, a execução do processo é manual: primeiro é executado o script `exportar_staging.py` e depois o pipeline no Apache Hop.

## 6. Resultado

A aplicação permite consultar cidades, obter informações meteorológicas, armazenar os dados em diferentes bancos e visualizar as condições climáticas atuais, as previsões e o histórico consolidado em uma interface web.