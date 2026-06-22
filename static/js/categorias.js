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
        alert('Erro ao buscar categorias');
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
                <strong>R$ ${categoria.valor_total.toFixed(2)}</strong>
            </div>
        </div>
        
        <div class="categoria-actions">
            <button class="btn-outline" onclick="abrirModalCategoria('${categoria.nome}')">Editar</button>
            ${categoria.nome.toLowerCase() !== 'outros' 
                ? `<button class="btn-outline btn-danger" onclick="excluirCategoria(${categoria.id})">Excluir</button>` 
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
        alert('Erro ao acessar modal de categoria');
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
        alert('Erro ao acessar campos do formulário');
        return;
    }
    
    const nome = nomeInput.value.trim();
    const palavrasChaveTexto = palavrasChaveInput.value.trim();
    const cor = corInput.value;
    const nomeAtual = nomeAtualInput.value;
    
    // Validações
    if (!nome) {
        alert('Por favor, informe o nome da categoria');
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        } else {
            // Criar nova categoria
            resposta = await fetch('/api/categorias', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        }
        
        const resultado = await resposta.json();
        
        if (!resposta.ok) {
            throw new Error(resultado.erro || 'Erro ao salvar categoria');
        }
        
        alert(resultado.mensagem || 'Categoria salva com sucesso!');
        fecharModalCategoria();
        buscarCategorias();
        
    } catch (erro) {
        console.error('Erro ao salvar categoria:', erro);
        alert(`Erro ao salvar categoria: ${erro.message}`);
    }
}

// Exclui categoria
async function excluirCategoria(id) {
    const confirmou = confirm(`Tem certeza que deseja excluir esta categoria? As transações desta categoria serão movidas para "outros".`);
    
    if (!confirmou) {
        return;
    }
    
    try {
        const resposta = await fetch(`/api/categorias/${id}`, {
            method: 'DELETE'
        });
        
        const resultado = await resposta.json();
        
        if (!resposta.ok) {
            throw new Error(resultado.erro || 'Erro ao excluir categoria');
        }
        
        const quantidadeAtualizada = resultado.quantidade_transacoes_atualizadas || 0;
        alert(`${resultado.mensagem} ${quantidadeAtualizada > 0 ? `(${quantidadeAtualizada} transações movidas para "outros")` : ''}`);
        buscarCategorias();
        
    } catch (erro) {
        console.error('Erro ao excluir categoria:', erro);
        alert(`Erro ao excluir categoria: ${erro.message}`);
    }
}

// Carrega categorias ao abrir a página
document.addEventListener('DOMContentLoaded', function() {
    buscarCategorias();
});
