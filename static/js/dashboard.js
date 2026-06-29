
function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarData(dataTexto) {
    return window.PFF.formatarData(dataTexto);
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
        console.error("Erro ao carregar dashboard:", erro);
        alert("Não foi possível carregar os dados da dashboard.");
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
        saldoFinal.textContent = formatarMoeda(
            resumo.saldo_final ?? resumo.saldo
        );
    }

    if (quantidadeTransacoes) {
        quantidadeTransacoes.textContent =
            resumo.qtd_transacoes ??
            resumo.quantidade_transacoes ??
            0;
    }
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

    new Chart(contexto, {
        type: "doughnut",

        data: {
            labels: dados.map(
                item => item.categoria
            ),

            datasets: [
                {
                    data: dados.map(
                        item => Number(item.valor) || 0
                    )
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

    const topCategorias = dados
        .slice()
        .sort(
            (a, b) =>
                (Number(b.valor) || 0) -
                (Number(a.valor) || 0)
        )
        .slice(0, 5);

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
                (item, index) =>
                    item.mes_ano ||
                    `Mês ${index + 1}`
            ),

            datasets: [
                {
                    type: "bar",
                    label: "Entradas",

                    data: dados.map(
                        item => Number(item.entrada) || 0
                    ),

                    backgroundColor:
                        "rgba(34, 197, 94, 0.45)",

                    borderColor:
                        "rgba(34, 197, 94, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 18,
                    maxBarThickness: 22
                },

                {
                    type: "bar",
                    label: "Saídas",

                    data: dados.map(
                        item => Number(item.saida) || 0
                    ),

                    backgroundColor:
                        "rgba(244, 63, 94, 0.45)",

                    borderColor:
                        "rgba(244, 63, 94, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 18,
                    maxBarThickness: 22
                },

                {
                    type: "bar",
                    label: "Saldo",

                    data: dados.map(
                        item => Number(item.saldo) || 0
                    ),

                    backgroundColor:
                        "rgba(37, 99, 235, 0.12)",

                    borderColor:
                        "rgba(37, 99, 235, 1)",

                    borderWidth: 2,
                    borderRadius: 7,
                    barThickness: 18,
                    maxBarThickness: 22
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
                    beginAtZero: true
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
                alert(erro.message);
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
                alert("Selecione um arquivo CSV.");

                inputPlanilha.value = "";

                return;
            }

            const formData = new FormData();

            formData.append(
                "arquivo",
                arquivo
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

                alert(
                    `${resultado.mensagem}\n\n` +
                    `Registros recebidos: ${resultado.recebidos}\n` +
                    `Novos registros: ${resultado.importados}\n` +
                    `Duplicados ignorados: ${resultado.ignorados}`
                );

                window.location.reload();

            } catch (erro) {
                console.error(
                    "Erro no upload:",
                    erro
                );

                alert(
                    `Erro ao importar planilha: ${erro.message}`
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
            const confirmou = window.PFF.confirmarExclusao(
                "Tem certeza de que deseja apagar todas as transações? Essa ação não poderá ser desfeita."
            );

            if (!confirmou) {
                return;
            }

            const textoOriginal =
                botaoLimpar.textContent;

            botaoLimpar.textContent =
                "Limpando...";

            botaoLimpar.disabled = true;

            try {
                const resposta = await fetch(
                    "/api/transacoes/limpar",
                    {
                        method: "DELETE"
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

                alert(
                    resultado.mensagem ||
                    "Dados removidos com sucesso."
                );

                window.location.reload();

            } catch (erro) {
                console.error(
                    "Erro ao limpar dados:",
                    erro
                );

                alert(
                    `Erro ao limpar dados: ${erro.message}`
                );

            } finally {
                botaoLimpar.textContent =
                    textoOriginal;

                botaoLimpar.disabled = false;
            }
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
            "Erro ao carregar investimentos na Dashboard:",
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
