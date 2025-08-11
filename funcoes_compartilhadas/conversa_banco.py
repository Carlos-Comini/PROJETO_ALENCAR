import streamlit as st
import hashlib
import os

XML_BASE = os.path.join(os.getcwd(), "xmls")
        raise


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def autenticar_usuario(email, senha):
    from funcoes_compartilhadas.usuarios_sql import autenticar
    senha_hash = hash_senha(senha)
    usuario = autenticar(email, senha_hash)
    if usuario:
        return True, usuario.get("tipo", ""), usuario
    return False, None, None


## Funções salvar_empresa e salvar_usuario removidas. Reescreva usando SQL.


## Função listar_empresas removida. Reescreva usando SQL.

