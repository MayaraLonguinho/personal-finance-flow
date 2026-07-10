// Módulo de categorias
// Responsável por gerenciar categorias na página de categorias

// Busca todas as categorias
async function buscarCategorias() {
    try {
        const resposta = await fetch('/api/categorias');
        const categorias = await resposta.json();

        if (!resposta.ok) {
            throw new Error('Erro ao buscar categorias');
        }

        exibirCategorias(categorias);

    } catch (erro) {
        console.error('Erro ao buscar categorias:', erro);
        window.PFF.mostrarNotificacao("Erro", "Erro ao buscar categorias", "error");
    }
}

// Exibe categorias na página
function exibirCategorias(categorias) {
    const grid = document.getElementById('categorias-grid');
    const empty = document.getElementById('categorias-empty');

    if (!categorias || categorias.length === 0) {
        if (empty) empty.style.display = 'flex';
        return;
    }

    if (empty) empty.style.display = 'none';

    // Limpa grid
    grid.innerHTML = '';

    // Adiciona cada categoria
    categorias.forEach(categoria => {
        const card = criarCardCategoria(categoria);
        grid.appendChild(card);
    });
}

// Cria card de categoria
function criarCardCategoria(categoria) {
    const card = document.createElement('div');
    card.className = 'categoria-card';

    const cor = categoria.cor || '#e5e7eb';

    card.innerHTML = `
        <div class="categoria-header">
            <h4>${categoria.nome}</h4>
            <div class="categoria-cor" style="background-color: ${cor}"></div>
        </div>
        
        <div class="categoria-palavras-chave">
            <span>Palavras-chave</span>
            <ul>
                ${categoria.palavras_chave.length > 0
            ? categoria.palavras_chave.map(palavra => `<li>${palavra}</li>`).join('')
            : '<li>Nenhuma palavra-chave</li>'}
            </ul>
        </div>
        
        <div class="categoria-estatisticas">
            <div class="categoria-estatistica">
                <span>Transações</span>
                <strong>${categoria.quantidade_transacoes}</strong>
            </div>
            <div class="categoria-estatistica">
                <span>Valor Total</span>
                <strong>${window.PFF.formatarMoeda(categoria.valor_total)}</strong>
            </div>
        </div>
        
        <div class="categoria-actions">
            <button class="btn-outline" onclick="abrirModalCategoria('${categoria.nome}')">Editar</button>
            ${categoria.nome.toLowerCase() !== 'outros'
            ? `<button class="btn-outline btn-danger" onclick="excluirCategoria('${categoria.nome}')">Excluir</button>`
            : ''}
        </div>
    `;

    return card;
}

// Abre modal de categoria
function abrirModalCategoria(nomeCategoria = null) {
    const modal = document.getElementById('modal-categoria');
    const titulo = document.getElementById('modal-categoria-titulo');
    const nomeInput = document.getElementById('categoria-nome');
    const palavrasChaveInput = document.getElementById('categoria-palavras-chave');
    const corInput = document.getElementById('categoria-cor');
    const nomeAtualInput = document.getElementById('categoria-nome-atual');

    if (!modal || !titulo || !nomeInput || !palavrasChaveInput || !corInput || !nomeAtualInput) {
        window.PFF.mostrarNotificacao("Erro", "Erro ao acessar modal de categoria", "error");
        return;
    }

    if (nomeCategoria) {
        // Modo edição
        titulo.textContent = 'Editar Categoria';
        nomeAtualInput.value = nomeCategoria;

        // Busca categoria para preencher campos
        fetch(`/api/categorias`)
            .then(res => res.json())
            .then(categorias => {
                const categoria = categorias.find(c => c.nome === nomeCategoria);
                if (categoria) {
                    nomeInput.value = categoria.nome;
                    palavrasChaveInput.value = categoria.palavras_chave.join(', ');
                    corInput.value = categoria.cor || '';
                }
            })
            .catch(erro => {
                console.error('Erro ao buscar categoria:', erro);
            });
    } else {
        // Modo criação
        titulo.textContent = 'Criar Categoria';
        nomeInput.value = '';
        palavrasChaveInput.value = '';
        corInput.value = '';
        nomeAtualInput.value = '';
    }

    modal.style.display = 'flex';
}

// Fecha modal de categoria
function fecharModalCategoria() {
    const modal = document.getElementById('modal-categoria');
    if (modal) modal.style.display = 'none';
}

// Salva categoria
async function salvarCategoria() {
    const nomeInput = document.getElementById('categoria-nome');
    const palavrasChaveInput = document.getElementById('categoria-palavras-chave');
    const corInput = document.getElementById('categoria-cor');
    const nomeAtualInput = document.getElementById('categoria-nome-atual');

    if (!nomeInput || !palavrasChaveInput || !corInput || !nomeAtualInput) {
        window.PFF.mostrarNotificacao("Erro", "Erro ao acessar campos do formulário", "error");
        return;
    }

    const nome = nomeInput.value.trim();
    const palavrasChaveTexto = palavrasChaveInput.value.trim();
    const cor = corInput.value;
    const nomeAtual = nomeAtualInput.value;

    // Validações
    if (!nome) {
        window.PFF.mostrarNotificacao("Validação", "Por favor, informe o nome da categoria", "warning");
        return;
    }

    // Converte palavras-chave para array
    const palavrasChave = palavrasChaveTexto
        ? palavrasChaveTexto.split(',').map(p => p.trim()).filter(p => p)
        : [];

    const dados = {
        nome: nome,
        palavras_chave: palavrasChave
    };

    if (cor) {
        dados.cor = cor;
    }

    try {
        let resposta;
        if (nomeAtual) {
            // Atualizar categoria existente
            resposta = await fetch(`/api/categorias/${encodeURIComponent(nomeAtual)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.PFF.csrfToken
                },
                body: JSON.stringify(dados)
            });
        } else {
            // Criar nova categoria
            resposta = await fetch('/api/categorias', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.PFF.csrfToken
                },
                body: JSON.stringify(dados)
            });
        }

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(resultado.erro || 'Erro ao salvar categoria');
        }

        window.PFF.mostrarNotificacao("Sucesso", resultado.mensagem || 'Categoria salva com sucesso!', "success");
        fecharModalCategoria();
        buscarCategorias();

    } catch (erro) {
        console.error('Erro ao salvar categoria:', erro);
        window.PFF.mostrarNotificacao("Erro ao salvar categoria", `Erro ao salvar categoria: ${erro.message}`, "error");
    }
}

// Exclui categoria
async function excluirCategoria(nome) {
    const confirmou = window.PFF.confirmarExclusao(`Tem certeza que deseja excluir a categoria "${nome}"? As transações desta categoria serão movidas para "outros".`);

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await fetch(`/api/categorias/${encodeURIComponent(nome)}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': window.PFF.csrfToken
            }
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(resultado.erro || 'Erro ao excluir categoria');
        }

        window.PFF.mostrarNotificacao("Sucesso", resultado.mensagem || 'Categoria excluída com sucesso!', "success");
        buscarCategorias();

    } catch (erro) {
        console.error('Erro ao excluir categoria:', erro);
        window.PFF.mostrarNotificacao("Erro ao excluir categoria", `Erro ao excluir categoria: ${erro.message}`, "error");
    }
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

// Carrega categorias ao abrir a página
document.addEventListener("DOMContentLoaded", function () {
    buscarCategorias();
    buscarMetaSidebar();
});
