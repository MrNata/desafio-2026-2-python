
# IMPORTAÇÃO DAS BIBLIOTECAS

# Responsáveis por:
# Ler as variáveis de ambiente (.env)
# Criar a conexão com o banco de dados MySQL
# Gerenciar sessões do SQLAlchemy
# Criar a classe Base utilizada pelos Models

import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE

# Carrega automaticamente as configurações armazenadas
# no arquivo ".env", evitando que informações sensíveis,
# como usuário e senha do banco, fiquem expostas no código.
load_dotenv()



# CONFIGURAÇÃO DA URL DE CONEXÃO
# Monta dinamicamente a URL utilizada pelo SQLAlchemy
# para estabelecer conexão com o banco de dados MySQL.

# As informações são obtidas através das variáveis
# de ambiente:
# DB_USER
# DB_PASS
# DB_HOST
# DB_NAME

# Utilizar variáveis de ambiente aumenta a segurança,
# pois evita expor credenciais diretamente no código.

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")

)
# ENGINE (MOTOR DE CONEXÃO)

# Cria o mecanismo responsável por abrir a comunicação
# entre a aplicação FastAPI e o banco de dados MySQL.

# O Engine não executa consultas diretamente.
# Ele gerencia toda a infraestrutura de conexão.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# SESSION FACTORY
# Responsável por criar sessões de comunicação
# com o banco de dados.
# Cada requisição da aplicação utiliza uma sessão,
# que é aberta no início da operação e encerrada
# automaticamente ao final.
#
# Configurações:
# autocommit=False
# As alterações somente são gravadas após db.commit().

# autoflush=False
# Evita sincronizações automáticas antes das consultas,
# proporcionando maior controle sobre as operações.

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# CLASSE BASE DOS MODELS
# Todos os Models do projeto herdam desta classe.
# Exemplo:
# class Usuario(Base):

# O SQLAlchemy utiliza esta classe para identificar
# todas as tabelas da aplicação e realizar o
# mapeamento objeto-relacional (ORM).

# Graças ao Base, é possível representar tabelas do
# banco como classes Python, tornando o código mais
# organizado e intuitivo.
Base = declarative_base()