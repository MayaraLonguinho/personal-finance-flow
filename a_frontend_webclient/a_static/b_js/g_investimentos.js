function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarPercentual(valor) {
    return `${(Number(valor) || 0).toFixed(2)}%`;
}

function formatarData(dataTexto) {
    return window.PFF.formatarData(dataTexto);
}

function escaparHtml(texto) {
    const elemento = document.createElement("div");
    elemento.textContent = texto ?? "-";
    return elemento.innerHTML;
}

function capitalizar(texto) {
    if (!texto) {
        return "-";
    }

    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function mostrarErroFormulario(mensagem) {
    const erro = document.getElementById(
        "investimento-form-error"
    );

    if (!erro) {
        return;
    }

    if (!mensagem) {
        erro.hidden = true;
        erro.textContent = "";
        return;
    }

    erro.textContent = mensagem;
    erro.hidden = false;
}

async function buscarResumoInvestimentos() {
    try {
        const resposta = await fetch(
            "/api/investimentos/resumo"
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro ||
                "Não foi possível carregar o resumo."
            );
        }

        preencherResumoInvestimentos(dados);
        preencherDistribuicao(dados.distribuicao_por_tipo || []);

    } catch (erro) {
        console.error(
            "Erro ao buscar resumo de investimentos:",
            erro
        );
    }
}

function preencherResumoInvestimentos(resumo) {
    document.getElementById(
        "resumo-total-aplicado"
    ).textContent = formatarMoeda(resumo.total_aplicado);

    document.getElementById(
        "resumo-valor-atual"
    ).textContent = formatarMoeda(resumo.valor_atual_total);

    const resultadoElemento = document.getElementById(
        "resumo-lucro-prejuizo"
    );

    const lucroPrejuizo = Number(
        resumo.lucro_prejuizo
    ) || 0;

    resultadoElemento.textContent = formatarMoeda(
        lucroPrejuizo
    );

    resultadoElemento.style.color = lucroPrejuizo < 0
        ? "#ef4444"
        : "#16a34a";

    const rentabilidadeElemento = document.getElementById(
        "resumo-rentabilidade"
    );

    const rentabilidade = Number(
        resumo.rentabilidade_total
    ) || 0;

    rentabilidadeElemento.textContent = formatarPercentual(
        rentabilidade
    );

    rentabilidadeElemento.style.color = rentabilidade < 0
        ? "#ef4444"
        : "#16a34a";

    document.getElementById(
        "resumo-quantidade-ativos"
    ).textContent = resumo.quantidade_ativos || 0;

    const total = resumo.quantidade_total || 0;

    document.getElementById(
        "resumo-quantidade-total"
    ).textContent = (
            `${total} ` +
            `${total === 1
                ? "investimento cadastrado"
                : "investimentos cadastrados"}`
        );
}

function preencherDistribuicao(distribuicao) {
    const container = document.getElementById(
        "distribuicao-lista"
    );

    if (!distribuicao || distribuicao.length === 0) {
        container.innerHTML = `
            <p class="empty-text">
                Nenhum investimento ativo encontrado.
            </p>
        `;

        return;
    }

    const maiorValor = Math.max(
        ...distribuicao.map(
            item => Number(item.valor_atual) || 0
        ),
        1
    );

    container.innerHTML = distribuicao.map(item => {
        const valor = Number(item.valor_atual) || 0;

        const percentual = Math.min(
            Math.max((valor / maiorValor) * 100, 0),
            100
        );

        return `
            <div class="distribuicao-item">
                <div class="distribuicao-conteudo">
                    <div class="distribuicao-topo">
                        <strong>
                            ${escaparHtml(item.tipo)}
                        </strong>

                        <span>
                            ${item.quantidade || 0}
                            investimento(s)
                        </span>
                    </div>

                    <div class="distribuicao-barra">
                        <div
                            class="distribuicao-progresso"
                            style="width: ${percentual}%"
                        ></div>
                    </div>
                </div>

                <strong class="distribuicao-valor">
                    ${formatarMoeda(valor)}
                </strong>
            </div>
        `;
    }).join("");
}

async function buscarInvestimentos() {
    const status = document.getElementById(
        "filtro-status"
    ).value;

    const url = status
        ? `/api/investimentos?status=${encodeURIComponent(status)}`
        : "/api/investimentos";

    try {
        const resposta = await fetch(url);
        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro ||
                "Não foi possível buscar os investimentos."
            );
        }

        exibirInvestimentos(dados);

    } catch (erro) {
        console.error(
            "Erro ao buscar investimentos:",
            erro
        );

        const container = document.getElementById(
            "investimentos-cards"
        );

        container.innerHTML = `
            <div class="investimentos-empty">
                <p>
                    Não foi possível carregar os investimentos.
                </p>
            </div>
        `;
    }
}

function exibirInvestimentos(investimentos) {
    const container = document.getElementById(
        "investimentos-cards"
    );

    const contador = document.getElementById(
        "contador-investimentos"
    );

    contador.textContent = (
        `${investimentos.length} ` +
        `${investimentos.length === 1
            ? "registro"
            : "registros"}`
    );

    if (!investimentos || investimentos.length === 0) {
        container.innerHTML = `
            <div class="investimentos-empty">
                <div>
                    <p>
                        Nenhum investimento encontrado.
                    </p>

                    <button
                        class="btn-primary"
                        type="button"
                        onclick="abrirModalInvestimento()"
                        style="margin-top: 12px;"
                    >
                        Cadastrar investimento
                    </button>
                </div>
            </div>
        `;

        return;
    }

    container.innerHTML = investimentos.map(
        investimento => criarCardInvestimento(investimento)
    ).join("");
}

function criarCardInvestimento(investimento) {
    const valorAplicado = Number(
        investimento.valor_aplicado
    ) || 0;

    const valorAtual = Number(
        investimento.valor_atual
    ) || 0;

    const resultado = valorAtual - valorAplicado;

    const rentabilidadeCalculada = valorAplicado > 0
        ? (resultado / valorAplicado) * 100
        : 0;

    let classeResultado = "neutro";

    if (resultado > 0) {
        classeResultado = "positivo";
    } else if (resultado < 0) {
        classeResultado = "negativo";
    }

    const textoResultado = resultado > 0
        ? `Lucro de ${formatarMoeda(resultado)}`
        : resultado < 0
            ? `Prejuízo de ${formatarMoeda(Math.abs(resultado))}`
            : "Sem variação no valor";

    return `
        <article class="investimento-card">
            <div class="investimento-card-header">
                <div>
                    <h4>
                        ${escaparHtml(investimento.nome)}
                    </h4>

                    <span>
                        ${escaparHtml(investimento.tipo)}
                        ${investimento.instituicao
            ? ` • ${escaparHtml(investimento.instituicao)}`
            : ""}
                    </span>
                </div>

                <span
                    class="investimento-status ${investimento.status}"
                >
                    ${capitalizar(investimento.status)}
                </span>
            </div>

            <div class="investimento-valores">
                <div class="investimento-valor">
                    <span>Valor aplicado</span>

                    <strong>
                        ${formatarMoeda(valorAplicado)}
                    </strong>
                </div>

                <div class="investimento-valor">
                    <span>Valor atual</span>

                    <strong>
                        ${formatarMoeda(valorAtual)}
                    </strong>
                </div>
            </div>

            <div class="investimento-informacoes">
                <div class="investimento-info">
                    <span>Aplicação</span>

                    <strong>
                        ${formatarData(investimento.data_aplicacao)}
                    </strong>
                </div>

                <div class="investimento-info">
                    <span>Vencimento</span>

                    <strong>
                        ${formatarData(investimento.data_vencimento)}
                    </strong>
                </div>

                <div class="investimento-info">
                    <span>Rentabilidade calculada</span>

                    <strong>
                        ${formatarPercentual(rentabilidadeCalculada)}
                    </strong>
                </div>
            </div>

            <div
                class="investimento-resultado ${classeResultado}"
            >
                ${textoResultado}
            </div>

            <div class="investimento-acoes">
                <button
                    class="btn-secondary"
                    type="button"
                    onclick="editarInvestimento(${investimento.id})"
                >
                    Editar
                </button>

                <button
                    class="btn-danger"
                    type="button"
                    onclick="excluirInvestimento(${investimento.id}, '${escaparHtml(investimento.nome)}')"
                >
                    Excluir
                </button>
            </div>
        </article>
    `;
}

function limparFormularioInvestimento() {
    document.getElementById("investimento-id").value = "";
    document.getElementById("investimento-nome").value = "";
    document.getElementById("investimento-tipo").value = "";
    document.getElementById("investimento-instituicao").value = "";
    document.getElementById("investimento-valor-aplicado").value = "";
    document.getElementById("investimento-valor-atual").value = "";
    document.getElementById("investimento-rentabilidade").value = "";
    document.getElementById("investimento-data-aplicacao").value = "";
    document.getElementById("investimento-data-vencimento").value = "";
    document.getElementById("investimento-status").value = "ativo";

    mostrarErroFormulario("");
}

function abrirModalInvestimento() {
    limparFormularioInvestimento();

    document.getElementById(
        "modal-investimento-titulo"
    ).textContent = "Novo investimento";

    document.getElementById(
        "modal-investimento"
    ).style.display = "flex";
}

function fecharModalInvestimento() {
    document.getElementById(
        "modal-investimento"
    ).style.display = "none";

    mostrarErroFormulario("");
}

async function editarInvestimento(investimentoId) {
    try {
        const resposta = await fetch(
            `/api/investimentos/${investimentoId}`
        );

        const investimento = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                investimento.erro ||
                "Não foi possível buscar o investimento."
            );
        }

        document.getElementById(
            "modal-investimento-titulo"
        ).textContent = "Editar investimento";

        document.getElementById(
            "investimento-id"
        ).value = investimento.id;

        document.getElementById(
            "investimento-nome"
        ).value = investimento.nome || "";

        document.getElementById(
            "investimento-tipo"
        ).value = investimento.tipo || "";

        document.getElementById(
            "investimento-instituicao"
        ).value = investimento.instituicao || "";

        document.getElementById(
            "investimento-valor-aplicado"
        ).value = investimento.valor_aplicado ?? "";

        document.getElementById(
            "investimento-valor-atual"
        ).value = investimento.valor_atual ?? "";

        document.getElementById(
            "investimento-rentabilidade"
        ).value = investimento.rentabilidade_percentual ?? 0;

        document.getElementById(
            "investimento-data-aplicacao"
        ).value = investimento.data_aplicacao || "";

        document.getElementById(
            "investimento-data-vencimento"
        ).value = investimento.data_vencimento || "";

        document.getElementById(
            "investimento-status"
        ).value = investimento.status || "ativo";

        mostrarErroFormulario("");

        document.getElementById(
            "modal-investimento"
        ).style.display = "flex";

    } catch (erro) {
        console.error(
            "Erro ao editar investimento:",
            erro
        );

        window.PFF.mostrarNotificacao("Erro", erro.message, "error");
    }
}

function obterDadosFormulario() {
    return {
        nome: document.getElementById(
            "investimento-nome"
        ).value.trim(),

        tipo: document.getElementById(
            "investimento-tipo"
        ).value,

        instituicao: document.getElementById(
            "investimento-instituicao"
        ).value.trim(),

        valor_aplicado: Number(
            document.getElementById(
                "investimento-valor-aplicado"
            ).value
        ),

        valor_atual: Number(
            document.getElementById(
                "investimento-valor-atual"
            ).value
        ),

        rentabilidade_percentual: Number(
            document.getElementById(
                "investimento-rentabilidade"
            ).value || 0
        ),

        data_aplicacao: document.getElementById(
            "investimento-data-aplicacao"
        ).value,

        data_vencimento: document.getElementById(
            "investimento-data-vencimento"
        ).value || null,

        status: document.getElementById(
            "investimento-status"
        ).value
    };
}

function validarFormularioInvestimento(dados) {
    if (!dados.nome) {
        return "Informe o nome do investimento.";
    }

    if (!dados.tipo) {
        return "Selecione o tipo do investimento.";
    }

    if (
        !dados.valor_aplicado ||
        dados.valor_aplicado <= 0
    ) {
        return "O valor aplicado deve ser maior que zero.";
    }

    if (
        Number.isNaN(dados.valor_atual) ||
        dados.valor_atual < 0
    ) {
        return "Informe um valor atual válido.";
    }

    if (!dados.data_aplicacao) {
        return "Informe a data da aplicação.";
    }

    if (
        dados.data_vencimento &&
        dados.data_vencimento < dados.data_aplicacao
    ) {
        return (
            "A data de vencimento não pode ser anterior " +
            "à data da aplicação."
        );
    }

    return null;
}

async function salvarInvestimento() {
    const dados = obterDadosFormulario();
    const erroValidacao = validarFormularioInvestimento(dados);

    if (erroValidacao) {
        mostrarErroFormulario(erroValidacao);
        return;
    }

    const investimentoId = document.getElementById(
        "investimento-id"
    ).value;

    const botao = document.getElementById(
        "btn-salvar-investimento"
    );

    const textoOriginal = botao.textContent;

    botao.disabled = true;
    botao.textContent = "Salvando...";

    try {
        const url = investimentoId
            ? `/api/investimentos/${investimentoId}`
            : "/api/investimentos";

        const metodo = investimentoId
            ? "PUT"
            : "POST";

        const resposta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.PFF.csrfToken
            },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                "Não foi possível salvar o investimento."
            );
        }

        window.PFF.mostrarNotificacao(
            "Sucesso",
            resultado.mensagem || "Investimento salvo com sucesso.",
            "success"
        );

        fecharModalInvestimento();
        await carregarPaginaInvestimentos();

    } catch (erro) {
        console.error(
            "Erro ao salvar investimento:",
            erro
        );

        mostrarErroFormulario(erro.message);

    } finally {
        botao.disabled = false;
        botao.textContent = textoOriginal;
    }
}

async function excluirInvestimento(
    investimentoId,
    investimentoNome
) {
    const confirmou = window.PFF.confirmarExclusao(
        `Deseja excluir o investimento "${investimentoNome}"?`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await fetch(
            `/api/investimentos/${investimentoId}`,
            {
                method: "DELETE",
                headers: { "X-CSRFToken": window.PFF.csrfToken }
            }
        );

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                "Não foi possível excluir o investimento."
            );
        }

        window.PFF.mostrarNotificacao(
            "Sucesso",
            resultado.mensagem || "Investimento excluído com sucesso.",
            "success"
        );

        await carregarPaginaInvestimentos();

    } catch (erro) {
        console.error(
            "Erro ao excluir investimento:",
            erro
        );

        window.PFF.mostrarNotificacao("Erro", erro.message, "error");
    }
}

function limparFiltroInvestimentos() {
    document.getElementById(
        "filtro-status"
    ).value = "";

    buscarInvestimentos();
}

async function buscarMetaSidebar() {
    try {
        const resposta = await fetch("/api/meta");

        if (!resposta.ok) {
            exibirMetaSidebarVazia();
            return;
        }

        const meta = await resposta.json();

        if (!meta || !meta.id) {
            exibirMetaSidebarVazia();
            return;
        }

        const valorAtual = Number(meta.valor_atual) || 0;
        const valorMeta = Number(meta.valor_meta) || 0;

        const percentual = Number(
            meta.percentual ??
            (
                valorMeta > 0
                    ? (valorAtual / valorMeta) * 100
                    : 0
            )
        );

        const percentualBarra = Math.min(
            Math.max(percentual, 0),
            100
        );

        const restante = Math.max(
            Number(
                meta.valor_restante ??
                valorMeta - valorAtual
            ),
            0
        );

        document.getElementById(
            "goal-valor-atual"
        ).textContent = formatarMoeda(valorAtual);

        document.getElementById(
            "goal-valor-meta"
        ).textContent = `de ${formatarMoeda(valorMeta)}`;

        document.getElementById(
            "goal-percentual"
        ).textContent = `${percentual.toFixed(0)}%`;

        document.getElementById(
            "goal-progress-bar"
        ).style.width = `${percentualBarra}%`;

        document.getElementById(
            "goal-restante"
        ).textContent = restante > 0
                ? (
                    `Faltam ${formatarMoeda(restante)} ` +
                    "para alcançar sua meta."
                )
                : "Parabéns! Você alcançou sua meta!";

    } catch (erro) {
        console.error(
            "Erro ao buscar meta:",
            erro
        );

        exibirMetaSidebarVazia();
    }
}

function exibirMetaSidebarVazia() {
    document.getElementById(
        "goal-valor-atual"
    ).textContent = "R$ 0,00";

    document.getElementById(
        "goal-valor-meta"
    ).textContent = "de R$ 0,00";

    document.getElementById(
        "goal-percentual"
    ).textContent = "0%";

    document.getElementById(
        "goal-progress-bar"
    ).style.width = "0%";

    document.getElementById(
        "goal-restante"
    ).textContent = "Nenhuma meta cadastrada.";
}

async function atualizarInvestimentos() {
    const botao = document.getElementById(
        "btn-atualizar-investimentos"
    );

    if (!botao) {
        return;
    }

    const textoOriginal = botao.textContent;

    try {
        botao.disabled = true;
        botao.textContent = "Atualizando...";

        await carregarPaginaInvestimentos();

        botao.textContent = "Atualizado";

        window.setTimeout(() => {
            botao.textContent = textoOriginal;
        }, 1500);
    } catch (erro) {
        console.error(
            "Erro ao atualizar investimentos:",
            erro
        );

        botao.textContent = "Erro ao atualizar";

        window.setTimeout(() => {
            botao.textContent = textoOriginal;
        }, 2000);
    } finally {
        botao.disabled = false;
    }
}

async function carregarPaginaInvestimentos() {
    try {
        await Promise.all([
            buscarInvestimentos(),
            buscarResumoInvestimentos(),
            buscarMetaSidebar()
        ]);
    } catch (erro) {
        console.error(
            "Erro ao carregar página de investimentos:",
            erro
        );

        throw erro;
    }
}

document.addEventListener(
    "DOMContentLoaded",
    carregarPaginaInvestimentos
);
