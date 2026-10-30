"""Passo de teste do roteiro: python testar_conexao.py"""
from db import testar_conexao
try:
    print("Conexão OK:", testar_conexao())
except Exception as e:
    print("FALHA na conexão:", e)
