"""Todas as rotas HTTP: páginas HTML e API JSON."""
import mysql.connector
from flask import Blueprint, abort, jsonify, redirect, request, send_from_directory, session
import agendamento, aparelhos, autenticacao as auth, clientes
from db import ErroNegocio, testar_conexao

bp = Blueprint("rotas", __name__)
LIVRES = ("/", "/login", "/api/login", "/api/logout", "/api/teste-conexao")
PAGINAS = ("login", "principal", "clientes", "aparelhos", "agendamentos")
MODULOS = {"clientes": clientes, "aparelhos": aparelhos, "agendamentos": agendamento}


@bp.before_request
def exigir_login():
    if request.path in LIVRES or auth.logado():
        return None
    if request.path.startswith("/api/"):
        return jsonify(erro="Sessão expirada. Faça login novamente."), 401
    return redirect("/login?expirou=1")


@bp.app_errorhandler(ErroNegocio)
def erro_negocio(e):
    return jsonify(erro=e.mensagem), e.status


@bp.app_errorhandler(mysql.connector.Error)
def erro_banco(e):
    # Imprime o erro no terminal do VS Code / Prompt para facilitar o debug
    print("ERRO DE BANCO:", e)
    return jsonify(erro="Erro ao acessar o banco de dados."), 500


def corpo():
    return request.get_json(silent=True) or {}


# ---------- páginas ----------
@bp.route("/")
def raiz():
    return redirect("/principal" if auth.logado() else "/login")


@bp.route("/<nome>")
def pagina(nome):
    if nome not in PAGINAS:
        abort(404)
    return send_from_directory("templates", nome + ".html")


# ---------- autenticação e apoio ----------
@bp.post("/api/login")
def login():
    d = corpo()
    usuario = d.get("login") or d.get("usuario")
    senha = d.get("senha")
    auth.iniciar_sessao(auth.autenticar(usuario, senha))
    return jsonify(ok=True, nome=session["nome"])


@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@bp.get("/api/me")
def me():
    return jsonify(nome=session["nome"])


@bp.get("/api/teste-conexao")
def teste_conexao():
    return jsonify(testar_conexao())


@bp.get("/api/servicos")
def servicos():
    return jsonify(agendamento.listar_servicos())


# ---------- CRUD ----------
def modulo(recurso):
    if recurso not in MODULOS:
        raise ErroNegocio("Recurso não encontrado.", 404)
    return MODULOS[recurso]


@bp.route("/api/<recurso>", methods=["GET", "POST"])
def colecao(recurso):
    m = modulo(recurso)
    if request.method == "POST":
        return jsonify(m.cadastrar(corpo())), 201
    return jsonify(m.listar(request.args["q"]) if "q" in request.args else m.listar())


@bp.route("/api/<recurso>/<int:id_>", methods=["PUT", "DELETE"])
def item(recurso, id_):
    m = modulo(recurso)
    if request.method == "PUT":
        return jsonify(m.editar(id_, corpo()))
    m.excluir(id_)
    return jsonify(ok=True)