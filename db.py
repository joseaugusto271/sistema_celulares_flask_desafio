"""Acesso ao MySQL: uma conexão por consulta e parâmetros %s (evita SQL Injection)."""
import os
from datetime import date, datetime
import mysql.connector

CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Senai@118'),
    'database': os.environ.get('DB_NAME', 'assistencia_db'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4'
}


class ErroNegocio(Exception):
    """Erro de validação/regra de negócio, devolvido ao usuário em JSON com um status HTTP."""
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem, self.status = mensagem, status


def query(sql, params=()):
    """SELECT: devolve uma lista de dicionários (datas e datetimes viram texto ISO para o JSON)."""
    with mysql.connector.connect(**CONFIG) as con, con.cursor(dictionary=True) as cur:
        cur.execute(sql, params)
        linhas = cur.fetchall()
        
        # Converte qualquer objeto de data ou data/hora para string ISO
        resultado = []
        for r in linhas:
            item = {}
            for k, v in r.items():
                if isinstance(v, (date, datetime)):
                    item[k] = v.isoformat()
                else:
                    item[k] = v
            resultado.append(item)
            
        return resultado


def execute(sql, params=()):
    """INSERT/UPDATE/DELETE com commit. Devolve o id inserido (no INSERT)."""
    with mysql.connector.connect(**CONFIG) as con, con.cursor() as cur:
        cur.execute(sql, params)
        con.commit()
        return cur.lastrowid


def buscar_um(sql, params, mensagem):
    """Devolve a primeira linha da consulta; se não houver nenhuma, erro 404 com a mensagem."""
    linhas = query(sql, params)
    if not linhas:
        raise ErroNegocio(mensagem, 404)
    return linhas[0]


def bloquear_se_existir(sql, params, mensagem):
    """Se a consulta achar algum registro, erro 409 (conflito: duplicado ou registro em uso)."""
    if query(sql, params):
        raise ErroNegocio(mensagem, 409)


def testar_conexao():
    return query("SELECT DATABASE() AS banco, VERSION() AS versao")[0]