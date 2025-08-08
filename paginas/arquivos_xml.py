from funcoes_compartilhadas.empresas_sql import buscar_empresa_por_cnpj
from funcoes_compartilhadas.documentos_sql import criar_tabela_documentos, registrar_documento, listar_documentos
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
XML_BASE = Path("xmls")



def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        ide = root.find(".//nfe:ide", ns)
        emit = root.find(".//nfe:emit", ns)
        dest = root.find(".//nfe:dest", ns)
        total = root.find(".//nfe:ICMSTot", ns)

        numero = ide.find("nfe:nNF", ns).text if ide is not None else "—"
        data_emissao = ide.find("nfe:dhEmi", ns).text[:10] if ide is not None else "—"
        cnpj_emit = emit.find("nfe:CNPJ", ns).text if emit is not None else "—"
        cnpj_dest = dest.find("nfe:CNPJ", ns).text if dest is not None else "—"
        valor = total.find("nfe:vNF", ns).text if total is not None else "—"

        return {
            "Número": numero,
            "Data": data_emissao,
            "CNPJ_Emitente": cnpj_emit,
            "CNPJ_Destinatario": cnpj_dest,
            "Valor": valor
        }
    except:
        return {"Número": "Erro", "Data": "Erro", "CNPJ_Emitente": "Erro", "CNPJ_Destinatario": "Erro", "Valor": "Erro"}

def exibir():
    from funcoes_compartilhadas.empresas_sql import criar_tabela_empresas
    criar_tabela_empresas()
    criar_tabela_documentos()
    st.title("📂 Gestão de Arquivos XML")
    st.subheader("📤 Enviar XML manualmente")
    uploaded = st.file_uploader("Escolha um ou mais arquivos XML", type=["xml"], accept_multiple_files=True)

    if uploaded:
        criar_tabela_documentos()
        for file in uploaded:
            temp_path = XML_BASE / "temp.xml"
            with open(temp_path, "wb") as f:
                f.write(file.read())
            info = parse_xml(temp_path)
            cnpj = info["CNPJ_Destinatario"] or info["CNPJ_Emitente"] or "geral"
            empresa_info = buscar_empresa_por_cnpj(cnpj)
            nome_empresa = empresa_info["razao_social"] if empresa_info else cnpj
            hoje = datetime.today().strftime("%Y_%m_%d")
            pasta_destino = XML_BASE / cnpj / hoje
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho = pasta_destino / file.name
            temp_path.replace(caminho)
            # Registrar no banco
            info_doc = {
                "nome": file.name,
                "caminho": str(caminho),
                "empresa": nome_empresa,
                "cnpj": cnpj,
                "banco": "XML",
                "ano": hoje.split('_')[0],
                "mes": hoje.split('_')[1],
                "tipo": "xml",
                "data_upload": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            registrar_documento(info_doc)
            st.info("Arquivo XML salvo e registrado!")
        st.success(f"{len(uploaded)} arquivo(s) salvo(s) com sucesso!")

    st.subheader("📁 Arquivos Recebidos")
    documentos = listar_documentos()
    empresas = sorted(set(d["empresa"] for d in documentos if d["banco"] == "XML"))
    filtro = st.selectbox("Filtrar por empresa", ["Todas"] + empresas)
    docs_xml = [d for d in documentos if d["banco"] == "XML"]
    if filtro != "Todas":
        docs_xml = [d for d in docs_xml if d["empresa"] == filtro]
    if docs_xml:
        for doc in docs_xml:
            with st.expander(f'{doc["nome"]} — {doc["empresa"]} {doc["ano"]}/{doc["mes"]}'):
                st.write(f"📌 Empresa: {doc['empresa']}")
                st.write(f"📅 Data: {doc['ano']}/{doc['mes']}")
                with open(doc["caminho"], "rb") as f:
                    st.download_button("⬇️ Baixar XML", f, file_name=doc["nome"])
    else:
        st.info("Nenhum arquivo XML encontrado.")