"""Autenticação: hash bcrypt (senha e CPF) e sessão com tempo de expiração."""
import time
import bcrypt
from flask import session
from db import ErroNegocio, query

EXPIRACAO_SEGUNDOS = 30 * 60  # 30 minutos a partir do login


def gerar_hash(texto):
    return bcrypt.hashpw(texto.encode(), bcrypt.gensalt(rounds=10)).decode()


def conferir(texto, hash_salvo):
    """True se o texto bate com o hash salvo (hash inválido conta como False)."""
    try:
        return bcrypt.checkpw(texto.encode(), hash_salvo.encode())
    except ValueError:
        return False


def autenticar(login, senha):
    """Devolve o usuário se login e senha conferem; senão, erro."""
    login, senha = (login or "").strip(), senha or ""
    if not login or not senha:
        raise ErroNegocio("Informe usuário e senha.")
    u = query("SELECT id, nome, senha_hash FROM usuarios WHERE login = %s", (login,))
    if not u or not conferir(senha, u[0]["senha_hash"]):  # mensagem única: não revela se o usuário existe
        raise ErroNegocio("Usuário ou senha inválidos.", 401)
    return u[0]


def iniciar_sessao(usuario):
    session.clear()
    session.permanent = True
    session.update(usuario_id=usuario["id"], nome=usuario["nome"], login_em=time.time())


def logado():
    """Sessão válida = tem usuário e o tempo de expiração ainda não passou."""
    if "usuario_id" in session and time.time() - session.get("login_em", 0) <= EXPIRACAO_SEGUNDOS:
        return True
    session.clear()
    return False
