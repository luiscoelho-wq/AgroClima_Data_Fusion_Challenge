# AgroClima Inteligente

Sistema web de consulta e integração de dados meteorológicos. O projeto utiliza uma API externa para obter informações climáticas, armazena os dados em diferentes bancos e realiza a integração por meio do Apache Hop.

## Objetivo

Consultar informações meteorológicas de cidades, armazenar os dados obtidos e disponibilizar previsões climáticas em uma interface web.

## Tecnologias utilizadas

- **Front-end:** React, Vite, JavaScript e CSS.
- **Back-end:** Python e Flask.
- **API externa:** Open-Meteo.
- **Bancos de dados:** MySQL, MongoDB e SQLite.
- **Integração:** Apache Hop e CSV.

## Funcionamento do sistema

1. O usuário informa uma cidade na interface React.
2. O Flask consulta a API Open-Meteo e recebe os dados meteorológicos.
3. A resposta original é armazenada no MongoDB.
4. Os dados da cidade e da consulta são registrados no MySQL.
5. Os registros climáticos por horário são armazenados no SQLite.
6. Um script Python agrupa os dados por dia e gera um arquivo CSV.
7. O Apache Hop realiza a transformação e carrega os dados consolidados no MySQL.
8. O React apresenta as informações ao usuário por meio da API Flask.

## Responsabilidade dos bancos de dados

| Banco | Utilização |
|---|---|
| MongoDB | Armazenamento das respostas originais da API. |
| SQLite | Armazenamento temporário dos dados climáticos horários. |
| MySQL | Armazenamento de cidades, consultas e previsões consolidadas. |

## Estrutura do projeto

```text
agroclima-inteligente/
├── backend/
│   ├── app.py
│   ├── exportar_staging.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── data/
│   ├── .gitkeep
│   └── staging_clima.csv
├── etl/
│   ├── .gitkeep
│   └── etl_clima.hpl
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── index.html
├── docs/
│   └── arquitetura.md
├── .gitignore
└── README.md
```

## Como executar

### 1. Back-end

Na pasta `backend`, crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Configure o arquivo `.env` com as conexões dos bancos de dados, utilizando o `.env.example` como referência.

Certifique-se de que os serviços MySQL e MongoDB estejam disponíveis.

Inicie a API:

```powershell
python app.py
```

API disponível em:

`http://localhost:5000`

### 2. Front-end

Na pasta `frontend`, instale as dependências:

```powershell
npm install
```

Inicie a aplicação:

```powershell
npm run dev
```

Interface disponível em:

`http://localhost:5173`

### 3. Integração com Apache Hop

Após realizar as consultas, acesse a pasta `backend` e execute:

```powershell
python exportar_staging.py
```

O script gera o arquivo `data/staging_clima.csv`, agrupando os registros por dia e evitando exportar dados que já foram carregados no MySQL.

Em seguida, abra o pipeline `etl_clima.hpl`, disponível na pasta `etl`, no Apache Hop e execute-o.

O pipeline possui três etapas:

1. **Entrada via arquivo CSV:** recebe os dados exportados do SQLite.
2. **Selecione valores:** organiza os campos que serão utilizados.
3. **Gravar clima no mysql:** insere os dados consolidados na tabela `clima_consolidado`.

A execução do pipeline é manual e deve ser repetida quando houver novos dados para consolidar.

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/health` | Verifica o funcionamento da API. |
| POST | `/api/consultas` | Consulta uma cidade e armazena os dados. |
| GET | `/api/historico` | Consulta o histórico de cidades. |
| GET | `/api/clima/{consulta_id}` | Retorna as previsões consolidadas. |

Exemplo de corpo para uma nova consulta:

```json
{
  "cidade": "Andradas"
}
```

## Funcionalidades

- Consulta meteorológica por cidade.
- Exibição de temperatura, umidade e precipitação atuais.
- Visualização de previsões diárias.
- Histórico de consultas.
- Armazenamento em três tecnologias diferentes.
- Integração e consolidação de dados com Apache Hop.

## Testes realizados

Foram realizadas consultas para São João da Boa Vista e Andradas.

Durante os testes, foram validados o recebimento dos dados da API, o armazenamento no MongoDB e SQLite, a exportação CSV, a execução do Apache Hop e a disponibilização dos resultados no React.

Foram inseridos seis registros diários no MySQL, sendo três para cada cidade, sem duplicidade.

## Considerações finais

O AgroClima Inteligente demonstra a integração de diferentes tecnologias no processo de coleta, armazenamento, transformação e disponibilização de dados meteorológicos, desde uma API externa até uma interface web.
