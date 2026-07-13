from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse

# Usuário exclusivo da aplicação e senha tratada
USUARIO = "unoesc_app"
SENHA = urllib.parse.quote_plus("Unoesc@2026")
HOST = "localhost"
PORTA = "3306"
BANCO = "unoesc_db"

# string de conexão segura
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{BANCO}"

# motor que vai gerenciar a conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criar as tabelas
Base = declarative_base()