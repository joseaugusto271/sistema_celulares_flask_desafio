"""Regras de aparelhos. Todo aparelho pertence a um cliente já cadastrado."""
import re
from db import ErroNegocio, bloquear_se_existir, buscar_um, execute, query

SELECT = """
    SELECT
        ap.id,
        ap.cliente_id,
        c.nome AS cliente_nome,
        ap.imei,
        ap.marca,
        ap.modelo,
        ap.cor,
        ap.defeito
    FROM aparelhos ap
    JOIN clientes c ON c.id = ap.cliente_id
"""

IMEI = re.compile(r"[0-9]{15}")  # IMEI tem 15 dígitos (ex.: 356938035643809)


def _inteiro(valor, mensagem):
    """Converte para número inteiro ou dá erro com a mensagem."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ErroNegocio(mensagem)


def _validar(d, id_=0):
    """Confere os dados e devolve (cliente_id, imei, marca, modelo, cor, defeito). id_=0 é cadastro."""
    imei = re.sub(r"\D", "", d.get("imei") or "")
    marca, modelo = (d.get("marca") or "").strip(), (d.get("modelo") or "").strip()
    defeito = (d.get("defeito") or "").strip()
    if not IMEI.fullmatch(imei):
        raise ErroNegocio("IMEI inválido (informe os 15 dígitos).")
    if not marca or not modelo:
        raise ErroNegocio("Informe marca e modelo.")
    if not defeito:
        raise ErroNegocio("Informe o defeito relatado pelo cliente.")
    cliente_id = _inteiro(d.get("cliente_id"), "Selecione o cliente proprietário do aparelho.")
    buscar_um("SELECT id FROM clientes WHERE id = %s", (cliente_id,), "O cliente informado não está cadastrado.")
    bloquear_se_existir("SELECT id FROM aparelhos WHERE imei = %s AND id <> %s", (imei, id_), "IMEI já cadastrado.")
    return cliente_id, imei, marca, modelo, d.get("cor"), defeito


def listar():
    return query(SELECT + " ORDER BY c.nome, ap.modelo")


def obter(id_):
    return buscar_um(SELECT + " WHERE ap.id = %s", (id_,), "Aparelho não encontrado.")


def cadastrar(d):
    return obter(execute("INSERT INTO aparelhos (cliente_id, imei, marca, modelo, cor, defeito) "
                         "VALUES (%s,%s,%s,%s,%s,%s)", _validar(d)))


def editar(id_, d):
    obter(id_)
    execute("UPDATE aparelhos SET cliente_id=%s, imei=%s, marca=%s, modelo=%s, cor=%s, defeito=%s WHERE id=%s",
            (*_validar(d, id_), id_))
    return obter(id_)


def excluir(id_):
    obter(id_)
    bloquear_se_existir("SELECT id FROM agendamentos WHERE aparelho_id = %s", (id_,),
                        "Aparelho possui agendamentos. Exclua-os antes.")
    execute("DELETE FROM aparelhos WHERE id = %s", (id_,))