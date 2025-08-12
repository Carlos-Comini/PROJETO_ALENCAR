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
            cnpj_emit = info["CNPJ_Emitente"]
            cnpj_dest = info["CNPJ_Destinatario"]
            # Verifica se o CNPJ do emitente ou destinatário está cadastrado
            from funcoes_compartilhadas.empresas_sql import listar_empresas
            empresas_cadastradas = [e["cnpj"] for e in listar_empresas()]
            # Definir CNPJ e tipo de nota antes de extrair tipo_xml
            tipo_nota = 'Desconhecido'
            cnpj = None
            if cnpj_emit in empresas_cadastradas:
                tipo_nota = 'Saída'
                cnpj = cnpj_emit
            elif cnpj_dest in empresas_cadastradas:
                tipo_nota = 'Entrada'
                cnpj = cnpj_dest
            else:
                st.warning(
                    f"O arquivo '{file.name}' não foi aceito porque o CNPJ do emitente ou destinatário não está cadastrado no sistema. "
                    "Por favor, cadastre a empresa antes de enviar este XML."
                )
                continue

            # Extrai tipo de XML (NF-e, CT-e, etc) e tipo de nota ANTES de mover o arquivo
            try:
                tree = ET.parse(temp_path)
                root = tree.getroot()
                ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
                # O elemento <ide> está dentro de <NFe>/<infNFe>/<ide>
                ide = root.find('.//{http://www.portalfiscal.inf.br/nfe}NFe/{http://www.portalfiscal.inf.br/nfe}infNFe/{http://www.portalfiscal.inf.br/nfe}ide')
                mod_val = ide.find('{http://www.portalfiscal.inf.br/nfe}mod').text if ide is not None and ide.find('{http://www.portalfiscal.inf.br/nfe}mod') is not None else ''
                if mod_val == '55':
                    tipo_xml = 'NF-e'
                elif mod_val == '65':
                    tipo_xml = 'NFC-e'
                elif mod_val == '57':
                    tipo_xml = 'CT-e'
                else:
                    tipo_xml = mod_val or 'Desconhecido'
                tpNF = ide.find('{http://www.portalfiscal.inf.br/nfe}tpNF').text if ide is not None and ide.find('{http://www.portalfiscal.inf.br/nfe}tpNF') is not None else ''
                tipo_nota = 'Saída' if tpNF == '1' else ('Entrada' if tpNF == '0' else 'Desconhecido')
            except Exception:
                tipo_xml = 'Desconhecido'
                tipo_nota = 'Desconhecido'

            empresa_info = buscar_empresa_por_cnpj(cnpj)
            nome_empresa = empresa_info["razao_social"] if empresa_info else cnpj
            hoje = datetime.today().strftime("%Y_%m_%d")
            pasta_destino = XML_BASE / cnpj / hoje
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho = pasta_destino / file.name
            temp_path.replace(caminho)
            # Evita duplicidade: verifica se já existe registro igual
            documentos_existentes = listar_documentos()
            ja_existe = any(
                d["nome"] == file.name and d["caminho"] == str(caminho)
                for d in documentos_existentes
            )
            if ja_existe:
                st.warning(f"O arquivo '{file.name}' já foi registrado para esta empresa e data.")
            else:
                info_doc = {
                    "nome": file.name,
                    "caminho": str(caminho),
                    "empresa": nome_empresa,
                    "cnpj": cnpj,
                    "banco": "XML",
                    "ano": hoje.split('_')[0],
                    "mes": hoje.split('_')[1],
                    "tipo_xml": tipo_xml,
                    "tipo_nota": tipo_nota,
                    "tipo": tipo_xml,
                    "data_upload": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                registrar_documento(info_doc)
                st.info(f"Arquivo XML salvo e registrado como {tipo_xml} - {tipo_nota}!")
        st.success(f"{len(uploaded)} arquivo(s) salvo(s) com sucesso!")

    st.subheader("📁 Arquivos Recebidos")
    documentos = listar_documentos()
    empresas = sorted(set(d["empresa"] for d in documentos if d["banco"] == "XML"))
    filtro = st.selectbox("Filtrar por empresa", ["Todas"] + empresas)
    docs_xml = [d for d in documentos if d["banco"] == "XML"]
    if filtro != "Todas":
        docs_xml = [d for d in docs_xml if d["empresa"] == filtro]
    import os
    from funcoes_compartilhadas.documentos_sql import deletar_documento
    if docs_xml:
        for doc in docs_xml:
            with st.expander(f'{doc["nome"]} — {doc["empresa"]} {doc["ano"]}/{doc["mes"]}'):
                st.write(f"📌 Empresa: {doc['empresa']}")
                tipo_xml = doc.get('tipo_xml', 'Desconhecido')
                tipo_nota = doc.get('tipo_nota', 'Desconhecido')
                st.write(f"📄 Tipo de XML: {tipo_xml}")
                st.write(f"📝 Tipo de Nota: {tipo_nota}")
                st.write(f"📅 Data: {doc['ano']}/{doc['mes']}")
                with open(doc["caminho"], "rb") as f:
                    st.download_button("⬇️ Baixar XML", f, file_name=doc["nome"], key=f"download_{doc['id']}")
                if st.button(f"🗑️ Excluir XML {doc['id']}", key=f"delxml_{doc['id']}"):
                    if st.session_state.get(f"confirm_delxml_{doc['id']}") != True:
                        st.warning("Tem certeza que deseja excluir este XML?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Sim, excluir", key=f"confirma_xml_{doc['id']}"):
                                st.session_state[f"confirm_delxml_{doc['id']}"] = True
                        with col2:
                            if st.button("Não cancelar", key=f"cancela_xml_{doc['id']}"):
                                st.session_state[f"confirm_delxml_{doc['id']}"] = False
                    elif st.session_state.get(f"confirm_delxml_{doc['id']}") == True:
                        try:
                            deletar_documento(doc['id'])
                            excluiu_arquivo = False
                            if os.path.exists(doc['caminho']):
                                os.remove(doc['caminho'])
                                excluiu_arquivo = True
                            st.success(
                                f"XML excluído com sucesso!\n"
                                f"Caminho do arquivo: {doc['caminho']}\n"
                                f"Arquivo físico removido: {'Sim' if excluiu_arquivo else 'Não'}\n"
                                f"Registro removido do banco: Sim"
                            )
                            st.session_state[f"confirm_delxml_{doc['id']}"] = False
                            # Atualiza a lista de documentos para sumir da tabela
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}\nCaminho do arquivo: {doc['caminho']}")
    else:
        st.info("Nenhum arquivo XML encontrado.")