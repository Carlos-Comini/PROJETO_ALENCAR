import streamlit as st
import requests
from funcoes_compartilhadas.empresas_sql import inserir_empresa
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title

def buscar_razao_social(cnpj):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("razao_social", "")
    return ""

def exibir():
    aplicar_estilo_padrao()
    set_page_title("Cadastro de Empresas")
    st.header("Cadastro de Empresas Clientes")


    with st.form("form_empresa"):
        cnpj = st.text_input("CNPJ")
        buscar = st.form_submit_button("Buscar Razão Social")

        if buscar:
            if cnpj:
                razao = buscar_razao_social(cnpj)
                if razao:
                    st.success(f"Razão Social encontrada: {razao}")
                    st.session_state["razao_social"] = razao
                else:
                    st.error("Razão Social não encontrada.")

        razao_social = st.text_input("Razão Social", value=st.session_state.get("razao_social", ""))
        salvar = st.form_submit_button("Salvar Empresa")

        if salvar:
            if cnpj and razao_social:
                inserir_empresa(cnpj, razao_social)
                st.success("Empresa cadastrada com sucesso.")
                st.session_state["razao_social"] = ""
            else:
                st.error("Preencha todos os campos.")

    # Tabela de empresas cadastradas
    st.subheader("Empresas já cadastradas")
    try:
        from funcoes_compartilhadas.empresas_sql import listar_empresas, criar_tabela_empresas
        criar_tabela_empresas()
        empresas = listar_empresas()
        import pandas as pd
        df_empresas = pd.DataFrame(empresas)
        st.dataframe(df_empresas, use_container_width=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar empresas: {e}")
