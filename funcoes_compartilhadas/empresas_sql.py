def inserir_empresa(cnpj, razao_social, endereco=None, telefone=None, email=None):
    criar_tabela_empresas()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO empresas (cnpj, razao_social, endereco, telefone, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (cnpj, razao_social, endereco or '', telefone or '', email or ''))
    conn.commit()
    conn.close()
def criar_tabela_empresas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE,
            razao_social TEXT,
            endereco TEXT,
            telefone TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()
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
