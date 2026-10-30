"""Regras de clientes. O CPF é guardado só como hash bcrypt (criptografia, LGPD)."""
import re
from autenticacao import conferir, gerar_hash
from db import ErroNegocio, bloquear_se_existir, buscar_um, execute, query

COLUNAS = "id, nome, telefone, email, endereco, criado_em"


def so_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def cpf_valido(cpf):
    """Confere só a quantidade: 11 dígitos (não precisa ser um CPF real)."""
    return len(cpf) == 11


def _dono_do_cpf(cpf):
    """Id do cliente com este CPF ou None. O hash bcrypt não aceita WHERE, então compara um a um."""
    for r in query("SELECT id, cpf_hash FROM clientes"):
        if conferir(cpf, r["cpf_hash"]):
            return r["id"]


def _validar(d, id_=None):
    """id_=None é cadastro (CPF obrigatório); com id_ é edição (CPF vazio mantém o atual)."""
    nome, email, cpf = (d.get("nome") or "").strip(), (d.get("email") or "").strip(), so_digitos(d.get("cpf"))
    if len(nome) < 3:
        raise ErroNegocio("Informe o nome completo.")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ErroNegocio("E-mail inválido.")
    if (id_ is None or cpf) and not cpf_valido(cpf):
        raise ErroNegocio("CPF deve conter 11 dígitos.")
    if cpf and _dono_do_cpf(cpf) not in (None, id_):
        raise ErroNegocio("Já existe cliente com este CPF.", 409)
    return nome, cpf, email or None


def listar(termo=""):
    """Busca por nome, e-mail, telefone ou CPF completo (termo vazio lista todos)."""
    termo = (termo or "").strip()
    achados = query(f"SELECT {COLUNAS} FROM clientes WHERE nome LIKE %s OR email LIKE %s "
                    "OR telefone LIKE %s ORDER BY nome", (f"%{termo}%",) * 3)
    cpf = so_digitos(termo)
    dono = _dono_do_cpf(cpf) if cpf_valido(cpf) else None
    if dono and all(a["id"] != dono for a in achados):
        achados.append(obter(dono))
    return achados


def obter(id_):
    return buscar_um(f"SELECT {COLUNAS} FROM clientes WHERE id = %s", (id_,), "Cliente não encontrado.")


def cadastrar(d):
    nome, cpf, email = _validar(d)
    return obter(execute("INSERT INTO clientes (nome, cpf_hash, telefone, email, endereco) VALUES (%s,%s,%s,%s,%s)",
                         (nome, gerar_hash(cpf), d.get("telefone"), email, d.get("endereco"))))


def editar(id_, d):
    obter(id_)
    nome, cpf, email = _validar(d, id_)
    novo_hash = gerar_hash(cpf) if cpf else None  # None + COALESCE = mantém o hash atual
    execute("UPDATE clientes SET nome=%s, cpf_hash=COALESCE(%s, cpf_hash), telefone=%s, email=%s, endereco=%s "
            "WHERE id=%s", (nome, novo_hash, d.get("telefone"), email, d.get("endereco"), id_))
    return obter(id_)


def excluir(id_):
    obter(id_)
    bloquear_se_existir("SELECT id FROM aparelhos WHERE cliente_id = %s", (id_,),
                        "Cliente possui aparelhos cadastrados. Exclua-os antes.")
    execute("DELETE FROM clientes WHERE id = %s", (id_,))