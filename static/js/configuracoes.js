(function () {
    const formulario = document.getElementById("form-configuracoes");
    const botaoRestaurar = document.getElementById("btn-restaurar");
    const seletorTema = document.getElementById("tema");

    function dadosFormulario() {
        return {
            nome: document.getElementById("nome").value.trim(),
            tema: seletorTema.value,
            moeda: document.getElementById("moeda").value,
            formato_data: document.getElementById("formato_data").value,
            qtd_transacoes_recentes: Number(
                document.getElementById("qtd_transacoes_recentes").value
            ),
            confirmar_exclusao: document.getElementById("confirmar_exclusao").checked,
            cards_visiveis: Array.from(
                document.querySelectorAll('input[name="cards_visiveis"]:checked')
            ).map(campo => campo.value)
        };
    }

    function mostrarMensagem(texto, erro) {
        const elemento = document.getElementById("configuracoes-mensagem");
        elemento.textContent = texto;
        elemento.classList.toggle("erro", Boolean(erro));
        elemento.hidden = false;
    }

    seletorTema.addEventListener("change", function () {
        window.PFF.aplicarTema(this.value);
    });

    formulario.addEventListener("submit", async function (evento) {
        evento.preventDefault();
        try {
            await window.PFF.salvarPreferencias(dadosFormulario());
            mostrarMensagem("Configurações salvas com sucesso.", false);
            window.setTimeout(() => window.location.reload(), 500);
        } catch (erro) {
            mostrarMensagem(erro.message, true);
        }
    });

    botaoRestaurar.addEventListener("click", async function () {
        try {
            const resposta = await fetch("/api/configuracoes/restaurar", {
                method: "POST",
                headers: {
                    "X-CSRFToken": window.PFF.csrfToken
                }
            });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro);
            window.location.reload();
        } catch (erro) {
            mostrarMensagem(erro.message || "Não foi possível restaurar os padrões.", true);
        }
    });
})();

function formatarMoedaMeta(valor) {
    if (window.PFF && typeof window.PFF.formatarMoeda === "function") {
        return window.PFF.formatarMoeda(valor);
    }

    return Number(valor || 0).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
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
        exibirMetaSidebar(meta);
    } catch (erro) {
        console.error("Erro ao carregar meta da sidebar:", erro);
        exibirMetaSidebarVazia();
    }
}

function exibirMetaSidebar(meta) {
    const valorAtual = document.getElementById("goal-valor-atual");
    const valorMeta = document.getElementById("goal-valor-meta");
    const percentual = document.getElementById("goal-percentual");
    const barra = document.getElementById("goal-progress-bar");
    const restante = document.getElementById("goal-restante");

    if (!valorAtual || !valorMeta || !percentual || !barra || !restante) {
        return;
    }

    const percentualMeta = Math.min(
        Number(meta.percentual || 0),
        100
    );

    valorAtual.textContent = formatarMoedaMeta(meta.valor_atual);
    valorMeta.textContent = `de ${formatarMoedaMeta(meta.valor_meta)}`;
    percentual.textContent = `${meta.percentual || 0}%`;
    barra.style.width = `${percentualMeta}%`;

    if (Number(meta.valor_restante || 0) > 0) {
        restante.textContent =
            `Faltam ${formatarMoedaMeta(meta.valor_restante)} para alcançar sua meta.`;
    } else {
        restante.textContent = "Parabéns! Você alcançou sua meta!";
    }
}

function exibirMetaSidebarVazia() {
    const valorAtual = document.getElementById("goal-valor-atual");
    const valorMeta = document.getElementById("goal-valor-meta");
    const percentual = document.getElementById("goal-percentual");
    const barra = document.getElementById("goal-progress-bar");
    const restante = document.getElementById("goal-restante");

    if (!valorAtual || !valorMeta || !percentual || !barra || !restante) {
        return;
    }

    valorAtual.textContent = formatarMoedaMeta(0);
    valorMeta.textContent = `de ${formatarMoedaMeta(0)}`;
    percentual.textContent = "0%";
    barra.style.width = "0%";
    restante.textContent = "Nenhuma meta cadastrada.";
}

document.addEventListener("DOMContentLoaded", buscarMetaSidebar);
