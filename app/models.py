
# IMPORTAÇÃO DAS BIBLIOTECAS
# Tipos de dados utilizados na criação das tabelas
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean
)
from sqlalchemy.sql import func
# Classe base utilizada pelo SQLAlchemy
from app.database import Base


# TABELA: BASE DE CONHECIMENTO (RF02)
# Armazena todas as informações oficiais utilizadas pela IA
# para responder às perguntas dos estudantes.
# Cada registro representa uma regra cadastrada.


class BaseConhecimento(Base):
    __tablename__ = "base_conhecimento"
    __table_args__ = {
        "extend_existing": True
    }
    # Identificador único
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    # Título do documento
    titulo = Column(
        String(255)
    )
    # Conteúdo completo utilizado pela IA
    conteudo = Column(
        Text
    )

    # Categoria do documento
    categoria = Column(
        String(100)
    )



# TABELA: HISTÓRICO (RF05)
# Armazena todas as interações realizadas pelos usuários.
# Essas informações são utilizadas para:
# Auditoria
# Consulta do histórico
# Estatísticas
# Tempo médio de resposta


class HistoricoLog(Base):
    __tablename__ = "historico"
    __table_args__ = {
        "extend_existing": True
    }

    # Identificador do registro
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Código do aluno que realizou a pergunta
    codigo_acesso = Column(
        String(20),
        index=True
    )

    # Pergunta enviada
    pergunta = Column(
        Text
    )

    # Resposta retornada pela IA
    resposta = Column(
        Text
    )

    # Data e horário automáticos
    data = Column(
        DateTime,
        default=func.now()
    )

    # Tempo utilizado pela IA para responder
    tempoProcessamento = Column(
        Float
    )


# TABELA: USUÁRIOS (RF07)
# Responsável por armazenar todos os usuários do sistema.
# Também controla quais usuários possuem privilégios admin.

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {
        "extend_existing": True
    }

    # Identificador interno
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Código utilizado para login
    codigo_acesso = Column(
        String(50),
        unique=True,
        index=True
    )

    # Nome completo
    nome = Column(
        String(100)
    )

    # Nome utilizado pela IA durante a conversa
    apelido = Column(
        String(50)
    )

    # E-mail único
    email = Column(
        String(150),
        unique=True,
        index=True
    )

    # Senha criptografada
    senha_hash = Column(
        String(255)
    )

    # Define se o usuário possui permissões admin
    admin = Column(
        Boolean,
        default=False
    )