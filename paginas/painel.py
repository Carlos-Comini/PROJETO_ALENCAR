import streamlit as st
import pandas as pd
from datetime import datetime

# Paleta Alencar
COR1 = "#40585E"  # cinza escuro
COR2 = "#28A6C7"  # azul claro
COR3 = "#0C9AD7"  # azul médio
COR4 = "#001927"  # azul escuro
COR_BG = "#181a20"  # fundo
COR_TXT = "#FFFFFF"  # texto

def exibir():
    st.title("Dashboard Simples")
    st.subheader("Empresas Registradas")
    from funcoes_compartilhadas.empresas_sql import listar_empresas
    empresas = listar_empresas()
    import pandas as pd
    df_empresas = pd.DataFrame(empresas)
    st.dataframe(df_empresas, use_container_width=True)

    st.subheader("Usuários Registrados")
    try:
        from funcoes_compartilhadas.usuarios_sql import listar_usuarios
        usuarios = listar_usuarios()
        df_usuarios = pd.DataFrame(usuarios)
        st.dataframe(df_usuarios, use_container_width=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar usuários: {e}")

def _contar_xmls(tipo_xml, empresa):
    # Exemplo: filtrar por tipo e empresa
    from funcoes_compartilhadas.documentos_sql import listar_documentos
    docs = [d for d in listar_documentos() if d["banco"] == "XML" and tipo_xml in d["nome"] and d["empresa"] == empresa]
    return len(docs)

def _contar_notas(empresa):
    # Exemplo: contar notas encontradas
    from funcoes_compartilhadas.documentos_sql import listar_documentos
    docs = [d for d in listar_documentos() if d["banco"] == "XML" and d["empresa"] == empresa]
    return len(docs)

def _contar_arquivos(empresa):
    from funcoes_compartilhadas.documentos_sql import listar_documentos
    docs = [d for d in listar_documentos() if d["banco"] != "XML" and d["empresa"] == empresa]
    return len(docs)

def _dados_grafico(empresa, tipo_xml):
    # Exemplo: gráfico de quantidade por data
    from funcoes_compartilhadas.documentos_sql import listar_documentos
    docs = [d for d in listar_documentos() if d["empresa"] == empresa and (tipo_xml in d["nome"] or d["banco"] == "XML")]
    df = pd.DataFrame(docs)
    if not df.empty:
        df["data_upload"] = pd.to_datetime(df["data_upload"], errors="coerce")
        return df.groupby(df["data_upload"].dt.date).size()
    return pd.Series()

def _dados_tabela(empresa, tipo_xml, filtro_notas, filtro_arquivos):
    from funcoes_compartilhadas.documentos_sql import listar_documentos
    docs = [d for d in listar_documentos() if d["empresa"] == empresa]
    if filtro_notas:
        docs = [d for d in docs if d["banco"] == "XML"]
    if filtro_arquivos:
        docs = [d for d in docs if d["banco"] != "XML"]
    if tipo_xml:
        docs = [d for d in docs if tipo_xml in d["nome"] or tipo_xml in d["banco"]]
    df = pd.DataFrame(docs)
    return df if not df.empty else pd.DataFrame([{"Mensagem": "Nenhum documento encontrado"}])

def _dados_usuarios(empresa):
    try:
        from funcoes_compartilhadas.usuarios_sql import listar_usuarios
        usuarios = [u for u in listar_usuarios() if u.get("tipo", "").lower() == "cliente" and u.get("empresa", "") == empresa]
        return pd.DataFrame(usuarios)
    except:
        return pd.DataFrame([{"Mensagem": "Nenhum usuário encontrado"}])
