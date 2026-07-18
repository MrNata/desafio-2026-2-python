// CONFIGURAÇÃO DA API
// Endereço base do servidor FastAPI.
const API_URL = "http://localhost:8000";

// VARIÁVEIS GLOBAIS

// tokenGlobal
// Armazena o Token JWT após o login.
// codigoAcessoGlobal
// Armazena o código do usuário autenticado.

let tokenGlobal = "";
let codigoAcessoGlobal = "";


// ALTERNÂNCIA DE TELAS
// Exibe uma tela e oculta outra utilizando a classe "hidden".

function alternarTela(mostrar, esconder) {
    document.getElementById(esconder).classList.add("hidden");
    document.getElementById(mostrar).classList.remove("hidden");
}


// EVENTO DE INICIALIZAÇÃO

// Aguarda todo o HTML ser carregado antes de registrar
// os eventos da página.
// Permite que o usuário envie perguntas pressionando ENTER.

document.addEventListener("DOMContentLoaded", () => {
    const inputPergunta = document.getElementById("pergunta-input");
    if (inputPergunta) {
        inputPergunta.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                enviarPergunta();
            }
        });
    }
});


// CADASTRO DE USUÁRIO

// Fluxo:
// 1. Captura os dados do formulário.
// 2. Envia para a API.
// 3. Caso sucesso:
//   Exibe o código de acesso.
//   Mostra o modal.
//   Preenche automaticamente o login.

async function fazerCadastro() {
    const nome = document.getElementById("reg-nome").value;
    const apelido = document.getElementById("reg-apelido").value;
    const email = document.getElementById("reg-email").value;
    const senha = document.getElementById("reg-senha").value;
    const response = await fetch(`${API_URL}/registrar`, {

        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            nome,
            apelido,
            email,
            senha
        })
    });

    const data = await response.json();
    if (response.ok) {
        // Exibe o código de acesso gerado
        document.getElementById("modal-codigo-acesso").innerText = data.codigo_acesso;

        // Exibe o modal de SUCESSO
        const modalSucesso = document.getElementById("sucesso-modal");
        modalSucesso.classList.remove("hidden");
        modalSucesso.style.display = "flex";

        // Preenche automaticamente o campo de login
        document.getElementById("login-codigo").value = data.codigo_acesso;
    }

    else {
        alert("Erro: " + data.detail);
    }
}


// FECHAMENTO DO MODAL

// Após visualizar o código,
// retorna automaticamente para a tela de login.
function fecharModalSucesso() {
    const modalSucesso = document.getElementById("sucesso-modal");
    modalSucesso.classList.add("hidden");
    modalSucesso.style.display = "none"; // Garante que o modal suma completamente

    alternarTela("login-form", "register-form");

    // Limpa o formulário de cadastro
    document.getElementById("reg-nome").value = "";
    document.getElementById("reg-apelido").value = "";
    document.getElementById("reg-email").value = "";
    document.getElementById("reg-senha").value = "";
    
    // Posiciona o cursor no login
    document.getElementById("login-codigo").focus();
}


// LOGIN

// Fluxo:
// 1. Recebe código e senha.
// 2. Envia para FastAPI.
// 3. Recebe o Token JWT.
// 4. Libera acesso ao Chat.

async function fazerLogin() {
    const codigo = document.getElementById("login-codigo").value;
    const senha = document.getElementById("login-senha").value;
    const params = new URLSearchParams();
    params.append("username", codigo);
    params.append("password", senha);
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        body: params
    });

    const data = await response.json();
    if (response.ok) {

        // Token utilizado nas próximas requisições
        tokenGlobal = data.access_token;

        // Código do usuário autenticado
        codigoAcessoGlobal = codigo;

        // Esconde tela de login
        document.getElementById("auth-screen").classList.add("hidden");

        // Exibe tela do chat
        document.getElementById("chat-screen").classList.remove("hidden");
        
        // CORREÇÃO: Removido o 'carregarEstatisticas()' que estava aqui fazendo o painel abrir sozinho.
    }

    else {
        alert("Erro: Código ou senha incorretos.");
    }
}


// ENVIO DA PERGUNTA PARA A IA

// Fluxo:

// 1. Captura a pergunta digitada.
// 2. Exibe imediatamente na tela.
// 3. Mostra animação "Digitando...".
// 4. Envia a pergunta para a API.
// 5. Recebe a resposta.
// 6. Remove a animação.
// 7. Exibe a resposta da IA.

async function enviarPergunta() {
    const inputElement = document.getElementById("pergunta-input");
    const pergunta = inputElement.value.trim();

    // Impede envio de perguntas vazias
    if (!pergunta) return;

    // Exibe a pergunta do usuário
    adicionarMensagemNaTela(pergunta, "user");
    inputElement.value = "";

    const loadingId = mostrarCarregando();
    try {

        const response = await fetch(`${API_URL}/perguntar`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${tokenGlobal}`
            },

            body: JSON.stringify({
                codigo_acesso: codigoAcessoGlobal,
                pergunta: pergunta
            })
        });

        const data = await response.json();
        removerCarregando(loadingId);
        if (response.ok) {
            adicionarMensagemNaTela(
                data.resposta,
                "ia"
            );
        }

        else {
            alert("Erro ao enviar pergunta. Sua sessão pode ter expirado.");
            sair();
        }
    }

    catch (error) {
        removerCarregando(loadingId);
        adicionarMensagemNaTela(
            "Erro de conexão. O servidor parece estar offline.",
            "ia"
        );
    }
}

function adicionarMensagemNaTela(texto, quem) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `msg ${quem}`;
    div.innerText = texto;
    chatBox.appendChild(div);
    // Mantém a conversa sempre no final
    chatBox.scrollTop = chatBox.scrollHeight;

}


function mostrarCarregando() {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    const id = "loading-" + Date.now();
    div.id = id;
    div.className = "msg ia typing";
    div.innerHTML =
        "Digitando<span>.</span><span>.</span><span>.</span>";
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removerCarregando(id) {
    const div = document.getElementById(id);
    if (div) {
        div.remove();
    }
}


// ENCERRAMENTO DA SESSÃO
// Limpa os dados do usuário e retorna
// para a tela inicial.

function sair() {
    tokenGlobal = "";
    codigoAcessoGlobal = "";
    document.getElementById("chat-screen").classList.add("hidden");
    document.getElementById("auth-screen").classList.remove("hidden");
    document.getElementById("chat-box").innerHTML = "";
}

// RELATÓRIO
async function carregarEstatisticas() {
    const token = tokenGlobal || localStorage.getItem("token_jwt");
    if (!token) {
        console.error("Nenhum token encontrado.");
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/estatisticas`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (response.ok) {
            const json = await response.json();
            const dados = json.dados;

            document.getElementById("stat-alunos").innerText = dados.total_alunos_cadastrados;
            document.getElementById("stat-perguntas").innerText = dados.total_perguntas_respondidas;
            document.getElementById("stat-tempo").innerText = dados.tempo_medio_resposta_segundos + "s";
            
            // Exibe o modal na tela
            document.getElementById("modal-relatorio").style.display = "flex"; 
        } else {
            console.error("A API não retornou sucesso. Status:", response.status);
        }
    } catch (error) {
        console.error("Erro de conexão:", error);
    }
}

function fecharRelatorio() {
    document.getElementById("modal-relatorio").style.display = "none";
}