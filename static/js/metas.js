// Funções para gerenciar metas na página exclusiva de metas

function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarData(data) {
    return window.PFF.formatarData(data);
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
    const metaEmpty = document.getElementById("meta-empty");
    const metaContent = document.getElementById("meta-content");
    
    if (metaEmpty) metaEmpty.style.display = "none";
    if (metaContent) metaContent.style.display = "block";
    
    const metaTituloDisplay = document.getElementById("meta-titulo-display");
    const metaStatus = document.getElementById("meta-status");
    const metaValorAtualDisplay = document.getElementById("meta-valor-atual-display");
    const metaValorMetaDisplay = document.getElementById("meta-valor-meta-display");
    const metaDataLimiteDisplay = document.getElementById("meta-data-limite-display");
    const metaPercentualDisplay = document.getElementById("meta-percentual-display");
    const metaProgressBar = document.getElementById("meta-progress-bar");
    const metaRestanteDisplay = document.getElementById("meta-restante-display");
    
    if (metaTituloDisplay) metaTituloDisplay.textContent = meta.titulo;
    if (metaStatus) metaStatus.textContent = meta.status.charAt(0).toUpperCase() + meta.status.slice(1);
    if (metaValorAtualDisplay) metaValorAtualDisplay.textContent = formatarMoeda(meta.valor_atual);
    if (metaValorMetaDisplay) metaValorMetaDisplay.textContent = formatarMoeda(meta.valor_meta);
    if (metaDataLimiteDisplay) metaDataLimiteDisplay.textContent = formatarData(meta.data_limite);
    if (metaPercentualDisplay) metaPercentualDisplay.textContent = `${meta.percentual}%`;
    if (metaProgressBar) metaProgressBar.style.width = `${meta.percentual}%`;
    
    const valorRestante = meta.valor_restante;
    if (metaRestanteDisplay) {
        if (valorRestante > 0) {
            metaRestanteDisplay.textContent = `Faltam ${formatarMoeda(valorRestante)}`;
        } else {
            metaRestanteDisplay.textContent = "Meta alcançada!";
        }
    }
    
    // Exibir meta na sidebar
    const goalValorAtual = document.getElementById("goal-valor-atual");
    const goalValorMeta = document.getElementById("goal-valor-meta");
    const goalPercentual = document.getElementById("goal-percentual");
    const goalProgressBar = document.getElementById("goal-progress-bar");
    const goalRestante = document.getElementById("goal-restante");
    
    if (goalValorAtual) goalValorAtual.textContent = formatarMoeda(meta.valor_atual);
    if (goalValorMeta) goalValorMeta.textContent = `de ${formatarMoeda(meta.valor_meta)}`;
    if (goalPercentual) goalPercentual.textContent = `${meta.percentual}%`;
    if (goalProgressBar) goalProgressBar.style.width = `${meta.percentual}%`;
    
    if (goalRestante) {
        if (valorRestante > 0) {
            goalRestante.textContent = `Faltam ${formatarMoeda(valorRestante)} para alcançar sua meta.`;
        } else {
            goalRestante.textContent = "Parabéns! Você alcançou sua meta!";
        }
    }
}

function exibirMetaVazia() {
    const metaEmpty = document.getElementById("meta-empty");
    const metaContent = document.getElementById("meta-content");
    
    if (metaEmpty) metaEmpty.style.display = "block";
    if (metaContent) metaContent.style.display = "none";
    
    // Exibir estado vazio na sidebar
    const goalValorAtual = document.getElementById("goal-valor-atual");
    const goalValorMeta = document.getElementById("goal-valor-meta");
    const goalPercentual = document.getElementById("goal-percentual");
    const goalProgressBar = document.getElementById("goal-progress-bar");
    const goalRestante = document.getElementById("goal-restante");
    
    if (goalValorAtual) goalValorAtual.textContent = formatarMoeda(0);
    if (goalValorMeta) goalValorMeta.textContent = `de ${formatarMoeda(0)}`;
    if (goalPercentual) goalPercentual.textContent = "0%";
    if (goalProgressBar) goalProgressBar.style.width = "0%";
    if (goalRestante) goalRestante.textContent = "Nenhuma meta cadastrada.";
}

function abrirModalMeta() {
    const modal = document.getElementById("modal-meta");
    const tituloModal = document.getElementById("modal-meta-titulo");
    const metaId = document.getElementById("meta-id");
    const metaTitulo = document.getElementById("meta-titulo");
    const metaValorMeta = document.getElementById("meta-valor-meta");
    const metaValorAtual = document.getElementById("meta-valor-atual");
    const metaDataLimite = document.getElementById("meta-data-limite");
    const metaStatusSelect = document.getElementById("meta-status-select");
    
    // Limpa campos
    if (metaTitulo) metaTitulo.value = "";
    if (metaValorMeta) metaValorMeta.value = "";
    if (metaValorAtual) metaValorAtual.value = "";
    if (metaDataLimite) metaDataLimite.value = "";
    if (metaStatusSelect) metaStatusSelect.value = "ativa";
    if (metaId) metaId.value = "";
    
    // Tenta buscar meta existente para edição
    fetch("/api/meta")
        .then(resposta => {
            if (resposta.ok) {
                return resposta.json();
            }
            return null;
        })
        .then(meta => {
            if (meta && meta.id) {
                // Modo edição
                if (tituloModal) tituloModal.textContent = "Editar Meta";
                if (metaId) metaId.value = meta.id;
                if (metaTitulo) metaTitulo.value = meta.titulo;
                if (metaValorMeta) metaValorMeta.value = meta.valor_meta;
                if (metaValorAtual) metaValorAtual.value = meta.valor_atual;
                if (metaDataLimite) metaDataLimite.value = meta.data_limite || "";
                if (metaStatusSelect) metaStatusSelect.value = meta.status;
            } else {
                // Modo criação
                if (tituloModal) tituloModal.textContent = "Criar Meta";
            }
        })
        .catch(erro => {
            console.error("Erro ao buscar meta:", erro);
            if (tituloModal) tituloModal.textContent = "Criar Meta";
        });
    
    if (modal) modal.style.display = "flex";
}

function fecharModalMeta() {
    const modal = document.getElementById("modal-meta");
    if (modal) modal.style.display = "none";
}

async function salvarMeta() {
    const metaIdElement = document.getElementById("meta-id");
    const metaTituloElement = document.getElementById("meta-titulo");
    const metaValorMetaElement = document.getElementById("meta-valor-meta");
    const metaValorAtualElement = document.getElementById("meta-valor-atual");
    const metaDataLimiteElement = document.getElementById("meta-data-limite");
    const metaStatusSelectElement = document.getElementById("meta-status-select");
    
    if (!metaIdElement || !metaTituloElement || !metaValorMetaElement || !metaValorAtualElement || !metaDataLimiteElement || !metaStatusSelectElement) {
        alert("Erro ao acessar campos do formulário.");
        return;
    }
    
    const metaId = metaIdElement.value;
    const titulo = metaTituloElement.value.trim();
    const valorMeta = metaValorMetaElement.value;
    const valorAtual = metaValorAtualElement.value;
    const dataLimite = metaDataLimiteElement.value;
    const status = metaStatusSelectElement.value;
    
    // Validações
    if (!titulo) {
        alert("Por favor, informe o título da meta.");
        return;
    }
    
    if (!valorMeta || Number(valorMeta) <= 0) {
        alert("Por favor, informe um valor de meta válido maior que zero.");
        return;
    }
    
    const dados = {
        titulo: titulo,
        valor_meta: Number(valorMeta),
        valor_atual: Number(valorAtual || 0),
        status: status
    };
    
    if (dataLimite) {
        dados.data_limite = dataLimite;
    }
    
    console.log("Enviando dados:", dados);
    
    try {
        let resposta;
        if (metaId) {
            // Atualizar meta existente
            resposta = await fetch(`/api/meta/${metaId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });
        } else {
            // Criar nova meta
            resposta = await fetch("/api/meta", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });
        }
        
        const resultado = await resposta.json();
        console.log("Resposta da API:", resultado);
        
        if (!resposta.ok) {
            throw new Error(resultado.erro || "Erro ao salvar meta");
        }
        
        alert(resultado.mensagem || "Meta salva com sucesso!");
        fecharModalMeta();
        buscarMeta();
        
    } catch (erro) {
        console.error("Erro ao salvar meta:", erro);
        alert(`Erro ao salvar meta: ${erro.message}`);
    }
}

async function excluirMeta() {
    if (!window.PFF.confirmarExclusao("Tem certeza de que deseja excluir esta meta? Esta ação não poderá ser desfeita.")) {
        return;
    }
    
    try {
        // Busca a meta ativa para obter o ID
        const respostaMeta = await fetch("/api/meta");
        
        if (!respostaMeta.ok) {
            throw new Error("Erro ao buscar meta para exclusão");
        }
        
        const meta = await respostaMeta.json();
        
        if (!meta || !meta.id) {
            throw new Error("Nenhuma meta encontrada para excluir");
        }
        
        // Exclui a meta usando o ID
        const resposta = await fetch(`/api/meta/${meta.id}`, {
            method: "DELETE"
        });
        
        const resultado = await resposta.json();
        
        if (!resposta.ok) {
            throw new Error(resultado.erro || "Erro ao excluir meta");
        }
        
        alert(resultado.mensagem || "Meta excluída com sucesso!");
        buscarMeta();
        
    } catch (erro) {
        console.error("Erro ao excluir meta:", erro);
        alert(`Erro ao excluir meta: ${erro.message}`);
    }
}

// Carregar meta ao abrir a página
buscarMeta();
