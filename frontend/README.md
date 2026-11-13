# Frontend

Interface web do AgroClima Inteligente, desenvolvida com React, Vite, JavaScript e CSS.

A aplicação permite consultar informações meteorológicas de cidades, visualizar as condições climáticas atuais, acompanhar previsões e consultar o histórico de pesquisas.

## Tecnologias utilizadas

- React: construção da interface.
- Vite: ambiente de desenvolvimento e execução.
- JavaScript: lógica da aplicação e comunicação com a API.
- CSS: estilização das páginas e componentes.

## Configuração inicial

Na pasta `frontend`, instale as dependências:

```powershell
npm install
```

Inicie o servidor de desenvolvimento:

```powershell
npm run dev
```

A interface estará disponível em:

`http://localhost:5173`

## Integração com o backend

O frontend realiza requisições para a API Flask, executada em:

`http://localhost:5000`

As principais operações são:

- Consultar uma cidade e obter informações meteorológicas.
- Carregar o histórico de consultas.
- Consultar as previsões consolidadas armazenadas no MySQL.

## Estrutura principal

- `src/App.jsx`: componente principal da aplicação.
- `src/App.css`: estilos da interface.
- `src/index.css`: estilos globais.
- `src/main.jsx`: ponto de entrada do React.
- `public/`: arquivos públicos utilizados pela aplicação.