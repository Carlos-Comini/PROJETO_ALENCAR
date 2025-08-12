import streamlit as st
import pandas as pd
import plotly.express as px
from funcoes_compartilhadas.documentos_sql import listar_documentos

st.set_page_config(page_title="Dashboard Contábil", layout="wide")
st.title("📊 Dashboard Contábil Avançado")

# Carrega dados
docs = listar_documentos()
df = pd.DataFrame(docs)

if df.empty:
    st.warning("Nenhum documento encontrado.")
    st.stop()

# Filtros dinâmicos
col1, col2, col3 = st.columns(3)
empresas = sorted(df["empresa"].dropna().unique())
usuarios = sorted(df["usuario"].dropna().unique())
tipos_nota = sorted(df["tipo_nota"].dropna().unique())

empresa_sel = col1.selectbox("Empresa", ["Todas"] + empresas)
usuario_sel = col2.selectbox("Usuário", ["Todos"] + usuarios)
tipo_nota_sel = col3.selectbox("Tipo de Nota", ["Todos"] + tipos_nota)

filtro = (df["empresa"].eq(empresa_sel) if empresa_sel != "Todas" else True)
filtro &= (df["usuario"].eq(usuario_sel) if usuario_sel != "Todos" else True)
filtro &= (df["tipo_nota"].eq(tipo_nota_sel) if tipo_nota_sel != "Todos" else True)
df_filtrado = df[filtro]

# Indicadores rápidos
colA, colB, colC, colD, colE = st.columns(5)
colA.metric("Documentos", len(df_filtrado))
colB.metric("Empresas", df_filtrado["empresa"].nunique())
colC.metric("Usuários", df_filtrado["usuario"].nunique())
colD.metric("Entradas", (df_filtrado["tipo_nota"] == "Entrada").sum())
colE.metric("Saídas", (df_filtrado["tipo_nota"] == "Saída").sum())

# Gráfico de pizza - Distribuição de tipo de nota
fig_pizza = px.pie(df_filtrado, names="tipo_nota", title="Distribuição de Tipos de Nota")
st.plotly_chart(fig_pizza, use_container_width=True)

# Gráfico de barras - Documentos por mês
if "ano" in df_filtrado and "mes" in df_filtrado:
    df_filtrado["periodo"] = df_filtrado["ano"] + "-" + df_filtrado["mes"]
    fig_bar = px.bar(df_filtrado.groupby("periodo").size().reset_index(name="Qtd"), x="periodo", y="Qtd", title="Documentos por Mês")
    st.plotly_chart(fig_bar, use_container_width=True)

# Ranking de empresas
ranking = df_filtrado["empresa"].value_counts().reset_index()
ranking.columns = ["Empresa", "Documentos"]
st.subheader("🏆 Ranking de Empresas")
st.dataframe(ranking)

# Tabela detalhada
st.subheader("📋 Tabela de Documentos")
st.dataframe(df_filtrado)

# Exportação
st.download_button("⬇️ Exportar dados filtrados (CSV)", df_filtrado.to_csv(index=False), file_name="dashboard_documentos.csv")
