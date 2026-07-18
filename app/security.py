# IMPORTAÇÃO DAS BIBLIOTECAS
# Responsáveis por:
# Leitura das variáveis de ambiente (.env)
# Criptografia de senhas (bcrypt)
# Geração e validação de Tokens JWT
# Autenticação de usuários no FastAPI
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE
# Lê automaticamente o arquivo ".env", onde ficam armazenadas
# informações sensíveis da aplicação, como a chave secreta
# utilizada na assinatura dos Tokens JWT.

load_dotenv()

# CONFIGURAÇÕES DE SEGURANÇA

# SECRET_KEY:
# Chave utilizada para assinar e validar os Tokens JWT.

# ALGORITHM:
# Algoritmo criptográfico utilizado na assinatura do Token.

# ACCESS_TOKEN_EXPIRE_MINUTES:
# Tempo de validade do Token de autenticação.

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# CONFIGURAÇÃO DO BCRYPT
# Define o algoritmo utilizado para criptografar as senhas
# antes do armazenamento no banco de dados.

# Nenhuma senha é salva em texto puro.
# Apenas o Hash criptografado é armazenado.

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# VERIFICAÇÃO DE SENHA
# Compara a senha digitada pelo usuário com o Hash
# armazenado no banco de dados.

# Retorna:
# True  -> senha correta
# False -> senha incorreta


def verificar_senha(senha_pura, senha_hash):

    return pwd_context.verify(
        senha_pura,
        senha_hash
    )



# GERAÇÃO DO HASH DA SENHA
# Antes de salvar uma nova senha no banco,
# ela é transformada em um Hash criptografado.
# Isso garante que mesmo admin do banco
# não consigam visualizar a senha original.

def gerar_hash_senha(senha):
    return pwd_context.hash(senha)



# GERAÇÃO DO TOKEN JWT

# Fluxo:
# 1. Recebe os dados do usuário autenticado.
# 2. Calcula a data de expiração.
# 3. Adiciona o campo "exp".
# 4. Assina digitalmente o Token.
# 5. Retorna o JWT ao cliente.

# O Token é utilizado nas próximas requisições,
# evitando que o usuário precise informar login
# e senha a cada acesso.

def criar_token_acesso(dados: dict):
    dados_para_codificar = dados.copy()

    # Calcula o horário de expiração do Token
    expiracao = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    dados_para_codificar.update({
        "exp": expiracao
    })

    # Assina digitalmente o Token JWT
    token_jwt = jwt.encode(
        dados_para_codificar,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token_jwt

# ESQUEMA DE AUTENTICAÇÃO OAUTH2
# Informa ao FastAPI que o Token JWT será obtido
# através da rota "/login".
# Sempre que uma rota utilizar:
# Depends(obter_usuario_atual)
# o FastAPI automaticamente exigirá um Token Bearer.


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"

)
# VALIDAÇÃO DO TOKEN JWT
# Fluxo:
# 1. Recebe o Token enviado pelo cliente.
# 2. Verifica assinatura e validade.
# 3. Extrai o usuário ("sub").
# 4. Caso tudo esteja correto, retorna o código do usuário autenticado.

# Caso contrário:
# • Token expirado
# • Token inválido
# uma exceção HTTP 401 é lançada.

# Todas as rotas protegidas utilizam esta função,
# garantindo que apenas usuários autenticados
# possam acessar recursos restritos do sistema.

def obter_usuario_atual(
    token: str = Depends(oauth2_scheme)
):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Crachá inválido"
            )

        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Crachá vencido. Faça login novamente."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Crachá falsificado ou inválido."
        )