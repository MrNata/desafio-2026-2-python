# IMPORTAÇÃO DAS BIBLIOTECAS

# Modelo LLM executado localmente através do Ollama
from langchain_ollama import OllamaLLM

# Responsável pela criação de prompts parametrizados
from langchain_core.prompts import PromptTemplate

# Sessão do banco de dados
from sqlalchemy.orm import Session


# INICIALIZAÇÃO DO MODELO
# O sistema utiliza o modelo Phi-3 executando localmente
# através do Ollama.

# Vantagens:
# Não depende de APIs externas.
# Não gera custo por requisição.
# Mantém os dados dentro da infraestrutura local.

llm = OllamaLLM(model="phi3")

# TEMPLATE DO PROMPT
# Este prompt define o comportamento padrão da IA.
# Restringindo as respostas somente às informações
# existentes na Base de Conhecimento.
template_prompt = """
Você é um assistente acadêmico rigoroso da Unoesc.
Siga ESTAS TRÊS REGRAS de forma inegociável:
1. Responda baseando-se ÚNICA E EXCLUSIVAMENTE nas informações listadas abaixo.
2. Seja extremamente direto, curto e objetivo.
3. Caso a resposta NÃO esteja presente na base de conhecimento,
é ESTRITAMENTE PROIBIDO inventar informações.

Você deve responder exatamente:
"Desculpe, não encontrei informações oficiais sobre este assunto na minha base."

Informações (Base de Conhecimento):

{contexto}
Pergunta do aluno:

{pergunta}
Resposta:
"""


# PROMPT TEMPLATE
# Substitui automaticamente:
# {contexto}
# {pergunta}
# pelos valores enviados durante a execução.

prompt = PromptTemplate(
    input_variables=[
        "contexto",
        "pergunta"
    ],
    template=template_prompt
)


# GERAÇÃO DA RESPOSTA
# Fluxo:
# 1. Consulta a Base de Conhecimento.
# 2. Junta todas as informações.
# 3. Monta o Prompt.
# 4. Envia para o modelo Phi-3.
# 5. Retorna a resposta gerada.

def gerar_resposta(
    pergunta_estudante: str,
    db: Session
):

    # Importação realizada aqui para evitar
    # dependência circular entre módulos.
    import app.models as models

    # CONSULTA À BASE DE CONHECIMENTO
    regras_db = (
        db.query(models.BaseConhecimento)
        .all()

    )

    # MONTAGEM DO CONTEXTO
    # Todos os documentos são agrupados
    # em um único texto.
    # Esse texto será utilizado como contexto
    # para a IA responder.
    textos = []
    for regra in regras_db:
        textos.append(
            f"Regra: {regra.titulo} - {regra.conteudo}"
        )
    contexto_agrupado = "\n".join(textos)

    # MONTAGEM DO PROMPT FINAL
    # O PromptTemplate substitui automaticamente:
    # {contexto}
    # {pergunta}
    texto_para_ia = prompt.format(
        contexto=contexto_agrupado,
        pergunta=pergunta_estudante
    )

    # EXECUÇÃO DO MODELO
    # O Prompt é enviado ao modelo Phi-3
    # executado localmente no Ollama.
    resposta_ia = llm.invoke(
        texto_para_ia
    )
    return resposta_ia