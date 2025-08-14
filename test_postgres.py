from sqlalchemy import create_engine, text
from funcoes_compartilhadas.usuarios_sql import inserir_usuario, listar_usuarios

# Substitua pelos seus dados de acesso
usuario = "postgres"
senha = "RxMax9098"  # ou a senha simples que você definiu no ALTER USER
host = "localhost"
porta = "5432"
banco = "projeto_alencar"

# String de conexão
DATABASE_URL = f"postgresql://{usuario}:{senha}@{host}:{porta}/{banco}"

# Cria o engine
engine = create_engine(DATABASE_URL)

# Testa a conexão e faz uma consulta simples
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM usuarios"))
    for row in result:
        print(row)

inserir_usuario("joao", "joao@alencar.com", "123456", "Cliente", False, True, True)
usuarios = listar_usuarios()
print(usuarios)