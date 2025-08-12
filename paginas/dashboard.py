import streamlit as st
import pandas as pd
import plotly.express as px
from funcoes_compartilhadas.documentos_sql import listar_documentos

def exibir():
    st.title("📊 Dashboard de Documentos Contábeis")
    registros = listar_documentos()
    df = pd.DataFrame(registros)

    if df.empty:
        st.warning("Nenhum documento encontrado.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    empresas = ['Todas'] + sorted(df['empresa'].dropna().unique())
    usuarios = ['Todos'] + sorted(df['usuario'].dropna().unique())
    tipos_nota = ['Todos'] + sorted(df['tipo_nota'].dropna().unique())

    empresa_filtro = col1.selectbox("Empresa", empresas)
    usuario_filtro = col2.selectbox("Usuário", usuarios)
    tipo_nota_filtro = col3.selectbox("Tipo de Nota", tipos_nota)

    filtro = (df['empresa'].notna())
    if empresa_filtro != 'Todas':
        filtro &= (df['empresa'] == empresa_filtro)
    if usuario_filtro != 'Todos':
        filtro &= (df['usuario'] == usuario_filtro)
    if tipo_nota_filtro != 'Todos':
        filtro &= (df['tipo_nota'] == tipo_nota_filtro)
    df_filtrado = df[filtro]

    colA, colB, colC, colD, colE = st.columns(5)
    colA.metric("Documentos", len(df_filtrado))
    colB.metric("Empresas", df_filtrado['empresa'].nunique())
    colC.metric("Usuários", df_filtrado['usuario'].nunique())
    colD.metric("Entradas", (df_filtrado['tipo_nota'] == 'Entrada').sum())
    colE.metric("Saídas", (df_filtrado['tipo_nota'] == 'Saída').sum())

    st.markdown("---")

    graf_pizza = px.pie(df_filtrado, names='tipo_nota', title='Distribuição de Tipo de Nota')
    st.plotly_chart(graf_pizza, use_container_width=True)

    if 'mes' in df_filtrado.columns and 'ano' in df_filtrado.columns:
        df_filtrado['periodo'] = df_filtrado['mes'].astype(str) + '/' + df_filtrado['ano'].astype(str)
        graf_barras = px.bar(df_filtrado.groupby('periodo').size().reset_index(name='Qtd'), x='periodo', y='Qtd', title='Documentos por Período')
        st.plotly_chart(graf_barras, use_container_width=True)

    ranking = df_filtrado['empresa'].value_counts().reset_index()
    ranking.columns = ['Empresa', 'Documentos']
    st.subheader("🏆 Ranking de Empresas")
    st.dataframe(ranking, use_container_width=True)

    st.subheader("📋 Tabela de Documentos Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    st.download_button("⬇️ Exportar dados filtrados para Excel", df_filtrado.to_excel(index=False), file_name="dashboard_documentos.xlsx")