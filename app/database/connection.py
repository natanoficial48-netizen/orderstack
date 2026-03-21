"""
Configuração de conexão com o banco de dados.

Aqui definimos:
- URL do banco
- Engine de conexão
- Sessão do banco
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL do banco (SQLite para desenvolvimento)
DATABASE_URL = "sqlite:///./burger.db"

# Cria a conexão com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Cria sessões de acesso ao banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)