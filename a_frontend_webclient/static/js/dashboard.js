
function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarData(dataTexto) {
    return window.PFF.formatarData(dataTexto);
}

let confirmacaoCallback = null;
let modalMensagemCallback = null;

function mostrarModalMensagem(titulo, conteudoHTML, onFechar = null) {
    const modal = document.getElementById('modal-mensagem');
    const modalTitulo = document.getElementById('modal-mensagem-titulo');
    const modalConteudo = document.getElementById('modal-mensagem-conteudo');

    if (!modal || !modalTitulo || !modalConteudo) {
        return;
    }

    modalTitulo.textContent = titulo;
    modalConteudo.innerHTML = conteudoHTML;
    modalMensagemCallback = onFechar;
    modal.classList.add('show');
}

function fecharModalMensagem() {
    const modal = document.getElementById('modal-mensagem');
    if (modal) {
        modal.classList.remove('show');
    }
    if (modalMensagemCallback) {
        modalMensagemCallback();
        modalMensagemCallback = null;
    }
}

function mostrarModalConfirmacao(titulo, mensagem, onConfirm) {
    const modal = document.getElementById('modal-confirmacao');
    const modalTitulo = document.getElementById('modal-confirmacao-titulo');
    const modalMensagem = document.getElementById('modal-confirmacao-mensagem');
    const btnConfirmar = document.getElementById('modal-confirmacao-btn-confirmar');

    if (!modal || !modalTitulo || !modalMensagem || !btnConfirmar) {
        return;
    }

    modalTitulo.textContent = titulo;
    modalMensagem.textContent = mensagem;
    confirmacaoCallback = onConfirm;
    modal.classList.add('show');
}

function fecharModalConfirmacao(confirmado) {
    const modal = document.getElementById('modal-confirmacao');
    if (modal) {
        modal.classList.remove('show');
    }
    if (confirmado && confirmacaoCallback) {
        confirmacaoCallback();
    }
    confirmacaoCallback = null;
}

document.getElementById('modal-confirmacao-btn-confirmar').addEventListener('click', function () {
    fecharModalConfirmacao(true);
});

function obterCorCss(nomeVariavel, fallback) {
    const valor = getComputedStyle(document.body)
        .getPropertyValue(nomeVariavel)
        .trim();
    return valor || fallback;
}

function formatarMesAno(mesAno) {
    if (!mesAno) {
        return "-";
    }

    const [ano, mes] = String(mesAno).split("-");
    if (!ano || !mes) {
        return String(mesAno);
    }

    const data = new Date(Number(ano), Number(mes) - 1, 1);
    return new Intl.DateTimeFormat("pt-BR", {
        month: "short",
        year: "2-digit"
    }).format(data);
}

function prepararTopCategorias(dados) {
    return (dados || [])
        .map(item => ({
            categoria: item.categoria || "Outros",
            valor: Number(item.valor) || 0
        }))
        .filter(item => item.valor > 0)
        .sort((a, b) => b.valor - a.valor)
        .slice(0, 5);
}

function valorSeguro(valor) {
    return Math.max(0, Number(valor) || 0);
}

function renderizarEstadoVazioGrafico(canvasId, mensagem) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        return false;
    }

    const chartBox = canvas.closest(".chart-box");
    if (!chartBox) {
        return false;
    }

    chartBox.innerHTML = `
        <div class="empty-chart-state">
            <p class="empty-text">${mensagem}</p>
        </div>
    `;
    return true;
}

async function buscarMetricas() {
    try {
        const resposta = await fetch("/api/metricas", {
            cache: "no-store"
        });

        if (!resposta.ok) {
            throw new Error("Erro ao buscar métricas da API.");
        }

        const dados = await resposta.json();

        preencherCards(dados.resumo_financeiro || {});
        criarGraficoCategorias(dados.gastos_por_categoria || []);
        criarGraficoTipos(dados.gastos_por_categoria || []);
        criarGraficoEvolucao(dados.evolucao_mensal || []);
        preencherInsights(dados.insights || []);

    } catch (erro) {
        console.error("Erro ao carregar visão geral:", erro);
        window.PFF.mostrarNotificacao(
            "Erro ao carregar visão geral",
            "Não foi possível carregar os dados da Visão Geral.",
            "error"
        );
    }
}

function preencherCards(resumo) {
    const totalEntradas = document.getElementById("total-entradas");
    const totalSaidas = document.getElementById("total-saidas");
    const saldoFinal = document.getElementById("saldo-final");
    const quantidadeTransacoes = document.getElementById("qtd-transacoes");

    if (totalEntradas) {
        totalEntradas.textContent = formatarMoeda(
            resumo.total_entradas
        );
    }

    if (totalSaidas) {
        totalSaidas.textContent = formatarMoeda(
            resumo.total_saidas
        );
    }

    if (saldoFinal) {
        const valorSaldo = Number(resumo.saldo_final ?? resumo.saldo) || 0;
        saldoFinal.textContent = formatarMoeda(valorSaldo);
        atualizarAparenciaCardSaldo(valorSaldo);
    }

    if (quantidadeTransacoes) {
        quantidadeTransacoes.textContent =
            resumo.qtd_transacoes ??
            resumo.quantidade_transacoes ??
            0;
    }
}

function atualizarAparenciaCardSaldo(valorSaldo) {
    const cardSaldo = document.querySelector(".summary-card.saldo");
    if (!cardSaldo) return;

    // Remove classes anteriores
    cardSaldo.classList.remove("saldo-positivo", "saldo-negativo");

    // Aplica classe baseada no valor
    if (valorSaldo > 0) {
        cardSaldo.classList.add("saldo-positivo");
    } else if (valorSaldo < 0) {
        cardSaldo.classList.add("saldo-negativo");
    }
    // Se valor == 0, mantém estilo neutro (sem classe adicional)
}

function preencherInsights(insights) {
    const container = document.getElementById("lista-insights");

    if (!container) {
        return;
    }

    if (!insights || insights.length === 0) {
        container.innerHTML = `
            <div class="insight-item">
                <div class="insight-icon neutral">↗</div>

                <div>
                    <strong>Sem insights</strong>

                    <p>
                        Não há dados suficientes para gerar insights.
                    </p>
                </div>
            </div>
        `;

        return;
    }

    container.innerHTML = insights.map(insight => {
        let iconClass = "neutral";
        let icon = "↗";

        if (insight.tipo === "positivo") {
            iconClass = "positive";
            icon = "↓";
        } else if (
            insight.tipo === "negativo" ||
            insight.tipo === "alerta"
        ) {
            iconClass = "negative";
            icon = "↑";
        }

        return `
            <div class="insight-item">
                <div class="insight-icon ${iconClass}">
                    ${icon}
                </div>

                <div>
                    <strong>
                        ${insight.titulo || "Insight financeiro"}
                    </strong>

                    <p>
                        ${insight.mensagem || ""}
                    </p>
                </div>
            </div>
        `;
    }).join("");
}

function criarGraficoCategorias(dados) {
    const contexto = document.getElementById(
        "grafico-categorias"
    );

    if (!contexto) {
        return;
    }

    const topCategorias = prepararTopCategorias(dados);

    if (topCategorias.length === 0) {
        renderizarEstadoVazioGrafico(
            "grafico-categorias",
            "Nenhum gasto por categoria no período."
        );
        return;
    }

    new Chart(contexto, {
        type: "doughnut",

        data: {
            labels: topCategorias.map(
                item => item.categoria
            ),

            datasets: [
                {
                    data: topCategorias.map(
                        item => Number(item.valor) || 0
                    ),
                    backgroundColor: [
                        "rgba(244, 63, 94, 0.75)",
                        "rgba(59, 130, 246, 0.75)",
                        "rgba(245, 158, 11, 0.75)",
                        "rgba(20, 184, 166, 0.75)",
                        "rgba(139, 92, 246, 0.75)"
                    ],
                    borderWidth: 0
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "58%",

            plugins: {
                legend: {
                    position: "bottom",

                    labels: {
                        boxWidth: 12,
                        boxHeight: 8,
                        padding: 8,

                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

function criarGraficoTipos(dados) {
    const contexto = document.getElementById(
        "grafico-tipos"
    );

    if (!contexto) {
        return;
    }

    const topCategorias = prepararTopCategorias(dados);

    if (topCategorias.length === 0) {
        renderizarEstadoVazioGrafico(
            "grafico-tipos",
            "Nenhum gasto por categoria no período."
        );
        return;
    }

    new Chart(contexto, {
        type: "bar",

        data: {
            labels: topCategorias.map(
                item => item.categoria
            ),

            datasets: [
                {
                    label: "Valor gasto",

                    data: topCategorias.map(
                        item => Number(item.valor) || 0
                    ),

                    backgroundColor: [
                        "rgba(244, 63, 94, 0.45)",
                        "rgba(59, 130, 246, 0.45)",
                        "rgba(245, 158, 11, 0.45)",
                        "rgba(20, 184, 166, 0.45)",
                        "rgba(139, 92, 246, 0.45)"
                    ],

                    borderColor: [
                        "rgba(244, 63, 94, 1)",
                        "rgba(59, 130, 246, 1)",
                        "rgba(245, 158, 11, 1)",
                        "rgba(20, 184, 166, 1)",
                        "rgba(139, 92, 246, 1)"
                    ],

                    borderWidth: 2,
                    borderRadius: 8,
                    barThickness: 22,
                    maxBarThickness: 26
                }
            ]
        },

        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                }
            },

            scales: {
                x: {
                    beginAtZero: true
                },

                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function criarGraficoEvolucao(dados) {
    const contexto = document.getElementById(
        "grafico-evolucao"
    );

    if (!contexto) {
        return;
    }

    new Chart(contexto, {
        type: "bar",

        data: {
            labels: dados.map(
                item => formatarMesAno(item.mes_ano)
            ),

            datasets: [
                {
                    type: "bar",
                    label: "Entradas",

                    data: dados.map(
                        item => valorSeguro(item.entrada)
                    ),

                    backgroundColor:
                        "rgba(34, 197, 94, 0.45)",

                    borderColor:
                        "rgba(34, 197, 94, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 10,
                    maxBarThickness: 14
                },

                {
                    type: "bar",
                    label: "Saídas",

                    data: dados.map(
                        item => valorSeguro(item.saida)
                    ),

                    backgroundColor:
                        "rgba(244, 63, 94, 0.45)",

                    borderColor:
                        "rgba(244, 63, 94, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 10,
                    maxBarThickness: 14
                },

                {
                    type: "bar",
                    label: "Saldo",

                    data: dados.map(
                        item => valorSeguro(item.saldo)
                    ),

                    backgroundColor:
                        "rgba(37, 99, 235, 0.12)",

                    borderColor:
                        "rgba(37, 99, 235, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 10,
                    maxBarThickness: 14
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            interaction: {
                mode: "index",
                intersect: false
            },

            plugins: {
                legend: {
                    position: "bottom",

                    labels: {
                        boxWidth: 10,
                        boxHeight: 8,
                        padding: 8,

                        font: {
                            size: 10
                        }
                    }
                }
            },

            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },

                y: {
                    beginAtZero: true,
                    min: 0
                }
            }
        }
    });
}

function configurarTrocaDeTema() {
    const seletorTema = document.getElementById(
        "theme-selector"
    );

    if (!seletorTema) {
        return;
    }

    const temaSalvo = window.PFF.configuracoes.tema || "theme-blue";

    document.body.className = temaSalvo;
    seletorTema.value = temaSalvo;

    seletorTema.addEventListener(
        "change",
        async function () {
            const temaAnterior = window.PFF.configuracoes.tema;
            window.PFF.aplicarTema(this.value);
            try {
                await window.PFF.salvarPreferencias({ tema: this.value });
            } catch (erro) {
                window.PFF.aplicarTema(temaAnterior);
                this.value = temaAnterior;
                window.PFF.mostrarNotificacao(
                    "Erro",
                    erro.message,
                    "error"
                );
            }
        }
    );
}

function obterClasseTag(categoria) {
    const categoriaNormalizada = String(
        categoria || ""
    ).toLowerCase();

    if (
        categoriaNormalizada.includes("salário") ||
        categoriaNormalizada.includes("salario")
    ) {
        return "tag-green";
    }

    if (
        categoriaNormalizada.includes("alimentação") ||
        categoriaNormalizada.includes("alimentacao")
    ) {
        return "tag-blue";
    }

    if (categoriaNormalizada.includes("casa")) {
        return "tag-pink";
    }

    if (categoriaNormalizada.includes("transporte")) {
        return "tag-cyan";
    }

    if (categoriaNormalizada.includes("lazer")) {
        return "tag-orange";
    }

    return "tag-blue";
}

async function carregarUltimasTransacoes() {
    const tabela = document.getElementById(
        "tabela-transacoes"
    );

    if (!tabela) {
        return;
    }

    try {
        const resposta = await fetch(
            "/api/transacoes",
            {
                cache: "no-store"
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Erro ao buscar transações."
            );
        }

        const transacoes = await resposta.json();

        if (!transacoes.length) {
            tabela.innerHTML = `
                <tr>
                    <td colspan="5">
                        Nenhuma transação encontrada.
                    </td>
                </tr>
            `;

            return;
        }

        tabela.innerHTML = transacoes.map(
            transacao => {
                const tipoClasse =
                    transacao.tipo === "entrada"
                        ? "entrada-text"
                        : "saida-text";

                const tipoTexto =
                    transacao.tipo === "entrada"
                        ? "Entrada"
                        : "Saída";

                const tagClasse = obterClasseTag(
                    transacao.categoria
                );

                return `
                    <tr>
                        <td>
                            ${formatarData(
                    transacao.data_transacao
                )}
                        </td>

                        <td>
                            ${transacao.descricao || "-"}
                        </td>

                        <td>
                            <span class="tag ${tagClasse}">
                                ${transacao.categoria || "Outros"}
                            </span>
                        </td>

                        <td>
                            <span class="type ${tipoClasse}">
                                ${tipoTexto}
                            </span>
                        </td>

                        <td class="value ${tipoClasse}">
                            ${formatarMoeda(
                    transacao.valor
                )}
                        </td>
                    </tr>
                `;
            }
        ).join("");

    } catch (erro) {
        console.error(
            "Erro ao carregar transações:",
            erro
        );

        tabela.innerHTML = `
            <tr>
                <td colspan="5">
                    Erro ao carregar transações.
                </td>
            </tr>
        `;
    }
}

function configurarUploadPlanilha() {
    const inputPlanilha = document.getElementById(
        "input-planilha"
    );

    const botaoImportar = document.getElementById(
        "btn-importar-planilha"
    );

    if (!inputPlanilha || !botaoImportar) {
        console.error(
            "Botão ou campo de upload não encontrado."
        );

        return;
    }

    botaoImportar.addEventListener(
        "click",
        function () {
            inputPlanilha.click();
        }
    );

    inputPlanilha.addEventListener(
        "change",
        async function () {
            const arquivo = inputPlanilha.files[0];

            if (!arquivo) {
                return;
            }

            if (
                !arquivo.name
                    .toLowerCase()
                    .endsWith(".csv")
            ) {
                mostrarToast("Erro", "Selecione um arquivo CSV.", "error");

                inputPlanilha.value = "";

                return;
            }

            const formData = new FormData();

            formData.append(
                "arquivo",
                arquivo
            );
            formData.append(
                "csrf_token",
                window.PFF.csrfToken
            );

            const textoOriginal =
                botaoImportar.textContent;

            botaoImportar.textContent =
                "Importando...";

            botaoImportar.disabled = true;

            try {
                const resposta = await fetch(
                    "/api/upload",
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": window.PFF.csrfToken
                        },
                        body: formData
                    }
                );

                const resultado =
                    await resposta.json();

                if (!resposta.ok) {
                    throw new Error(
                        resultado.detalhe ||
                        resultado.erro ||
                        "Não foi possível importar a planilha."
                    );
                }

                let conteudoHTML = '<p><strong>Planilha processada com sucesso</strong></p>';

                if (resultado.recebidos !== undefined) {
                    conteudoHTML += `<p>Registros recebidos: ${resultado.recebidos}</p>`;
                }
                if (resultado.importados !== undefined) {
                    conteudoHTML += `<p>Registros inseridos: ${resultado.importados}</p>`;
                }
                if (resultado.tratados !== undefined) {
                    conteudoHTML += `<p>Registros tratados: ${resultado.tratados}</p>`;
                }
                if (resultado.ignorados !== undefined) {
                    conteudoHTML += `<p>Duplicados ignorados: ${resultado.ignorados}</p>`;
                }

                mostrarModalMensagem("Importação Concluída", conteudoHTML, function () {
                    window.location.reload();
                });

            } catch (erro) {
                console.error(
                    "Erro no upload:",
                    erro
                );

                window.PFF.mostrarNotificacao(
                    "Erro ao importar planilha",
                    erro.message,
                    "error"
                );

            } finally {
                botaoImportar.textContent =
                    textoOriginal;

                botaoImportar.disabled = false;
                inputPlanilha.value = "";
            }
        }
    );
}

function configurarLimpezaDeDados() {
    const botaoLimpar = document.getElementById(
        "btn-limpar-dados"
    );

    if (!botaoLimpar) {
        return;
    }

    botaoLimpar.addEventListener(
        "click",
        async function () {
            mostrarModalConfirmacao(
                "Limpar dados financeiros?",
                "Esta ação removerá todas as transações, investimentos, metas e categorias. Esta ação não poderá ser desfeita.",
                async function () {
                    const textoOriginal =
                        botaoLimpar.textContent;

                    botaoLimpar.textContent =
                        "Limpando...";

                    botaoLimpar.disabled = true;

                    try {
                        const resposta = await fetch(
                            "/api/transacoes/limpar",
                            {
                                method: "DELETE",
                                headers: {
                                    "X-CSRFToken": window.PFF.csrfToken
                                }
                            }
                        );

                        const resultado =
                            await resposta.json();

                        if (!resposta.ok) {
                            throw new Error(
                                resultado.detalhe ||
                                resultado.erro ||
                                "Não foi possível limpar os dados."
                            );
                        }

                        const conteudoHTML = `
                            <p><strong>Dados removidos com sucesso</strong></p>
                            ${resultado.transacoes_removidas ? `<p>Transações removidas: ${resultado.transacoes_removidas}</p>` : ''}
                            ${resultado.investimentos_removidos ? `<p>Investimentos removidos: ${resultado.investimentos_removidos}</p>` : ''}
                            ${resultado.metas_removidas ? `<p>Metas removidas: ${resultado.metas_removidas}</p>` : ''}
                            ${resultado.categorias_removidas ? `<p>Categorias removidas: ${resultado.categorias_removidas}</p>` : ''}
                            ${resultado.mensagem ? `<p>${resultado.mensagem}</p>` : ''}
                        `;
                        mostrarModalMensagem("Limpeza Concluída", conteudoHTML);

                        window.location.reload();

                    } catch (erro) {
                        console.error(
                            "Erro ao limpar dados:",
                            erro
                        );

                        window.PFF.mostrarNotificacao(
                            "Erro ao limpar dados",
                            `Erro ao limpar dados: ${erro.message}`,
                            "error"
                        );

                    } finally {
                        botaoLimpar.textContent =
                            textoOriginal;

                        botaoLimpar.disabled = false;
                    }
                }
            );
        }
    );
}

async function buscarMeta() {
    try {
        const resposta = await fetch(
            "/api/meta",
            {
                cache: "no-store"
            }
        );

        if (!resposta.ok) {
            if (resposta.status === 404) {
                exibirMetaVazia();
                return;
            }

            throw new Error(
                "Erro ao buscar meta."
            );
        }

        const meta = await resposta.json();

        if (!meta || !meta.id) {
            exibirMetaVazia();
            return;
        }

        exibirMeta(meta);

    } catch (erro) {
        console.error(
            "Erro ao carregar meta:",
            erro
        );

        exibirMetaVazia();
    }
}

function exibirMeta(meta) {
    const valorAtual = Number(
        meta.valor_atual
    ) || 0;

    const valorMeta = Number(
        meta.valor_meta
    ) || 0;

    const percentualCalculado =
        valorMeta > 0
            ? (valorAtual / valorMeta) * 100
            : 0;

    const percentual = Number(
        meta.percentual ??
        percentualCalculado
    );

    const percentualBarra = Math.min(
        Math.max(percentual, 0),
        100
    );

    const valorRestante = Math.max(
        Number(
            meta.valor_restante ??
            valorMeta - valorAtual
        ),
        0
    );

    document.getElementById(
        "goal-valor-atual"
    ).textContent = formatarMoeda(
        valorAtual
    );

    document.getElementById(
        "goal-valor-meta"
    ).textContent = `de ${formatarMoeda(
        valorMeta
    )}`;

    document.getElementById(
        "goal-percentual"
    ).textContent = `${percentual.toFixed(0)}%`;

    document.getElementById(
        "goal-progress-bar"
    ).style.width = `${percentualBarra}%`;

    document.getElementById(
        "goal-restante"
    ).textContent = valorRestante > 0
            ? (
                `Faltam ${formatarMoeda(
                    valorRestante
                )} para alcançar sua meta.`
            )
            : "Parabéns! Você alcançou sua meta!";
}

function exibirMetaVazia() {
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
    ).textContent =
        "Nenhuma meta cadastrada.";
}

async function buscarResumoInvestimentosDashboard() {
    const totalInvestidoElemento =
        document.getElementById(
            "total-investido"
        );

    if (!totalInvestidoElemento) {
        console.error(
            'Elemento com id "total-investido" não foi encontrado.'
        );

        return;
    }

    try {
        const resposta = await fetch(
            "/api/investimentos/resumo",
            {
                cache: "no-store"
            }
        );

        const contentType =
            resposta.headers.get(
                "content-type"
            ) || "";

        if (
            !contentType.includes(
                "application/json"
            )
        ) {
            throw new Error(
                "A API de investimentos não retornou JSON."
            );
        }

        const resumo = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resumo.erro ||
                "Não foi possível consultar os investimentos."
            );
        }

        const valorAtualTotal = Number(
            resumo.valor_atual_total
        ) || 0;

        totalInvestidoElemento.textContent =
            formatarMoeda(
                valorAtualTotal
            );

        totalInvestidoElemento.title =
            `Total aplicado: ${formatarMoeda(
                resumo.total_aplicado
            )} | Resultado: ${formatarMoeda(
                resumo.lucro_prejuizo
            )}`;

    } catch (erro) {
        console.error(
            "Erro ao carregar investimentos na Visão Geral:",
            erro
        );

        totalInvestidoElemento.textContent =
            "R$ 0,00";
    }
}

async function carregarDashboard() {
    configurarTrocaDeTema();
    configurarUploadPlanilha();
    configurarLimpezaDeDados();

    await Promise.all([
        buscarMetricas(),
        carregarUltimasTransacoes(),
        buscarMeta()
    ]);

    await buscarResumoInvestimentosDashboard();
}

document.addEventListener(
    "DOMContentLoaded",
    carregarDashboard
);
