import sqlite3

DB_PATH = 'usuarios.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
# Cria a tabela se não existir
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
		data_upload TEXT
	)
''')
# Tenta adicionar a coluna tipo_nota
try:
	cursor.execute("ALTER TABLE documentos ADD COLUMN tipo_nota TEXT DEFAULT 'Desconhecido';")
	print('Coluna tipo_nota adicionada com sucesso!')
except sqlite3.OperationalError as e:
	if 'duplicate column name' in str(e):
		print('Coluna tipo_nota já existe.')
	else:
		print('Erro ao adicionar coluna:', e)
conn.commit()
conn.close()
