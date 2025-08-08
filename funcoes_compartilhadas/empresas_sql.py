import sqlite3
from typing import Optional, Dict, List

DB_PATH = 'usuarios.db'

def conectar():
    return sqlite3.connect(DB_PATH)

def buscar_empresa_por_cnpj(cnpj: str) -> Optional[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas WHERE cnpj=?", (cnpj,))
    row = cursor.fetchone()
    conn.close()
    if row:
        colunas = [desc[0] for desc in cursor.description]
        return dict(zip(colunas, row))
    return None

def listar_empresas() -> List[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas")
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(colunas, row)) for row in rows]
