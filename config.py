import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:RxMax9098@localhost:5432/projetoalencar"
)
engine = create_engine(DATABASE_URL)