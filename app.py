"""Ponto de entrada: python app.py"""
import os
from flask import Flask
from autenticacao import EXPIRACAO_SEGUNDOS
from rotas import bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
app.config.update(PERMANENT_SESSION_LIFETIME=EXPIRACAO_SEGUNDOS,            # cookie dura o mesmo que a sessão
                  SESSION_REFRESH_EACH_REQUEST=False,                       # expiração conta a partir do login
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
