from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database import Base
import datetime

# Tabela da Base de Conhecimento (RF02)
class BaseConhecimento(Base):
    __tablename__ = "base_conhecimento"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255))
    conteudo = Column(Text)
    categoria = Column(String(100))

# Tabela de Histórico/Logs (RF05)
class HistoricoLog(Base):
    __tablename__ = "historico"
    
    id = Column(Integer, primary_key=True, index=True)
    codigoAluno = Column(Integer, index=True)
    pergunta = Column(Text)
    resposta = Column(Text)
    data = Column(DateTime, default=datetime.datetime.utcnow)
    tempoProcessamento = Column(Float)

# Tabela de Usuários para o JWT (RF07 Segurança)
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    senha_hash = Column(String(255)) # senha criptografada