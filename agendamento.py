"""Regras de agendamento de reparos (serviços da assistência técnica)."""
from datetime import datetime
from db import ErroNegocio, buscar_um, execute, query

STATUS = ("AGENDADO", "EM_ANDAMENTO", "CONCLUIDO", "CANCELADO")

# Agendamento já com os dados do serviço, do aparelho e do cliente
SELECT = """SELECT 
                a.id, 
                a.data_agendamento, 
                a.status, 
                a.observacao,
                s.id AS servico_id, 
                s.descricao AS servico, 
                s.valor,
                ap.id AS aparelho_id, 
                ap.imei, 
                ap.marca, 
                ap.modelo, 
                ap.cor, 
                ap.defeito,
                c.id AS cliente_id, 
                c.nome AS cliente_nome, 
                c.telefone, 
                c.email, 
                c.endereco
            FROM agendamentos a 
            JOIN aparelhos ap ON ap.id = a.aparelho_id
            JOIN clientes c ON c.id = ap.cliente_id 
            JOIN servicos s ON s.id = a.servico_id """


def _data(valor):
    """Converte o texto do formulário (AAAA-MM-DDTHH:MM) em data/hora."""
    try:
        return datetime.fromisoformat((valor or "").replace("Z", ""))
    except ValueError:
        raise ErroNegocio("Data/hora inválida.")


def listar():
    return query(SELECT + "ORDER BY a.data_agendamento, a.id")


def listar_servicos():
    return query("SELECT id, descricao, valor FROM servicos ORDER BY descricao")


def obter(id_):
    return buscar_um(SELECT + "WHERE a.id = %s", (id_,), "Agendamento não encontrado.")


def cadastrar(d):
    data = _data(d.get("data_agendamento"))
    buscar_um("SELECT id FROM aparelhos WHERE id = %s", (d.get("aparelho_id"),), "Aparelho não encontrado.")
    buscar_um("SELECT id FROM servicos WHERE id = %s", (d.get("servico_id"),), "Serviço não encontrado.")
    return obter(execute("INSERT INTO agendamentos (aparelho_id, servico_id, data_agendamento, observacao) "
                         "VALUES (%s,%s,%s,%s)", (d["aparelho_id"], d["servico_id"], data, d.get("observacao"))))


def editar(id_, d):
    """Atualiza a data (obrigatória) e, se enviados, status e observação."""
    atual = obter(id_)
    data, status = _data(d.get("data_agendamento")), d.get("status", atual["status"])
    if status not in STATUS:
        raise ErroNegocio("Status inválido.")
    execute("UPDATE agendamentos SET data_agendamento=%s, status=%s, observacao=%s WHERE id=%s",
            (data, status, d.get("observacao", atual["observacao"]), id_))
    return obter(id_)


def excluir(id_):
    obter(id_)
    execute("DELETE FROM agendamentos WHERE id = %s", (id_,))
