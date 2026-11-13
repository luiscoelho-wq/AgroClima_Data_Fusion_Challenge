
import os
import sqlite3
import requests
import mysql.connector

from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)
CORS(app)


def conectar_mysql():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


def conectar_mongo():
    cliente = MongoClient(
        os.getenv("MONGODB_URI"),
        serverSelectionTimeoutMS=5000
    )

    return cliente[os.getenv("MONGODB_DATABASE")]["respostas_api"]


def conectar_sqlite():
    caminho = Path(os.getenv("SQLITE_PATH"))

    if not caminho.is_absolute():
        caminho = Path(__file__).resolve().parent / caminho

    caminho.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(caminho)

    conexao.execute("""
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

    conexao.commit()

    return conexao


def buscar_cidade(nome):
    resposta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": nome,
            "count": 1,
            "language": "pt",
            "format": "json"
        },
        timeout=20
    )

    resposta.raise_for_status()

    dados = resposta.json()
    resultados = dados.get("results", [])

    if not resultados:
        return None

    cidade = resultados[0]

    return {
        "open_meteo_id": cidade["id"],
        "nome": cidade["name"],
        "estado": cidade.get("admin1"),
        "pais": cidade.get("country", ""),
        "latitude": cidade["latitude"],
        "longitude": cidade["longitude"]
    }


def consultar_clima(latitude, longitude):
    resposta = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation",
            "daily": "temperature_2m_max,temperature_2m_min",
            "forecast_days": 3,
            "timezone": "auto"
        },
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()


def salvar_mysql(cidade, mongo_id):
    conexao = conectar_mysql()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id FROM cidades
        WHERE open_meteo_id = %s
    """, (cidade["open_meteo_id"],))

    resultado = cursor.fetchone()

    if resultado:
        cidade_id = resultado[0]
    else:
        cursor.execute("""
            INSERT INTO cidades (
                open_meteo_id,
                nome,
                estado,
                pais,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            cidade["open_meteo_id"],
            cidade["nome"],
            cidade["estado"],
            cidade["pais"],
            cidade["latitude"],
            cidade["longitude"]
        ))

        cidade_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO consultas (cidade_id, mongo_id)
        VALUES (%s, %s)
    """, (cidade_id, mongo_id))

    consulta_id = cursor.lastrowid

    conexao.commit()
    cursor.close()
    conexao.close()

    return consulta_id


def preparar_sqlite(consulta_id, dados):
    conexao = conectar_sqlite()
    cursor = conexao.cursor()

    horario = dados["hourly"]
    diario = dados["daily"]

    temperaturas_minimas = {
        data: valor
        for data, valor in zip(
            diario["time"],
            diario["temperature_2m_min"]
        )
    }

    temperaturas_maximas = {
        data: valor
        for data, valor in zip(
            diario["time"],
            diario["temperature_2m_max"]
        )
    }

    registros = []

    for i, data_hora in enumerate(horario["time"]):
        data = data_hora[:10]

        registros.append((
            consulta_id,
            data_hora,
            horario["temperature_2m"][i],
            temperaturas_minimas.get(data),
            temperaturas_maximas.get(data),
            horario["precipitation_probability"][i],
            horario["precipitation"][i],
            horario["relative_humidity_2m"][i]
        ))

    cursor.executemany("""
        INSERT INTO staging_clima (
            consulta_id,
            data_hora,
            temperatura,
            temperatura_min,
            temperatura_max,
            probabilidade_chuva,
            precipitacao,
            umidade
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, registros)

    conexao.commit()
    cursor.close()
    conexao.close()

    return len(registros)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "mensagem": "API AgroClima Inteligente funcionando!"
    })


@app.post("/api/consultas")
def criar_consulta():
    try:
        dados = request.get_json(silent=True) or {}
        nome = dados.get("cidade", "").strip()

        if not nome:
            return jsonify({
                "erro": "Informe o nome de uma cidade."
            }), 400

        cidade = buscar_cidade(nome)

        if not cidade:
            return jsonify({
                "erro": "Cidade não encontrada."
            }), 404

        clima = consultar_clima(
            cidade["latitude"],
            cidade["longitude"]
        )

        documento = {
            "cidade": cidade,
            "data_armazenamento": datetime.now().isoformat(),
            "dados_climaticos": clima
        }

        colecao = conectar_mongo()
        resultado = colecao.insert_one(documento)

        mongo_id = str(resultado.inserted_id)

        consulta_id = salvar_mysql(cidade, mongo_id)

        quantidade = preparar_sqlite(consulta_id, clima)

        return jsonify({
            "mensagem": "Consulta realizada e dados armazenados com sucesso!",
            "cidade": cidade,
            "consulta_id": consulta_id,
            "mongo_id": mongo_id,
            "registros_sqlite": quantidade,
            "clima_atual": clima.get("current"),
            "previsao_diaria": clima.get("daily")
        }), 201

    except requests.RequestException as erro:
        return jsonify({
            "erro": "Não foi possível consultar a API meteorológica.",
            "detalhes": str(erro)
        }), 502

    except Exception as erro:
        return jsonify({
            "erro": "Erro ao processar a consulta.",
            "detalhes": str(erro)
        }), 500


@app.get("/api/historico")
def historico():
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                consultas.id,
                cidades.nome AS cidade,
                cidades.pais,
                consultas.data_consulta
            FROM consultas
            INNER JOIN cidades
                ON cidades.id = consultas.cidade_id
            ORDER BY consultas.data_consulta DESC
            LIMIT 20
        """)

        resultados = cursor.fetchall()

        for item in resultados:
            if item["data_consulta"]:
                item["data_consulta"] = item["data_consulta"].isoformat()

        cursor.close()
        conexao.close()

        return jsonify(resultados)

    except Exception as erro:
        return jsonify({
            "erro": "Não foi possível consultar o histórico.",
            "detalhes": str(erro)
        }), 500


@app.get("/api/clima/<int:consulta_id>")
def consultar_clima_consolidado(consulta_id):
    try:
        conexao = conectar_mysql()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                consulta_id,
                data_previsao,
                cidade_id,
                cidade_nome,
                data_consulta,
                temp_min,
                temp_max,
                amplitude_termica,
                prob_chuva_max,
                precipitacao_mm,
                classificacao_chuva,
                codigo_clima,
                descricao_clima,
                temp_atual,
                umidade_atual,
                precipitacao_atual,
                atualizado_em
            FROM clima_consolidado
            WHERE consulta_id = %s
            ORDER BY data_previsao
        """, (consulta_id,))

        resultados = cursor.fetchall()

        cursor.close()
        conexao.close()

        if not resultados:
            return jsonify({
                "erro": "Nenhum dado climático encontrado para esta consulta."
            }), 404

        for item in resultados:
            for campo, valor in item.items():
                if isinstance(valor, Decimal):
                    item[campo] = float(valor)
                elif isinstance(valor, (datetime, date)):
                    item[campo] = valor.isoformat()

        return jsonify({
            "consulta_id": consulta_id,
            "quantidade": len(resultados),
            "previsoes": resultados
        }), 200

    except Exception as erro:
        return jsonify({
            "erro": "Não foi possível consultar os dados climáticos.",
            "detalhes": str(erro)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=True
    )
