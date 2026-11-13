# Backend

API desenvolvida em Python com Flask, responsável por consultar informações meteorológicas, integrar os bancos de dados e disponibilizar os dados para o frontend.

## Configuração inicial

Na pasta `backend`, execute:

1. Crie o ambiente virtual:

```powershell
python -m venv .venv
```

2. Ative o ambiente virtual:

```powershell
.venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
pip install -r requirements.txt
```

4. Copie o arquivo `.env.example` para `.env` e preencha as configurações de conexão com os bancos de dados.

5. Inicie a API:

```powershell
python app.py
```

## Teste

Acesse o endereço abaixo para verificar se a API está funcionando:

`http://localhost:5000/api/health`

## Arquivos principais

- `app.py`: inicialização da API, rotas e integração dos dados.
- `exportar_staging.py`: exportação e agrupamento dos dados climáticos do SQLite para CSV.
- `requirements.txt`: dependências utilizadas pelo backend.
- `.env.example`: modelo das configurações necessárias para execução.