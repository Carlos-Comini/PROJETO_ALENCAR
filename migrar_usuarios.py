import sqlite3
from sqlalchemy import text
from config import engine

# Caminho do banco SQLite antigo
sqlite_conn = sqlite3.connect('usuarios.db')
sqlite_cursor = sqlite_conn.cursor()

# Migração dos usuários
for row in sqlite_cursor.execute("SELECT nome, email, senha, tipo, cadastrar, ver_arquivo, ver_xml FROM usuarios"):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO usuarios (nome, email, senha, tipo, cadastrar, ver_arquivo, ver_xml)
                VALUES (:nome, :email, :senha, :tipo, :cadastrar, :ver_arquivo, :ver_xml)
                ON CONFLICT (email) DO NOTHING
            """),
            {
                "nome": row[0],
                "email": row[1],
                "senha": row[2],
                "tipo": row[3],
                "cadastrar": bool(row[4]),
                "ver_arquivo": bool(row[5]),
                "ver_xml": bool(row[6])
            }
        )

sqlite_conn.close()
print("Migração concluída!")