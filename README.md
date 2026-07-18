# API Assistente Acadêmico - Desafio Unoesc

Esta é uma API desenvolvida em Python (FastAPI) para atuar como assistente virtual acadêmico, acompanhada de uma interface gráfica web completa. O sistema utiliza a arquitetura RAG (Retrieval-Augmented Generation) com o modelo de linguagem Phi-3 executado localmente via Ollama, garantindo a segurança e privacidade dos dados institucionais.

## Requisitos Atendidos

* **RF01:** Endpoint `POST /perguntar` recebendo JSON com `codigo_acesso` e `pergunta`.
* **RF02 & RF03:** Respostas geradas estritamente com base nos dados cadastrados no banco de dados. A IA foi instruída a recusar perguntas fora do escopo acadêmico fornecido.
* **RF05:** Registro de log de todas as interações na tabela `historico`, incluindo o tempo de processamento da IA.
* **RF07:** Proteção de todos os endpoints de consulta via autenticação JWT (JSON Web Token). Armazenamento de senhas utilizando hash seguro (Bcrypt).
* **Diferenciais Adicionais:** 
  * Processamento de IA 100% local (offline), eliminando custos e dependência de APIs externas de terceiros.
  * Endpoint adicional `GET /estatisticas` e Painel Web para visualização de métricas (total de alunos, perguntas respondidas e tempo médio de resposta).
  * Interface Gráfica interativa (HTML/CSS/JS) pronta para uso.

## Tecnologias Utilizadas

* **Framework:** FastAPI / Uvicorn
* **Banco de Dados:** MySQL 8.0
* **ORM:** SQLAlchemy
* **Segurança:** PyJWT, Passlib (Bcrypt)
* **Inteligência Artificial:** LangChain, Ollama (Modelo Phi-3)
* **Front-end:** HTML5, CSS3, Vanilla JavaScript

---

## Configuração do Ambiente

### 1. Banco de Dados (MySQL)
Para seguir as boas práticas de privilégio mínimo, a API utiliza um usuário dedicado em vez do root. 

Acesse o seu gerenciador do MySQL e execute o script abaixo:

```sql
-- Criação do banco de dados
CREATE DATABASE unoesc_db;

-- Criação do usuário dedicado e permissões
CREATE USER 'unoesc_app'@'localhost' IDENTIFIED BY 'Unoesc@2026';
GRANT ALL PRIVILEGES ON unoesc_db.* TO 'unoesc_app'@'localhost';
FLUSH PRIVILEGES;
```

*(Obs: As tabelas `base_conhecimento`, `historico` e `usuarios` serão criadas automaticamente pelo SQLAlchemy na primeira execução da API).*

Após a API iniciar e gerar as tabelas, execute os inserts abaixo para alimentar a base de conhecimento com as regras acadêmicas:

```sql
USE unoesc_db;

INSERT INTO base_conhecimento (titulo, conteudo, categoria) VALUES 
('Como fazer a rematrícula', 'A rematrícula deve ser realizada pelo Espaço Acadêmico, acessando a opção Matrícula/Rematrícula. Antes de iniciar o processo, verifique se o período de rematrícula está aberto, pois essa opção fica disponível apenas durante as datas estabelecidas pela instituição.', 'SAE'),
('Como retirar atesdado de regularidade e frequência', 'Para solicitar um atestado, acesse o Espaço Acadêmico e, no menu Serviços on-line, selecione o curso desejado. Em seguida, clique em Nova solicitação, escolha o tipo de atestado que deseja emitir e siga as instruções exibidas na tela.', 'SAE'),
('Onde atualizar meus dados pessoais', 'Para atualizar seus dados cadastrais, acesse seu nome no canto superior direito da tela e clique sobre ele. Em seguida, selecione a opção "Dados pessoais". Nessa área, você poderá visualizar e atualizar as informações do seu cadastro.', 'SAE');
```

### 2. Configuração do Ollama
1. Baixe e instale o Ollama através do site oficial: [ollama.com](https://ollama.com).
2. No terminal do sistema operacional, faça o download do modelo Phi-3:
   ```bash
   ollama run phi3
   ```
3. O serviço do Ollama deve permanecer rodando em segundo plano (porta padrão `11434`).

### 3. Instalação das Dependências do Python
Com o seu ambiente virtual (`.venv`) ativo no terminal, execute o comando de instalação:

```bash
pip install fastapi uvicorn sqlalchemy pymysql passlib bcrypt==4.0.1 PyJWT python-multipart langchain langchain-community langchain-core
```

---

## Como Executar a API

Na raiz do projeto (`projeto-unoesc`), inicie o servidor:

```bash
uvicorn
```

A API estará ativa em `http://127.0.0.1:8000`.

---

## Fluxo de Testes (Swagger)

Acesse a documentação interativa da API em: **`http://127.0.0.1:8000/docs`**

1. **Criar Usuário:** Acesse a rota `POST /registrar` e crie as credenciais que deseja utilizar para os testes.
2. **Autenticação (Login):** Clique no botão **Authorize** (ícone de cadeado no topo direito da tela), preencha o formulário com o usuário e senha criados. O Swagger irá gerenciar e injetar o token JWT gerado nas próximas requisições de forma automática.
3. **Enviar Pergunta:** Com o acesso autorizado, envie uma requisição para a rota protegida `POST /perguntar` utilizando o formato JSON abaixo:

```json
{
  "codigoAluno": 1,
  "pergunta": "Como realizar a rematrícula?"
}
```

4. **Verificação de Performance e Logs:** A resposta será entregue contendo a informação extraída da base e o tempo de execução em segundos. O registro completo dessa transação será salvo na tabela `historico` do banco de dados.

> **Nota de infraestrutura:** Como o processamento do modelo de IA ocorre localmente via CPU em ambiente de desenvolvimento, o tempo de resposta inicial pode variar entre 15 e 25 segundos dependendo do hardware. Em ambiente de produção com suporte a GPU dedicadas, este tempo cai para cerca de 2 segundos.