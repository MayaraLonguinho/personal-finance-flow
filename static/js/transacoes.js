// Script da página de transações
// Responsável por buscar e exibir todas as transações

function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarData(data) {
    return window.PFF.formatarData(data);
}

function getStatusClass(status) {
    switch(status) {
        case "confirmado":
            return "status-confirmado";
        case "pendente":
            return "status-pendente";
        case "cancelado":
            return "status-cancelado";
        default:
            return "";
    }
}

function getTipoClass(tipo) {
    switch(tipo) {
        case "entrada":
            return "entrada-text";
        case "saida":
            return "saida-text";
        case "investimento":
            return "investimento-text";
        default:
            return "";
    }
}

function getCategoriaTagClass(categoria) {
    const classes = {
        "Salário": "tag-green",
        "Alimentação": "tag-blue",
        "Casa": "tag-pink",
        "Transporte": "tag-cyan",
        "Lazer": "tag-orange",
        "Saúde": "tag-purple"
    };
    return classes[categoria] || "tag-blue";
}

async function buscarTransacoes() {
    try {
        // Obtém valores dos filtros
        const filtroDescricao = document.getElementById("filtro-descricao").value;
        const filtroCategoria = document.getElementById("filtro-categoria").value;
        const filtroTipo = document.getElementById("filtro-tipo").value;
        const filtroStatus = document.getElementById("filtro-status").value;
        
        // Constrói URL com filtros
        const params = new URLSearchParams();
        if (filtroDescricao) params.append('descricao', filtroDescricao);
        if (filtroCategoria) params.append('categoria', filtroCategoria);
        if (filtroTipo) params.append('tipo', filtroTipo);
        if (filtroStatus) params.append('status', filtroStatus);
        
        const url = `/api/transacoes/todas?${params.toString()}`;
        
        const resposta = await fetch(url);

        if (!resposta.ok) {
            throw new Error("Erro ao buscar transações da API");
        }

        const transacoes = await resposta.json();
        preencherTabela(transacoes);

    } catch (erro) {
        console.error("Erro ao carregar transações:", erro);
        document.getElementById("corpo-tabela").innerHTML = `
            <tr>
                <td colspan="9" class="loading">Não foi possível carregar as transações.</td>
            </tr>
        `;
    }
}

function limparFiltros() {
    document.getElementById("filtro-descricao").value = "";
    document.getElementById("filtro-categoria").value = "";
    document.getElementById("filtro-tipo").value = "";
    document.getElementById("filtro-status").value = "";
    buscarTransacoes();
}

// Adiciona eventos para aplicar filtros quando os campos mudarem
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("filtro-descricao").addEventListener("input", buscarTransacoes);
    document.getElementById("filtro-categoria").addEventListener("change", buscarTransacoes);
    document.getElementById("filtro-tipo").addEventListener("change", buscarTransacoes);
    document.getElementById("filtro-status").addEventListener("change", buscarTransacoes);
});

// Funções para gerenciar meta na sidebar
function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

async function buscarMeta() {
    try {
        const resposta = await fetch("/api/meta");

        if (!resposta.ok) {
            if (resposta.status === 404) {
                exibirMetaVazia();
                return;
            }
            throw new Error("Erro ao buscar meta");
        }

        const meta = await resposta.json();
        exibirMeta(meta);

    } catch (erro) {
        console.error("Erro ao carregar meta:", erro);
        exibirMetaVazia();
    }
}

function exibirMeta(meta) {
    document.getElementById("goal-valor-atual").textContent = formatarMoeda(meta.valor_atual);
    document.getElementById("goal-valor-meta").textContent = `de ${formatarMoeda(meta.valor_meta)}`;
    document.getElementById("goal-percentual").textContent = `${meta.percentual}%`;
    document.getElementById("goal-progress-bar").style.width = `${meta.percentual}%`;
    
    const valorRestante = meta.valor_restante;
    if (valorRestante > 0) {
        document.getElementById("goal-restante").textContent = `Faltam ${formatarMoeda(valorRestante)} para alcançar sua meta.`;
    } else {
        document.getElementById("goal-restante").textContent = "Parabéns! Você alcançou sua meta!";
    }
}

function exibirMetaVazia() {
    document.getElementById("goal-valor-atual").textContent = formatarMoeda(0);
    document.getElementById("goal-valor-meta").textContent = `de ${formatarMoeda(0)}`;
    document.getElementById("goal-percentual").textContent = "0%";
    document.getElementById("goal-progress-bar").style.width = "0%";
    document.getElementById("goal-restante").textContent = "Nenhuma meta cadastrada.";
}

// Carregar meta ao abrir a página
buscarMeta();

function preencherTabela(transacoes) {
    const corpoTabela = document.getElementById("corpo-tabela");

    if (!transacoes || transacoes.length === 0) {
        corpoTabela.innerHTML = `
            <tr>
                <td colspan="9" class="loading">Nenhuma transação encontrada.</td>
            </tr>
        `;
        return;
    }

    corpoTabela.innerHTML = transacoes.map(transacao => `
        <tr>
            <td>${formatarData(transacao.data_transacao)}</td>
            <td>${transacao.descricao || "-"}</td>
            <td><span class="tag ${getCategoriaTagClass(transacao.categoria)}">${transacao.categoria || "-"}</span></td>
            <td><span class="type ${getTipoClass(transacao.tipo)}">${transacao.tipo || "-"}</span></td>
            <td class="value ${getTipoClass(transacao.tipo)}">${formatarMoeda(transacao.valor)}</td>
            <td>${transacao.conta || "-"}</td>
            <td>${transacao.instituicao || "-"}</td>
            <td><span class="${getStatusClass(transacao.status)}">${transacao.status || "-"}</span></td>
            <td>
                <div class="actions">
                    <button class="action-btn edit" onclick="editarTransacao(${transacao.id})">Editar</button>
                    <button class="action-btn delete" onclick="excluirTransacao(${transacao.id})">Excluir</button>
                </div>
            </td>
        </tr>
    `).join("");
}

function editarTransacao(id) {
    // Busca a transação pelo ID
    fetch(`/api/transacoes/todas`)
        .then(resposta => resposta.json())
        .then(transacoes => {
            const transacao = transacoes.find(t => t.id === id);
            if (transacao) {
                // Preenche o formulário com os dados da transação
                document.getElementById("transacao-id").value = transacao.id;
                document.getElementById("data").value = transacao.data_transacao ? transacao.data_transacao.split('T')[0] : '';
                document.getElementById("descricao").value = transacao.descricao || '';
                document.getElementById("categoria").value = transacao.categoria || '';
                document.getElementById("tipo").value = transacao.tipo || '';
                document.getElementById("valor").value = transacao.valor || '';
                document.getElementById("conta").value = transacao.conta || '';
                document.getElementById("instituicao").value = transacao.instituicao || '';
                document.getElementById("status").value = transacao.status || '';
                
                // Muda o título do modal
                document.getElementById("modal-titulo").textContent = "Editar Transação";
                
                // Abre o modal
                abrirModalNovaTransacao();
            } else {
                alert("Transação não encontrada.");
            }
        })
        .catch(erro => {
            console.error("Erro ao buscar transação:", erro);
            alert("Não foi possível carregar a transação.");
        });
}

function excluirTransacao(id) {
    // Pedir confirmação
    if (window.PFF.confirmarExclusao("Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.")) {
        fetch(`/api/transacoes/${id}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": window.PFF.csrfToken
            }
        })
        .then(resposta => {
            if (resposta.ok) {
                return resposta.json();
            } else if (resposta.status === 404) {
                throw new Error("Transação não encontrada");
            } else {
                throw new Error("Erro ao excluir transação");
            }
        })
        .then(resultado => {
            alert(resultado.mensagem);
            buscarTransacoes(); // Atualiza a tabela
        })
        .catch(erro => {
            console.error("Erro ao excluir transação:", erro);
            alert("Erro: " + erro.message);
        });
    }
}

// Funções do Modal de Nova Transação
function abrirModalNovaTransacao() {
    const modal = document.getElementById("modal-nova-transacao");
    modal.style.display = "flex";
    
    // Se não tiver ID, é criação nova - define data atual
    const idTransacao = document.getElementById("transacao-id").value;
    if (!idTransacao) {
        const hoje = new Date().toISOString().split('T')[0];
        document.getElementById("data").value = hoje;
    }
}

function fecharModalNovaTransacao() {
    const modal = document.getElementById("modal-nova-transacao");
    modal.style.display = "none";
    
    // Limpa o formulário e reseta o título
    document.getElementById("form-nova-transacao").reset();
    document.getElementById("transacao-id").value = "";
    document.getElementById("modal-titulo").textContent = "Nova Transação";
}

async function salvarNovaTransacao(event) {
    event.preventDefault();
    
    const form = document.getElementById("form-nova-transacao");
    const formData = new FormData(form);
    
    const idTransacao = document.getElementById("transacao-id").value;
    
    const dados = {
        data: formData.get("data"),
        descricao: formData.get("descricao"),
        categoria: formData.get("categoria"),
        tipo: formData.get("tipo"),
        valor: formData.get("valor"),
        conta: formData.get("conta") || "",
        instituicao: formData.get("instituicao") || "",
        status: formData.get("status")
    };
    
    try {
        let resposta;
        
        if (idTransacao) {
            // Edição - PUT
            resposta = await fetch(`/api/transacoes/${idTransacao}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.PFF.csrfToken
                },
                body: JSON.stringify(dados)
            });
        } else {
            // Criação - POST
            resposta = await fetch("/api/transacoes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.PFF.csrfToken
                },
                body: JSON.stringify(dados)
            });
        }
        
        if (resposta.ok) {
            const resultado = await resposta.json();
            alert(resultado.mensagem);
            fecharModalNovaTransacao();
            buscarTransacoes(); // Atualiza a tabela
        } else {
            const erro = await resposta.json();
            alert("Erro: " + erro.erro);
        }
    } catch (erro) {
        console.error("Erro ao salvar transação:", erro);
        alert("Não foi possível salvar a transação.");
    }
}

// Fecha o modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById("modal-nova-transacao");
    if (event.target === modal) {
        fecharModalNovaTransacao();
    }
}
// Carregar transações ao abrir a página
buscarTransacoes();
