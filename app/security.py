import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 1. Configurando o encoder de senhas (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Função para verificar se a senha digitada bate com o Hash do banco
def verificar_senha(senha_pura, senha_hash):
    return pwd_context.verify(senha_pura, senha_hash)

# 3. Função para transformar a senha Hash antes de salvar no banco
def gerar_hash_senha(senha):
    return pwd_context.hash(senha)

# 4. Função para gerar Token JWT
def criar_token_acesso(dados: dict):
    dados_para_codificar = dados.copy()
    
    # Calcula a hora que o token vence
    expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_para_codificar.update({"exp": expiracao})
    
    # Token criptografado
    token_jwt = jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 5. Função para validar o token
def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Crachá inválido")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Crachá vencido. Faça login novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Crachá falsificado ou inválido.")