# IMPORTAÇÃO DAS BIBLIOTECAS
# Middleware responsável por permitir comunicação entre Front-end e API
from fastapi.middleware.cors import CORSMiddleware

# Recursos principais do FastAPI
from fastapi import FastAPI, Depends, HTTPException, status

# Recursos de autenticação OAuth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Sessão do SQLAlchemy para comunicação com o banco de dados
from sqlalchemy.orm import Session

# Validação automática dos dados recebidos pela API
from pydantic import BaseModel

# Bibliotecas auxiliares
import time
import random
import string

# Arquivo responsável pela Inteligência Artificial
import app.ia as ia

# Funções SQL utilizadas para cálculos (AVG, COUNT, etc.)
from sqlalchemy import func

import app.models as models
from app.database import engine, SessionLocal
import app.security as security

# CRIAÇÃO AUTOMÁTICA DAS TABELAS
# Caso o banco ainda não possua as tabelas definidas nos Models,
# elas serão criadas automaticamente durante a inicialização.

models.Base.metadata.create_all(bind=engine)

# INICIALIZAÇÃO DA API
app = FastAPI()


# CONEXÃO COM O BANCO
# Esta função cria uma sessão com o banco de dados para cada
# requisição realizada.
# O FastAPI fecha automaticamente essa conexão ao final da
# execução utilizando o bloco "finally".

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CONFIGURAÇÃO DO CORS
# Permite que aplicações externas (Front-end) possam realizar
# requisições para esta API, liberado para qualquer origem,
# facilitando testes durante o desenvolvimento.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MODELOS DE ENTRADA (Pydantic)
# Os modelos abaixo validam automaticamente os dados enviados
# pelo Front-end antes de chegar à lógica da aplicação.

class UsuarioCreate(BaseModel):
    nome: str
    apelido: str
    email: str
    senha: str


class PerguntaRequest(BaseModel):
    codigo_acesso: str
    pergunta: str


# RF07 - CADASTRO DE USUÁRIO

# Fluxo da funcionalidade:
# 1 - Verifica se o e-mail já existe.
# 2 - Obtém o último usuário cadastrado.
# 3 - Gera um novo código de acesso sequencial.
# 4 - Criptografa a senha.
# 5 - Salva o usuário no banco.

@app.post("/registrar")
def registrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):

# Verifica se já existe um usuário utilizando este e-mail.
    db_user = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == usuario.email)
        .first()
    )

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

# Busca o último usuário cadastrado.
    ultimo_usuario = (
        db.query(models.Usuario)
        .order_by(models.Usuario.id.desc())
        .first()
    )

    # Gera um código de acesso sequencial.
    # Exemplo:
    # Usuário anterior = 15
    # Novo usuário = 16
    if (
        ultimo_usuario
        and
        ultimo_usuario.codigo_acesso.isdigit()
    ):
        novo_numero = int(
            ultimo_usuario.codigo_acesso
        ) + 1

    else:
        novo_numero = 1
    novo_codigo = str(novo_numero)

    # Cria o novo usuário utilizando a senha criptografada.
    novo_usuario = models.Usuario(
        nome=usuario.nome,
        apelido=usuario.apelido,
        email=usuario.email,
        senha_hash=security.gerar_hash_senha(
            usuario.senha
        ),
        codigo_acesso=novo_codigo
    )

    # Persiste os dados no banco.
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {
        "mensagem": "Usuário criado com sucesso",
        "codigo_acesso": novo_codigo
    }


# LOGIN
# O usuário informa:
# Código de acesso
# Senha
# Caso estejam corretos,
# um Token JWT é gerado para autenticação das próximas
# requisições.
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Localiza o usuário através do código informado.
    user = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.codigo_acesso ==
            form_data.username
        )
        .first()
    )

    # Validação das credenciais.
    if (
        not user
        or
        not security.verificar_senha(
            form_data.password,
            user.senha_hash
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de acesso ou senha incorretos",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Geração do Token JWT.
    token_jwt = security.criar_token_acesso(
        dados={
            "sub": user.codigo_acesso
        }
    )

    return {
        "access_token": token_jwt,
        "token_type": "bearer"
    }

# RF01 - CONSULTA À INTELIGÊNCIA ARTIFICIAL
# Fluxo da requisição:
# 1. O usuário envia uma pergunta pelo Front-end.
# 2. O Token JWT é validado automaticamente.
# 3. O sistema verifica se o usuário existe.
# 4. É criado um prompt personalizado.
# 5. A pergunta é enviada para o módulo da IA.
# 6. O tempo de resposta é calculado.
# 7. A pergunta e a resposta são registradas no histórico.
# 8. A resposta é devolvida ao usuário.

@app.post("/perguntar")
async def perguntar(
    # Dados enviados pelo Front-end
    request: PerguntaRequest,
    # Usuário autenticado através do Token JWT
    usuario_logado: str = Depends(security.obter_usuario_atual),
    # Sessão do banco de dados
    db: Session = Depends(get_db)

):

    # Marca o instante inicial para calcular
    # o tempo total de processamento da IA.
    inicio = time.time()
    # Procura o usuário pelo código informado.
    usuario = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.codigo_acesso ==
            request.codigo_acesso
        )
        .first()
    )

    # Caso o usuário não exista,
    # a requisição é interrompida.
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não autorizado ou não existe."
        )
    
    documentos = db.query(models.BaseConhecimento).all()
    texto_base = "\n".join([doc.conteudo for doc in documentos]) if documentos else "Base de conhecimento vazia."

    prompt_personalizado = f"""
Você é o assistente virtual oficial da Unoesc.
Você é educado e prestativo.
Você é formal e toma sempre cuidado para não escrever palavras erradas.
Sempre mantenha a coerência.
Você está conversando com o aluno {usuario.apelido}.

DOCUMENTOS OFICIAIS (BASE DE CONHECIMENTO):
---
{texto_base}
---

INSTRUÇÕES IMPORTANTES:
1. Responda APENAS com base nos documentos que você tem acesso acima.
2. Caso a resposta para a pergunta não esteja nos documentos acima, responda exatamente:

"Poxa, {usuario.apelido}, não encontrei essa informação nos meus documentos oficiais. Por favor, entre em contato com a Secretaria Acadêmica da Unoesc."

3. Nunca invente procedimentos, horários ou cursos.
4. Mantenha sempre respostas curtas, objetivas e claras.

Pergunta do aluno:
{request.pergunta}
"""

    # ENVIO PARA O MÓDULO DE IA

    # A lógica da Inteligência Artificial foi separada
    # em outro arquivo (ia.py),
    # deixando o main.py responsável apenas
    # pelo controle da aplicação.

    resposta_da_ia = ia.gerar_resposta(
        prompt_personalizado,
        db
    )

    # CÁLCULO DO TEMPO DE PROCESSAMENTO
    # Utilizado posteriormente
    # para geração das estatísticas.
    fim = time.time()
    tempo_total = fim - inicio

    # REGISTRO DO HISTÓRICO
    # Todas as interações ficam armazenadas,
    # permitindo consultas futuras
    # e geração de relatórios admin.
    novo_log = models.HistoricoLog(
        codigo_acesso=request.codigo_acesso,
        pergunta=request.pergunta,
        resposta=resposta_da_ia,
        tempoProcessamento=tempo_total

    )
    db.add(novo_log)
    db.commit()

    # RETORNO DA API
    return {
        "status": "sucesso",
        "Estudante": request.codigo_acesso,
        "resposta": resposta_da_ia,
        "tempo_segundos": round(
            tempo_total,
            2
        )
    }

# CONSULTA DO HISTÓRICO (RF05)

# Implementada paginação para evitar que todos os registros
# sejam carregados de uma única vez, melhorando o desempenho
# da aplicação.

@app.get("/historico")
async def consultar_historico(
    # Quantidade de registros ignorados
    skip: int = 0,
    # Quantidade máxima de registros retornados
    limit: int = 10,
    # Validação automática do Token JWT
    usuario_logado: str = Depends(
        security.obter_usuario_atual
    ),
    # Conexão com o banco
    db: Session = Depends(get_db)
):

    # Busca os registros mais recentes
    registros = (
        db.query(models.HistoricoLog)
        .order_by(
            models.HistoricoLog.data.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Quantidade total de registros existentes
    total = (
        db.query(models.HistoricoLog)
        .count()
    )

    # Calcula automaticamente a página atual
    pagina_atual = (
        (skip // limit) + 1
        if limit > 0
        else 1
    )

    # Retorno da API
    return {
        "status": "sucesso",
        "total_registros": total,
        "registros_retornados": len(registros),
        "pagina_atual": pagina_atual,
        "dados": registros
    }


# RELATÓRIO ADMIN

@app.get("/estatisticas")
async def obter_estatisticas(

    # Usuário autenticado via Token JWT
    usuario_logado: str = Depends(
        security.obter_usuario_atual
    ),

    # Sessão do banco de dados
    db: Session = Depends(get_db)
):

    # CÁLCULO DAS ESTATÍSTICAS
    # Total de perguntas realizadas
    total_interacoes = (
        db.query(models.HistoricoLog)
        .count()
    )

    # Tempo médio de resposta da IA
    tempo_medio_consulta = (
        db.query(
            func.avg(
                models.HistoricoLog.tempoProcessamento
            )
        )
        .scalar()
    )

    tempo_medio = (
        round(tempo_medio_consulta, 2)
        if tempo_medio_consulta
        else 0.0
    )

    # Total de usuários cadastrados
    total_alunos = (
        db.query(models.Usuario)
        .count()
    )

    # RETORNO DOS INDICADORES
    # Essas informações serão exibidas
    # no painel admin do sistema.
    return {
        "status": "sucesso",
        "dados": {
            "total_alunos_cadastrados": total_alunos,
            "total_perguntas_respondidas": total_interacoes,
            "tempo_medio_resposta_segundos": tempo_medio
        }
    }
