from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
import app.models as models

# Ollama local (modelo phi3)
llm = OllamaLLM(model="phi3")

# Prompt de regras (RF02)
template_prompt = """Você é um assistente acadêmico rigoroso da Unoesc.
Siga ESTAS TRÊS REGRAS de forma inegociável:
1. Responda baseando-se ÚNICA E EXCLUSIVAMENTE nas informações listadas abaixo.
2. Seja extremamente direto, curto e objetivo. Não dê explicações extras.
3. Se a resposta para a pergunta NÃO estiver no texto abaixo, é ESTRITAMENTE PROIBIDO inventar informações ou dar dicas. Você deve responder EXATAMENTE e APENAS com a frase: "Desculpe, não encontrei informações oficiais sobre este assunto na minha base."

Informações (Base de Conhecimento):
{contexto}

Pergunta do Aluno:
{pergunta}

Resposta:"""

prompt = PromptTemplate(
    input_variables=["contexto", "pergunta"],
    template=template_prompt
)

# Função principal de acionagem da API
def gerar_resposta(pergunta_aluno: str, db: Session):
    # Consulta o banco de dados (pega todas as regras da base_conhecimento)
    regras_db = db.query(models.BaseConhecimento).all()
    
    # Junta os títulos e conteúdos em um texto só
    textos = []
    for regra in regras_db:
        textos.append(f"Regra: {regra.titulo} - {regra.conteudo}")
    
    contexto_agrupado = "\n".join(textos)
    
    # Preenche com as regras do banco e a pergunta do aluno
    texto_pronto_para_ia = prompt.format(contexto=contexto_agrupado, pergunta=pergunta_aluno)
    
    resposta_ia = llm.invoke(texto_pronto_para_ia)
    return resposta_ia