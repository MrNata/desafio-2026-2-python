from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
import app.ia as ia

# arquivos locais
import app.models as models
from app.database import engine, SessionLocal
import app.security as security

# Cria as tabelas se não existirem
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem testes locais
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROTAS DE SEGURANÇA (RF07)

class UsuarioCreate(BaseModel):
    username: str
    senha: str

@app.post("/registrar")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o usuário já existe no banco
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já registrado")
    
    # 2. Embaralhar a senha
    senha_criptografada = security.gerar_hash_senha(usuario.senha)
    
    # 3. Salva no banco de dados com a senha segura
    novo_usuario = models.Usuario(username=usuario.username, senha_hash=senha_criptografada)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return {"mensagem": f"Usuário '{usuario.username}' criado com sucesso!"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Procura o usuário no banco
    user = db.query(models.Usuario).filter(models.Usuario.username == form_data.username).first()
    
    # 2. Verifica se o usuário existe E se a senha bate com o Hash
    if not user or not security.verificar_senha(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Gera o Token
    token_jwt = security.criar_token_acesso(dados={"sub": user.username})
    
    return {"access_token": token_jwt, "token_type": "bearer"}

# ROTAS DA APLICAÇÃO (RF01)

class PerguntaRequest(BaseModel):
    codigoAluno: int
    pergunta: str

@app.post("/perguntar")
async def perguntar(
    request: PerguntaRequest, 
    usuario_logado: str = Depends(security.obter_usuario_atual),
    db: Session = Depends(get_db)
):
    # Inicia o cronômetro
    inicio = time.time()
    
    # Manda a pergunta para o LangChain/Ollama
    resposta_da_ia = ia.gerar_resposta(request.pergunta, db)
    
    # Para o cronômetro e calcula o tempo total
    fim = time.time()
    tempo_total = fim - inicio
    
    # Salva o registro completo na tabela de Histórico (RF05)
    novo_log = models.HistoricoLog(
        codigoAluno=request.codigoAluno,
        pergunta=request.pergunta,
        resposta=resposta_da_ia,
        tempoProcessamento=tempo_total
    )
    db.add(novo_log)
    db.commit()
    
    # Retorna resposta para o estudante
    return {
        "status": "sucesso",
        "aluno": request.codigoAluno,
        "resposta": resposta_da_ia,
        "tempo_segundos": round(tempo_total, 2)
    }

@app.get("/historico")
async def consultar_historico(
    skip: int = 0, 
    limit: int = 10, 
    usuario_logado: str = Depends(security.obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Retorna o histórico de perguntas de forma paginada.
    - skip: Quantos registros pular (OFFSET)
    - limit: Quantos registros trazer (LIMIT)
    """
    
    # Mais recentes primeiro)
    registros = (
        db.query(models.HistoricoLog)
        .order_by(models.HistoricoLog.data.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Conta o total de registros no banco
    total = db.query(models.HistoricoLog).count()
    
    # Calcula qual é a página atual
    pagina_atual = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "status": "sucesso",
        "total_registros": total,
        "registros_retornados": len(registros),
        "pagina_atual": pagina_atual,
        "dados": registros
    }