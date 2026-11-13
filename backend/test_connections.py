import os
import sqlite3
from pathlib import Path

import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

print("\n=== TESTE DE CONEXÕES AGROCLIMA ===\n")

# MYSQL
try:
    conexao_mysql = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    print("MySQL: conexão realizada com sucesso!")

    conexao_mysql.close()

except Exception as erro:
    print(f"MySQL: erro na conexão: {erro}")

# MONGODB
try:
    cliente_mongo = MongoClient(
        os.getenv("MONGODB_URI"),
        serverSelectionTimeoutMS=5000
    )

    cliente_mongo.admin.command("ping")

    print("MongoDB: conexão realizada com sucesso!")

    cliente_mongo.close()

except Exception as erro:
    print(f"MongoDB: erro na conexão: {erro}")

# SQLITE
try:
    caminho = Path(os.getenv("SQLITE_PATH"))
    caminho = caminho.resolve()

    caminho.parent.mkdir(parents=True, exist_ok=True)

    conexao_sqlite = sqlite3.connect(caminho)

    conexao_sqlite.execute("""
        CREATE TABLE IF NOT EXISTS staging_clima (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consulta_id INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            temperatura REAL,
            temperatura_min REAL,
            temperatura_max REAL,
            probabilidade_chuva REAL,
            precipitacao REAL,
            umidade REAL
        )
    """)

    conexao_sqlite.commit()
    conexao_sqlite.close()

    print("SQLite: conexão realizada com sucesso!")
    print(f"Arquivo criado em: {caminho}")

except Exception as erro:
    print(f"SQLite: erro na conexão: {erro}")

print("\n=== FIM DOS TESTES ===")