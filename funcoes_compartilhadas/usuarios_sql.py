import sqlite3
from typing import Optional, Dict

DB_PATH = 'usuarios.db'

def conectar():
    return sqlite3.connect(DB_PATH)

def autenticar(email: str, senha: str) -> Optional[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM usuarios WHERE email=? AND senha=?
    """, (email, senha))
    row = cursor.fetchone()
    conn.close()
    if row:
        colunas = [desc[0] for desc in cursor.description]
        return dict(zip(colunas, row))
    return None

def buscar_por_id(user_id: int) -> Optional[Dict]:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        colunas = [desc[0] for desc in cursor.description]
        return dict(zip(colunas, row))
    return None

def listar_usuarios() -> list:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(colunas, row)) for row in rows]
