

from funcoes_compartilhadas.empresas_sql import listar_empresas
from funcoes_compartilhadas.documentos_sql import criar_tabela_documentos, registrar_documento, listar_documentos
import streamlit as st
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title
aplicar_estilo_padrao()
set_page_title("Arquivo")
st.markdown("""
    <style>
    .topbar {position: fixed;top: 0;left: 0;width: 100vw;height: 64px;background: #263a53;display: flex;align-items: center;z-index: 100;box-shadow: 0 2px 8px #0002;}
    .topbar-logo {height: 40px;margin-left: 32px;margin-right: 24px;}
    .topbar-menu {display: flex;gap: 32px;}
    .topbar-menu a {color: #fff;font-size: 1.1rem;text-decoration: none;font-weight: 500;padding: 8px 0;transition: color 0.2s;}
    .topbar-menu a:hover {color: #42a5f5;}
    .topbar-account {margin-left: auto;margin-right: 32px;background: #42a5f5;color: #fff;border-radius: 8px;padding: 8px 18px;font-weight: 600;font-size: 1rem;box-shadow: 0 2px 8px #0002;}
    .stApp {padding-top: 72px !important;}
    </style>
    <div class="topbar">
        <img src="https://raw.githubusercontent.com/Notalize/brand-assets/main/logo-notalize.png" class="topbar-logo" alt="Logo" />
        <div class="topbar-menu">
            <a href="#">Cadastros</a>
            <a href="#">Administrativo</a>
            <a href="#">Busca de Documentos</a>
            <a href="#">NF-e | NFC-e | CF-e</a>
            <a href="#">CT-e</a>
            <a href="#">NFC-e</a>
            <a href="#">MDF-e</a>
            <a href="#">Relatórios</a>
        </div>
        <div class="topbar-account">Minha Conta</div>
    </div>
""", unsafe_allow_html=True)

import streamlit as st
from pathlib import Path
from datetime import datetime
import mimetypes
import re

BASE_DIR = Path("arquivo")

# Lista de bancos conhecidos para identificar o nome mesmo que contenha outras palavras
BANCOS_CONHECIDOS = [
    "SICREDI", "SICOOB", "BRADESCO", "BANCO DO BRASIL", "CAIXA", "ITAU",
    "SANTANDER", "INTER", "NUBANK", "BTG", "C6", "XP"
]

def get_cnpjs_sql():
    empresas = listar_empresas()
    return {e['cnpj']: e['razao_social'] for e in empresas}

def extrair_info(nome_arquivo):
    nome_limpo = nome_arquivo.lower()
    cnpj_match = re.search(r"\d{14}", nome_limpo)
    data_match = re.search(r"(\d{2})_(\d{4})", nome_limpo)

    cnpj = cnpj_match.group() if cnpj_match else "geral"
    mes = data_match.group(1) if data_match else "00"
    ano = data_match.group(2) if data_match else "0000"

    banco = "desconhecido"
    for b in BANCOS_CONHECIDOS:
        if b.lower() in nome_limpo:
            banco = b.upper()
            break

    return cnpj, banco, ano, mes

def exibir():
    criar_tabela_documentos()
    st.title("📁 Arquivos Contábil")

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    criar_tabela_documentos()
    st.subheader("📤 Enviar arquivos")

    tipos_aceitos = [
        "pdf", "jpg", "jpeg", "png",
        "xls", "xlsx",
        "doc", "docx",
        "ppt", "pptx",
        "txt"
    ]

    arquivos = st.file_uploader(
        "Envie arquivos (PDF, Excel, Word, Imagem, TXT...)", 
        type=tipos_aceitos, accept_multiple_files=True
    )

    if arquivos:
        from funcoes_compartilhadas.empresas_sql import buscar_empresa_por_cnpj
        for arq in arquivos:
            nome = arq.name
            cnpj, banco, ano, mes = extrair_info(nome)
            pasta_destino = BASE_DIR / cnpj / banco / ano / mes
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho = pasta_destino / nome
            with open(caminho, "wb") as f:
                f.write(arq.read())
            # Buscar nome da empresa via SQL
            empresa_info = buscar_empresa_por_cnpj(cnpj)
            nome_empresa = empresa_info["razao_social"] if empresa_info else cnpj
            # Registrar no banco
            info_doc = {
                "nome": nome,
                "caminho": str(caminho),
                "empresa": nome_empresa,
                "cnpj": cnpj,
                "banco": banco,
                "ano": ano,
                "mes": mes,
                "tipo": mimetypes.guess_type(caminho)[0] or "desconhecido",
                "data_upload": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            registrar_documento(info_doc)
            st.info("Arquivo salvo e registrado!")
        st.success(f"{len(arquivos)} arquivo(s) enviado(s) com sucesso!")

    st.subheader("📂 Arquivos Armazenados")
    documentos = listar_documentos()
    empresas = sorted(set(d["empresa"] for d in documentos))
    filtro = st.selectbox("Filtrar por empresa", ["Todas"] + empresas)
    if filtro != "Todas":
        documentos = [d for d in documentos if d["empresa"] == filtro]
    for doc in documentos:
        with st.expander(f'{doc["nome"]} — {doc["banco"]} {doc["mes"]}/{doc["ano"]} — {doc["empresa"]}'):
            st.write(f"📌 Empresa: {doc['empresa']}")
            st.write(f"🏦 Banco: {doc['banco']}")
            st.write(f"📅 Data: {doc['mes']}/{doc['ano']}")
            with open(doc["caminho"], "rb") as f:
                st.download_button("⬇️ Baixar", f, file_name=doc["nome"])


