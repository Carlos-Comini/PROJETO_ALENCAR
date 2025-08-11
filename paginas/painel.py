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
    st.info('PAINEL NOVO CARREGADO - TESTE')
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&display=swap');
        html, body, .stApp {{ background: {COR_BG} !important; }}
        .alencar-topbar {{ background: {COR1}; padding: 18px 32px; border-radius: 0 0 18px 18px; display: flex; align-items: center; gap: 24px; }}
        .alencar-title {{ font-family: 'Montserrat', 'Myriad Pro', sans-serif; font-size: 2.2rem; color: {COR2}; font-weight: 700; margin-right: 32px; }}
        .alencar-empresa {{ background: {COR3}; color: {COR_TXT}; border-radius: 8px; padding: 8px 18px; font-weight: 600; font-size: 1.1rem; margin-right: 12px; }}
        .alencar-filtros {{ background: {COR1}; border-radius: 12px; padding: 18px 24px; margin: 24px 0; display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }}
        .alencar-btn-limpar {{ background: {COR4}; color: {COR_TXT}; border-radius: 8px; padding: 8px 18px; font-weight: 600; font-size: 1rem; border: none; cursor: pointer; }}
        .alencar-card {{ background: {COR2}; color: {COR4}; border-radius: 12px; padding: 18px 24px; margin: 12px 0; display: inline-block; min-width: 180px; font-family: 'Montserrat', 'Myriad Pro', sans-serif; }}
        .alencar-card-title {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }}
        .alencar-card-value {{ font-size: 2rem; font-weight: 700; }}
        .alencar-grafico {{ background: {COR1}; border-radius: 12px; padding: 18px 24px; margin: 24px 0; }}
        .alencar-tabela {{ background: {COR1}; border-radius: 12px; padding: 18px 24px; margin: 24px 0; color: {COR_TXT}; }}
        .alencar-usuarios {{ background: {COR3}; border-radius: 12px; padding: 18px 24px; margin: 24px 0; color: {COR_TXT}; }}
        </style>
    """, unsafe_allow_html=True)

    # Topo: Empresas cadastradas
    from funcoes_compartilhadas.empresas_sql import listar_empresas
    empresas = listar_empresas()
    empresas_opcoes = [e['razao_social'] for e in empresas]
    empresa_selecionada = st.selectbox("Selecione a empresa", empresas_opcoes, key="empresa_topo")
    st.markdown(f'<div class="alencar-topbar"><span class="alencar-title">Painel Alencar</span><span class="alencar-empresa">{empresa_selecionada}</span></div>', unsafe_allow_html=True)

    # Filtros
    tipos_xml = ["NF-e", "CT-e", "NFS-e", "NFC-e"]
    tipo_xml = st.selectbox("Tipo de XML", tipos_xml, key="tipo_xml")
    filtro_notas = st.checkbox("Notas encontradas", key="filtro_notas")
    filtro_arquivos = st.checkbox("Arquivos (PDF, TXT, PNG, JPEG, Word, etc.)", key="filtro_arquivos")
    if st.button("Limpar filtros", key="limpar_filtros", help="Limpa todos os filtros"):
        st.session_state["tipo_xml"] = tipos_xml[0]
        st.session_state["filtro_notas"] = False
        st.session_state["filtro_arquivos"] = False
        st.experimental_rerun()
    st.markdown('<div class="alencar-filtros">' +
        f'<b>Tipo XML:</b> {tipo_xml} &nbsp;'+
        f'<b>Notas:</b> {"Sim" if filtro_notas else "Não"} &nbsp;'+
        f'<b>Arquivos:</b> {"Sim" if filtro_arquivos else "Não"} &nbsp;'+
        '<button class="alencar-btn-limpar" onclick="window.location.reload()">Limpar filtros</button>'+
        '</div>', unsafe_allow_html=True)

    # Cards de resumo
    st.markdown('<div style="display:flex;gap:24px;flex-wrap:wrap;">', unsafe_allow_html=True)
    st.markdown(f'<div class="alencar-card"><div class="alencar-card-title">XMLs</div><div class="alencar-card-value">{_contar_xmls(tipo_xml, empresa_selecionada)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alencar-card"><div class="alencar-card-title">Notas</div><div class="alencar-card-value">{_contar_notas(empresa_selecionada)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alencar-card"><div class="alencar-card-title">Arquivos</div><div class="alencar-card-value">{_contar_arquivos(empresa_selecionada)}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Gráficos
    st.markdown('<div class="alencar-grafico">', unsafe_allow_html=True)
    st.write("Gráfico de quantidade de documentos por data")
    df_grafico = _dados_grafico(empresa_selecionada, tipo_xml)
    st.line_chart(df_grafico)
    st.write("Gráfico de valor reconhecido nos arquivos")
    st.bar_chart(df_grafico)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabela de documentos filtrados
    st.markdown('<div class="alencar-tabela">', unsafe_allow_html=True)
    st.write("Documentos filtrados:")
    df_docs = _dados_tabela(empresa_selecionada, tipo_xml, filtro_notas, filtro_arquivos)
    st.dataframe(df_docs, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Usuários vinculados à empresa
    st.markdown('<div class="alencar-usuarios">', unsafe_allow_html=True)
    st.write("Usuários do tipo cliente vinculados à empresa:")
    df_usuarios = _dados_usuarios(empresa_selecionada)
    st.dataframe(df_usuarios, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
