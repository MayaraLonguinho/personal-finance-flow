function formatarMoeda(valor) {
    return window.PFF.formatarMoeda(valor);
}

function formatarPercentual(valor) {
    return `${(Number(valor) || 0).toFixed(2)
        }%`;
}

function formatarData(dataTexto) {
    return window.PFF.formatarData(dataTexto);
}

function capitalizarTexto(texto) {
    if (!texto) {
        return "-";
    }

    return (
        texto.charAt(0).toUpperCase()
        + texto.slice(1)
    );
}

function escaparHtml(texto) {
    const elemento = document.createElement(
        "div"
    );

    elemento.textContent = texto ?? "-";

    return elemento.innerHTML;
}

function mostrarErroFiltro(mensagem) {
    const erro = document.getElementById(
        "filtro-erro"
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

function validarFiltros() {
    const dataInicio = document.getElementById(
        "data-inicio"
    ).value;

    const dataFim = document.getElementById(
        "data-fim"
    ).value;

    if (
        dataInicio
        && dataFim
        && dataInicio > dataFim
    ) {
        mostrarErroFiltro(
            "A data inicial não pode ser maior "
            + "que a data final."
        );

        return false;
    }

    mostrarErroFiltro("");

    return true;
}

function montarUrlRelatorio() {
    const dataInicio = document.getElementById(
        "data-inicio"
    ).value;

    const dataFim = document.getElementById(
        "data-fim"
    ).value;

    const parametros = new URLSearchParams();

    if (dataInicio) {
        parametros.set(
            "data_inicio",
            dataInicio
        );
    }

    if (dataFim) {
        parametros.set(
            "data_fim",
            dataFim
        );
    }

    const queryString = parametros.toString();

    return queryString
        ? `/api/relatorios?${queryString}`
        : "/api/relatorios";
}

function preencherResumo(resumo) {
    const dados = resumo || {};

    document.getElementById(
        "relatorio-entradas"
    ).textContent = formatarMoeda(
        dados.total_entradas
    );

    document.getElementById(
        "relatorio-saidas"
    ).textContent = formatarMoeda(
        dados.total_saidas
    );

    const saldoElemento = document.getElementById(
        "relatorio-saldo"
    );

    const saldo = Number(
        dados.saldo
    ) || 0;

    saldoElemento.textContent = formatarMoeda(
        saldo
    );

    saldoElemento.style.color = saldo < 0
        ? "#ef4444"
        : "#16a34a";

    document.getElementById(
        "relatorio-investimentos"
    ).textContent = formatarMoeda(
        dados.total_investido
    );

    document.getElementById(
        "relatorio-quantidade"
    ).textContent = (
            Number(
                dados.quantidade_transacoes
            )
            || 0
        );
}

function preencherResumoCarteira(
    investimentos
) {
    const carteira = investimentos || {};

    const totalAplicado = Number(
        carteira.total_aplicado
    ) || 0;

    const valorAtual = Number(
        carteira.valor_atual_total
    ) || 0;

    const resultado = Number(
        carteira.lucro_prejuizo
    ) || 0;

    const rentabilidade = Number(
        carteira.rentabilidade_total
    ) || 0;

    const quantidadeAtivos = Number(
        carteira.quantidade_ativos
    ) || 0;

    const aplicadoElemento = document.getElementById(
        "relatorio-carteira-aplicado"
    );

    const atualElemento = document.getElementById(
        "relatorio-carteira-atual"
    );

    const resultadoElemento = document.getElementById(
        "relatorio-carteira-resultado"
    );

    const rentabilidadeElemento = document.getElementById(
        "relatorio-carteira-rentabilidade"
    );

    const ativosElemento = document.getElementById(
        "relatorio-carteira-ativos"
    );

    if (aplicadoElemento) {
        aplicadoElemento.textContent = formatarMoeda(
            totalAplicado
        );
    }

    if (atualElemento) {
        atualElemento.textContent = formatarMoeda(
            valorAtual
        );
    }

    if (resultadoElemento) {
        resultadoElemento.textContent = formatarMoeda(
            resultado
        );

        resultadoElemento.style.color = resultado < 0
            ? "#ef4444"
            : "#16a34a";
    }

    if (rentabilidadeElemento) {
        rentabilidadeElemento.textContent =
            formatarPercentual(
                rentabilidade
            );

        rentabilidadeElemento.style.color =
            rentabilidade < 0
                ? "#ef4444"
                : "#16a34a";
    }

    if (ativosElemento) {
        ativosElemento.textContent =
            quantidadeAtivos;
    }
}

function preencherPeriodo(periodo) {
    const dadosPeriodo = periodo || {};

    const dataInicio = (
        dadosPeriodo.data_inicio
    );

    const dataFim = (
        dadosPeriodo.data_fim
    );

    document.getElementById(
        "periodo-data-inicio"
    ).textContent = dataInicio
            ? formatarData(dataInicio)
            : "Todas";

    document.getElementById(
        "periodo-data-fim"
    ).textContent = dataFim
            ? formatarData(dataFim)
            : "Todas";

    let periodoTexto = (
        "Todos os registros"
    );

    if (dataInicio && dataFim) {
        periodoTexto = (
            `De ${formatarData(dataInicio)} `
            + `até ${formatarData(dataFim)}`
        );
    } else if (dataInicio) {
        periodoTexto = (
            `A partir de ${formatarData(dataInicio)
            }`
        );
    } else if (dataFim) {
        periodoTexto = (
            `Até ${formatarData(dataFim)}`
        );
    }

    document.getElementById(
        "relatorio-periodo"
    ).textContent = periodoTexto;

    document.getElementById(
        "relatorio-gerado-em"
    ).textContent = `${formatarData(new Date())} ${new Date().toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit"
    })}`;
}

function preencherCategorias(categorias) {
    const container = document.getElementById(
        "relatorio-categorias"
    );

    if (
        !categorias
        || categorias.length === 0
    ) {
        container.innerHTML = `
            <p class="empty-text">
                Nenhuma despesa encontrada no período.
            </p>
        `;

        return;
    }

    const maiorValor = Math.max(
        ...categorias.map(
            categoria =>
                Number(categoria.valor)
                || 0
        ),
        1
    );

    container.innerHTML = categorias.map(
        categoria => {
            const valor = Number(
                categoria.valor
            ) || 0;

            const percentual = Math.min(
                Math.max(
                    (valor / maiorValor) * 100,
                    0
                ),
                100
            );

            return `
                <div class="categoria-relatorio-item">
                    <div class="categoria-relatorio-conteudo">
                        <div class="categoria-relatorio-topo">
                            <strong>
                                ${escaparHtml(
                categoria.categoria
            )}
                            </strong>

                            <span>
                                ${categoria.quantidade || 0}
                                transação(ões)
                            </span>
                        </div>

                        <div class="categoria-relatorio-barra">
                            <div
                                class="categoria-relatorio-progresso"
                                style="width: ${percentual}%"
                            ></div>
                        </div>
                    </div>

                    <strong class="categoria-relatorio-valor">
                        ${formatarMoeda(valor)}
                    </strong>
                </div>
            `;
        }
    ).join("");
}

function obterClasseTipo(tipo) {
    if (tipo === "entrada") {
        return "tipo-entrada";
    }

    if (tipo === "investimento") {
        return "tipo-investimento";
    }

    return "tipo-saida";
}

function obterClasseValor(tipo) {
    if (tipo === "entrada") {
        return "valor-entrada";
    }

    if (tipo === "investimento") {
        return "valor-investimento";
    }

    return "valor-saida";
}

function preencherTransacoes(transacoes) {
    const lista = transacoes || [];

    const corpoTabela = document.getElementById(
        "relatorio-transacoes"
    );

    const contador = document.getElementById(
        "contador-registros"
    );

    contador.textContent = (
        `${lista.length} `
        + `${lista.length === 1
            ? "registro"
            : "registros"
        }`
    );

    if (lista.length === 0) {
        corpoTabela.innerHTML = `
            <tr>
                <td colspan="7">
                    Nenhuma transação encontrada no período.
                </td>
            </tr>
        `;

        return;
    }

    corpoTabela.innerHTML = lista.map(
        transacao => {
            const tipo = (
                transacao.tipo
                || "saida"
            );

            return `
                <tr>
                    <td>
                        ${formatarData(
                transacao.data_transacao
            )}
                    </td>

                    <td>
                        ${escaparHtml(
                transacao.descricao
            )}
                    </td>

                    <td>
                        ${escaparHtml(
                transacao.categoria
            )}
                    </td>

                    <td class="${obterClasseTipo(tipo)}">
                        ${capitalizarTexto(tipo)}
                    </td>

                    <td>
                        ${escaparHtml(
                transacao.conta
            )}
                    </td>

                    <td>
                        ${escaparHtml(
                transacao.instituicao
            )}
                    </td>

                    <td class="${obterClasseValor(tipo)}">
                        ${formatarMoeda(
                transacao.valor
            )}
                    </td>
                </tr>
            `;
        }
    ).join("");
}

async function buscarRelatorio() {
    if (!validarFiltros()) {
        return;
    }

    const botao = document.getElementById(
        "btn-gerar-relatorio"
    );

    const textoOriginal = botao.textContent;

    botao.disabled = true;
    botao.textContent = "Gerando...";

    try {
        const resposta = await fetch(
            montarUrlRelatorio(),
            {
                cache: "no-store"
            }
        );

        const contentType = (
            resposta.headers.get(
                "content-type"
            )
            || ""
        );

        if (
            !contentType.includes(
                "application/json"
            )
        ) {
            throw new Error(
                "A API de relatórios não retornou JSON. "
                + `Status: ${resposta.status}.`
            );
        }

        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro
                || "Não foi possível gerar o relatório."
            );
        }

        preencherResumo(
            dados.resumo
        );

        preencherResumoCarteira(
            dados.investimentos
        );

        preencherPeriodo(
            dados.periodo
        );

        preencherCategorias(
            dados.categorias || []
        );

        preencherTransacoes(
            dados.transacoes || []
        );

        mostrarErroFiltro("");

    } catch (erro) {
        console.error(
            "Erro ao buscar relatório:",
            erro
        );

        mostrarErroFiltro(
            erro.message
        );

    } finally {
        botao.disabled = false;
        botao.textContent = textoOriginal;
    }
}

function limparFiltros() {
    document.getElementById(
        "data-inicio"
    ).value = "";

    document.getElementById(
        "data-fim"
    ).value = "";

    mostrarErroFiltro("");

    buscarRelatorio();
}

function imprimirRelatorio() {
    window.print();
}

/* ==========================
   META DA SIDEBAR
========================== */

async function buscarMetaSidebar() {
    try {
        const resposta = await fetch(
            "/api/meta",
            {
                cache: "no-store"
            }
        );

        if (!resposta.ok) {
            if (resposta.status === 404) {
                exibirMetaSidebarVazia();

                return;
            }

            throw new Error(
                "Erro ao buscar meta."
            );
        }

        const meta = await resposta.json();

        if (!meta || !meta.id) {
            exibirMetaSidebarVazia();

            return;
        }

        exibirMetaSidebar(meta);

    } catch (erro) {
        console.error(
            "Erro ao carregar meta da sidebar:",
            erro
        );

        exibirMetaSidebarVazia();
    }
}

function exibirMetaSidebar(meta) {
    const valorAtual = Number(
        meta.valor_atual
    ) || 0;

    const valorMeta = Number(
        meta.valor_meta
    ) || 0;

    const percentualCalculado = valorMeta > 0
        ? (valorAtual / valorMeta) * 100
        : 0;

    const percentual = Number(
        meta.percentual
        ?? percentualCalculado
    );

    const percentualBarra = Math.min(
        Math.max(
            percentual,
            0
        ),
        100
    );

    const valorRestante = Math.max(
        Number(
            meta.valor_restante
            ?? valorMeta - valorAtual
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
    ).textContent = (
            `de ${formatarMoeda(valorMeta)}`
        );

    document.getElementById(
        "goal-percentual"
    ).textContent = (
            `${percentual.toFixed(0)}%`
        );

    document.getElementById(
        "goal-progress-bar"
    ).style.width = (
            `${percentualBarra}%`
        );

    document.getElementById(
        "goal-restante"
    ).textContent = valorRestante > 0
            ? (
                `Faltam ${formatarMoeda(valorRestante)
                } para alcançar sua meta.`
            )
            : "Parabéns! Você alcançou sua meta!";
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
    ).textContent = (
            "Nenhuma meta cadastrada."
        );
}

document.addEventListener(
    "DOMContentLoaded",
    function () {
        buscarRelatorio();
        buscarMetaSidebar();
    }
);
