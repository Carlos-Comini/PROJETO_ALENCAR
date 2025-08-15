# Cria tabela de associação N para N entre usuários e empresas
def criar_tabela_usuarios_empresas():
    import os
    import sqlite3
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'usuarios.db')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_empresas (
            id_usuario INTEGER,
            id_empresa INTEGER,
            PRIMARY KEY (id_usuario, id_empresa)
        )
    ''')
    conn.commit()
    conn.close()
import sqlite3
import os
from typing import Optional, Dict
from sqlalchemy import text
from config import engine

# Caminho absoluto do banco na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'usuarios.db')

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        empresa TEXT,
        cadastrar TEXT,
        ver_arquivo TEXT,
        ver_xml TEXT
    )''')
    return conn

def inserir_usuario(nome, email, senha, tipo, cadastrar, ver_arquivo, ver_xml):
    with engine.begin() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM usuarios WHERE email = :email"),
            {"email": email}
        ).first()
        if existe:
            print(f"Usuário com e-mail {email} já existe.")
            return
        conn.execute(
            text("""
                INSERT INTO usuarios (nome, email, senha, tipo, cadastrar, ver_arquivo, ver_xml)
                VALUES (:nome, :email, :senha, :tipo, :cadastrar, :ver_arquivo, :ver_xml)
            """),
            {
                "nome": nome,
                "email": email,
                "senha": senha,
                "tipo": tipo,
                "cadastrar": cadastrar,
                "ver_arquivo": ver_arquivo,
                "ver_xml": ver_xml
            }
        )

def autenticar(email: str, senha: str) -> Optional[Dict]:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM usuarios WHERE email = :email AND senha = :senha"),
            {"email": email, "senha": senha}
        ).mappings().first()
        return dict(result) if result else None

def buscar_por_id(user_id: int) -> Optional[Dict]:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM usuarios WHERE id = :id"),
            {"id": user_id}
        ).mappings().first()
        return dict(result) if result else None

def listar_usuarios():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM usuarios"))
        return [dict(row) for row in result.mappings()]

def registrar_usuario_padrao():
    # Registra o usuário ELIANE se não existir
    email = "eliane@alencarassociados.com.br"
    with engine.begin() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM usuarios WHERE email = :email"),
            {"email": email}
        ).first()
        if not existe:
            conn.execute(
                text("""
                    INSERT INTO usuarios (nome, email, senha, tipo, empresa, cadastrar, ver_arquivo, ver_xml)
                    VALUES (:nome, :email, :senha, :tipo, :empresa, :cadastrar, :ver_arquivo, :ver_xml)
                """),
                {
                    "nome": "ELIANE",
                    "email": email,
                    "senha": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
                    "tipo": "Escritorio",
                    "empresa": None,
                    "cadastrar": "Sim",
                    "ver_arquivo": "Sim",
                    "ver_xml": "Sim"
                }
            )
