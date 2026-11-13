
import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv
import mysql.connector

pasta_projeto = Path(__file__).resolve().parent.parent
load_dotenv(Path(__file__).resolve().parent / ".env")

caminho_banco = pasta_projeto / "data" / "agroclima_staging.db"
caminho_csv = pasta_projeto / "data" / "staging_clima.csv"

conexao_sqlite = sqlite3.connect(caminho_banco)
cursor_sqlite = conexao_sqlite.cursor()

conexao_mysql = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    database=os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD")
)

cursor_mysql = conexao_mysql.cursor()

cursor_mysql.execute("""
    SELECT consulta_id, data_previsao
    FROM clima_consolidado
""")

registros_existentes = set()

for consulta_id, data_previsao in cursor_mysql.fetchall():
    if isinstance(data_previsao, (datetime, date)):
        data_previsao = data_previsao.strftime("%Y-%m-%d")

    registros_existentes.add((consulta_id, str(data_previsao)))

cursor_sqlite.execute("""
    SELECT
        consulta_id,
        substr(data_hora, 1, 10) AS data_previsao,
        MIN(temperatura_min),
        MAX(temperatura_max),
        MAX(probabilidade_chuva),
        SUM(precipitacao)
    FROM staging_clima
    GROUP BY consulta_id, substr(data_hora, 1, 10)
    ORDER BY consulta_id, data_previsao
""")

registros_sqlite = cursor_sqlite.fetchall()
registros = []

consultas_cache = {}

for registro in registros_sqlite:
    consulta_id, data_previsao, temp_min, temp_max, prob_chuva, precipitacao = registro

    if (consulta_id, str(data_previsao)) in registros_existentes:
        continue

    if consulta_id not in consultas_cache:
        cursor_mysql.execute("""
            SELECT
                c.cidade_id,
                ci.nome,
                c.data_consulta
            FROM consultas c
            INNER JOIN cidades ci ON ci.id = c.cidade_id
            WHERE c.id = %s
        """, (consulta_id,))

        consultas_cache[consulta_id] = cursor_mysql.fetchone()

    cidade = consultas_cache[consulta_id]

    if cidade is None:
        continue

    cidade_id, cidade_nome, data_consulta = cidade

    if isinstance(data_consulta, datetime):
        data_consulta = data_consulta.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(data_consulta, str):
        data_consulta = data_consulta[:19]

    atualizado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    registros.append([
        consulta_id,
        data_previsao,
        cidade_id,
        cidade_nome,
        data_consulta,
        temp_min,
        temp_max,
        prob_chuva,
        precipitacao if precipitacao is not None else 0,
        atualizado_em
    ])

colunas = [
    "consulta_id",
    "data_previsao",
    "cidade_id",
    "cidade_nome",
    "data_consulta",
    "temp_min",
    "temp_max",
    "prob_chuva_max",
    "precipitacao_mm",
    "atualizado_em"
]

with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.writer(arquivo, delimiter=";")
    escritor.writerow(colunas)
    escritor.writerows(registros)

cursor_sqlite.close()
conexao_sqlite.close()
cursor_mysql.close()
conexao_mysql.close()

print(f"Arquivo CSV gerado: {caminho_csv}")
print(f"Total de registros novos exportados: {len(registros)}")
