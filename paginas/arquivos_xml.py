from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_google_drive(file_obj, filename, folder_id=None):
    import json
    from io import BytesIO
    from google.oauth2.service_account import Credentials
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = credenciais_dict
    gauth.ServiceAuth()
    drive = GoogleDrive(gauth)
    file_drive = drive.CreateFile({"title": filename, "parents": [{"id": folder_id}] if folder_id else []})
    file_drive.SetContentString(file_obj.read().decode("latin1") if hasattr(file_obj, "read") else file_obj)
    file_drive.Upload()
    return file_drive["id"]
import gspread
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

XML_BASE = Path(r"https://github.com/Carlos-Comini/PROJETO_XML/tree/main/xmls")

def get_cnpjs_planilha():
    import json
    from google.oauth2.service_account import Credentials
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict)
    gc = gspread.authorize(credenciais)
    sh = gc.open_by_key('1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw')
    ws = sh.worksheet('Empresas')
    cnpjs = ws.col_values(2)[1:]      # Segunda coluna: CNPJ
    razoes = ws.col_values(3)[1:]     # Terceira coluna: Razão Social
    return {cnpj: razao for cnpj, razao in zip(cnpjs, razoes)}

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
    st.title("📂 Gestão de Arquivos XML")
    st.subheader("📤 Enviar XML manualmente")
    uploaded = st.file_uploader("Escolha um ou mais arquivos XML", type=["xml"], accept_multiple_files=True)

    if uploaded:
        cnpjs_empresas = get_cnpjs_planilha()
        for file in uploaded:
            temp_path = XML_BASE / "temp.xml"
            with open(temp_path, "wb") as f:
                f.write(file.read())
            info = parse_xml(temp_path)
            if info["CNPJ_Destinatario"] in cnpjs_empresas:
                cnpj = info["CNPJ_Destinatario"]
            elif info["CNPJ_Emitente"] in cnpjs_empresas:
                cnpj = info["CNPJ_Emitente"]
            else:
                cnpj = "geral"
            hoje = datetime.today().strftime("%Y_%m_%d")
            pasta_destino = XML_BASE / cnpj / hoje
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho = pasta_destino / file.name
            temp_path.replace(caminho)

            # Upload para Google Drive
            file.seek(0)
            try:
                folder_id = "1V7qAWb8MpoX6fV9LVB0Cq8ovlogEanmt"
                file_id = upload_google_drive(file, file.name, folder_id=folder_id)
                st.info(f"Arquivo XML enviado para o Google Drive (ID: {file_id}) na pasta compartilhada!")
            except Exception as e:
                st.warning(f"Falha ao enviar para o Google Drive: {e}")
        st.success(f"{len(uploaded)} arquivo(s) salvo(s) com sucesso!")

    st.subheader("📁 Arquivos Recebidos")
    try:
        import json
        folder_id = "1QrgORE3rm2d_CusD7cqT12wN5wQoeurj"
        credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        gauth = GoogleAuth()
        gauth.settings["client_config_backend"] = "service"
        gauth.settings["service_config"] = {
            "client_json_dict": credenciais_dict,
            "client_user_email": credenciais_dict.get("client_email")
        }
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        if file_list:
            for file in file_list:
                file_link = f'https://drive.google.com/file/d/{file["id"]}/view?usp=sharing'
                st.markdown(f"- [{file['title']}]({file_link})")
        else:
            st.info("Nenhum arquivo encontrado na pasta do Google Drive XMLX.")
    except Exception as e:
        st.warning(f"Falha ao listar arquivos do Google Drive: {e}")