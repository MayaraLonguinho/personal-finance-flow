// Módulo do Assistente Financeiro
// Responsável por gerenciar a conversa com o Agent

// Adiciona mensagem ao chat
function adicionarMensagem(texto, tipo) {
    const chatContainer = document.getElementById('chat-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${tipo}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = texto;
    
    contentDiv.appendChild(paragraph);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Rola para o final
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Adiciona indicador de carregamento
function adicionarLoading() {
    const chatContainer = document.getElementById('chat-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message loading';
    messageDiv.id = 'loading-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = 'Analisando...';
    
    contentDiv.appendChild(paragraph);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Rola para o final
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove indicador de carregamento
function removerLoading() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Envia pergunta para a API
async function enviarPergunta() {
    const input = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    
    const pergunta = input.value.trim();
    
    // Validação
    if (!pergunta) {
        return;
    }
    
    // Desabilita input e botão
    input.disabled = true;
    btnSend.disabled = true;
    
    // Adiciona mensagem do usuário
    adicionarMensagem(pergunta, 'user');
    
    // Limpa input
    input.value = '';
    
    // Adiciona indicador de carregamento
    adicionarLoading();
    
    try {
        const resposta = await fetch('/api/assistente', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pergunta: pergunta })
        });
        
        const dados = await resposta.json();
        
        // Remove indicador de carregamento
        removerLoading();
        
        if (resposta.ok) {
            // Adiciona resposta do assistente
            adicionarMensagem(dados.resposta, 'assistant');
        } else {
            // Trata erro
            const mensagemErro = dados.resposta || dados.erro || 'Ocorreu um erro ao processar sua pergunta.';
            adicionarMensagem(mensagemErro, 'assistant');
        }
        
    } catch (erro) {
        console.error('Erro ao enviar pergunta:', erro);
        
        // Remove indicador de carregamento
        removerLoading();
        
        // Adiciona mensagem de erro
        adicionarMensagem('Ocorreu um erro ao processar sua pergunta. Tente novamente.', 'assistant');
    } finally {
        // Reabilita input e botão
        input.disabled = false;
        btnSend.disabled = false;
        input.focus();
    }
}

// Envia sugestão
function enviarSugestao(sugestao) {
    const input = document.getElementById('chat-input');
    input.value = sugestao;
    enviarPergunta();
}

function formatarMoedaMeta(valor) {
    return window.PFF.formatarMoeda(valor);
}

async function buscarMetaSidebar() {
    try {
        const resposta = await fetch("/api/meta");

        if (!resposta.ok) {
            if (resposta.status === 404) {
                exibirMetaSidebarVazia();
                return;
            }

            throw new Error("Erro ao buscar meta");
        }

        const meta = await resposta.json();

        if (!meta || !meta.id) {
            exibirMetaSidebarVazia();
            return;
        }

        exibirMetaSidebar(meta);

    } catch (erro) {
        console.error("Erro ao carregar meta da sidebar:", erro);
        exibirMetaSidebarVazia();
    }
}

function exibirMetaSidebar(meta) {
    const valorAtual = Number(meta.valor_atual) || 0;
    const valorMeta = Number(meta.valor_meta) || 0;

    const percentualCalculado = valorMeta > 0
        ? (valorAtual / valorMeta) * 100
        : 0;

    const percentual = Number(
        meta.percentual ?? percentualCalculado
    );

    const percentualBarra = Math.min(
        Math.max(percentual, 0),
        100
    );

    const valorRestante = Math.max(
        Number(meta.valor_restante ?? valorMeta - valorAtual),
        0
    );

    const goalValorAtual = document.getElementById("goal-valor-atual");
    const goalValorMeta = document.getElementById("goal-valor-meta");
    const goalPercentual = document.getElementById("goal-percentual");
    const goalProgressBar = document.getElementById("goal-progress-bar");
    const goalRestante = document.getElementById("goal-restante");

    if (goalValorAtual) {
        goalValorAtual.textContent = formatarMoedaMeta(valorAtual);
    }

    if (goalValorMeta) {
        goalValorMeta.textContent = `de ${formatarMoedaMeta(valorMeta)}`;
    }

    if (goalPercentual) {
        goalPercentual.textContent = `${percentual.toFixed(0)}%`;
    }

    if (goalProgressBar) {
        goalProgressBar.style.width = `${percentualBarra}%`;
    }

    if (goalRestante) {
        goalRestante.textContent = valorRestante > 0
            ? `Faltam ${formatarMoedaMeta(valorRestante)} para alcançar sua meta.`
            : "Parabéns! Você alcançou sua meta!";
    }
}

function exibirMetaSidebarVazia() {
    const goalValorAtual = document.getElementById("goal-valor-atual");
    const goalValorMeta = document.getElementById("goal-valor-meta");
    const goalPercentual = document.getElementById("goal-percentual");
    const goalProgressBar = document.getElementById("goal-progress-bar");
    const goalRestante = document.getElementById("goal-restante");

    if (goalValorAtual) {
        goalValorAtual.textContent = formatarMoedaMeta(0);
    }

    if (goalValorMeta) {
        goalValorMeta.textContent = `de ${formatarMoedaMeta(0)}`;
    }

    if (goalPercentual) {
        goalPercentual.textContent = "0%";
    }

    if (goalProgressBar) {
        goalProgressBar.style.width = "0%";
    }

    if (goalRestante) {
        goalRestante.textContent = "Nenhuma meta cadastrada.";
    }
}

// Configura evento de Enter no input
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("chat-input");

    if (input) {
        input.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                enviarPergunta();
            }
        });

        input.focus();
    }

    buscarMetaSidebar();
});
