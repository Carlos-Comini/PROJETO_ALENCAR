def atualizar_data_documento(doc_id: int, data_documento: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE documentos SET data_documento = ? WHERE id = ?", (data_documento, doc_id))
    conn.commit()
    conn.close()
def deletar_documento(doc_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM documentos WHERE id=?', (doc_id,))
    conn.commit()
    conn.close()
import sqlite3
from typing import Optional, Dict, List

DB_PATH = 'usuarios.db'

def conectar():
    import os
    abs_path = os.path.abspath(DB_PATH)
    print(f"[DEBUG] Usando banco de dados: {abs_path}")
    return sqlite3.connect(DB_PATH)

def criar_tabela_documentos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            caminho TEXT,
            empresa TEXT,
            cnpj TEXT,
            banco TEXT,
            ano TEXT,
            mes TEXT,
            tipo TEXT,
            tipo_nota TEXT,
            usuario TEXT,
            razao_social_usuario TEXT,
            data_upload TEXT,
            data_documento TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_documento(info: Dict):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documentos (nome, caminho, empresa, cnpj, banco, ano, mes, tipo, tipo_nota, usuario, razao_social_usuario, data_upload, data_documento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        info['nome'], info['caminho'], info['empresa'], info['cnpj'], info['banco'],
        info['ano'], info['mes'], info['tipo'], info.get('tipo_nota', 'Desconhecido'),
        info.get('usuario', 'N/A'), info.get('razao_social_usuario', 'N/A'), info['data_upload'],
        info.get('data_documento', None)
    ))
    conn.commit()
    conn.close()

def listar_documentos(filtro_empresa=None) -> List[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    if filtro_empresa:
        cursor.execute('SELECT * FROM documentos WHERE empresa=?', (filtro_empresa,))
    else:
        cursor.execute('SELECT * FROM documentos')
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(colunas, row)) for row in rows]

def buscar_documento_por_id(doc_id: int) -> Optional[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documentos WHERE id=?', (doc_id,))
    row = cursor.fetchone()
    colunas = [desc[0] for desc in cursor.description]
    conn.close()
    if row:
        return dict(zip(colunas, row))
    return None
