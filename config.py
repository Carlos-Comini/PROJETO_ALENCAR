import os
from sqlalchemy import create_engine

# Busca a variável de ambiente DATABASE_URL (usada no Streamlit Cloud)
# Se não existir, usa o banco local como padrão
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:RxMax9098@localhost:5432/projeto_alencar"
)
engine = create_engine(DATABASE_URL)