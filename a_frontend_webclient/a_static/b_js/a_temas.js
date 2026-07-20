(function () {
    const temas = [
        "theme-blue",
        "theme-pink",
        "theme-green",
        "theme-red",
        "theme-dark"
    ];

    const configuracoes = window.PFF_CONFIG || {};
    const csrfToken = window.PFF_CSRF_TOKEN;
    const locaisMoeda = {
        BRL: "pt-BR",
        USD: "en-US",
        EUR: "de-DE"
    };

    function formatarMoeda(valor) {
        const moeda = configuracoes.moeda || "BRL";
        return new Intl.NumberFormat(locaisMoeda[moeda] || "pt-BR", {
            style: "currency",
            currency: moeda
        }).format(Number(valor) || 0);
    }

    function partesData(dataTexto) {
        if (!dataTexto) return null;
        const texto = String(dataTexto).substring(0, 10);
        const correspondencia = /^(\d{4})-(\d{2})-(\d{2})$/.exec(texto);
        if (correspondencia) {
            return {
                ano: correspondencia[1],
                mes: correspondencia[2],
                dia: correspondencia[3]
            };
        }

        const data = new Date(dataTexto);
        if (Number.isNaN(data.getTime())) return null;
        return {
            ano: String(data.getFullYear()),
            mes: String(data.getMonth() + 1).padStart(2, "0"),
            dia: String(data.getDate()).padStart(2, "0")
        };
    }

    function formatarData(dataTexto) {
        const partes = partesData(dataTexto);
        if (!partes) return dataTexto ? String(dataTexto) : "-";

        switch (configuracoes.formato_data || "DD/MM/YYYY") {
            case "MM/DD/YYYY":
                return `${partes.mes}/${partes.dia}/${partes.ano}`;
            case "YYYY-MM-DD":
                return `${partes.ano}-${partes.mes}-${partes.dia}`;
            default:
                return `${partes.dia}/${partes.mes}/${partes.ano}`;
        }
    }

    function confirmarExclusao(mensagem) {
        if (configuracoes.confirmar_exclusao === false) return true;
        return window.confirm(mensagem);
    }

    let toastTimeout = null;

    function mostrarNotificacao(titulo, mensagem, tipo = 'success', duracao = 5000) {
        const toast = document.getElementById('toast-notification');
        const toastTitle = document.getElementById('toast-title');
        const toastBody = document.getElementById('toast-body');
        const toastIcon = document.getElementById('toast-icon');

        if (!toast || !toastTitle || !toastBody || !toastIcon) {
            console.warn('Elementos do toast não encontrados');
            return;
        }

        // Remove classes anteriores
        toast.classList.remove('success', 'error', 'warning', 'info');
        toast.classList.add(tipo);

        // Define conteúdo
        toastTitle.textContent = titulo;
        toastBody.textContent = mensagem;

        // Define ícone
        switch (tipo) {
            case 'success':
                toastIcon.textContent = '✓';
                break;
            case 'error':
                toastIcon.textContent = '✕';
                break;
            case 'warning':
                toastIcon.textContent = '⚠';
                break;
            case 'info':
                toastIcon.textContent = 'ℹ';
                break;
            default:
                toastIcon.textContent = '✓';
        }

        // Mostra toast
        toast.classList.add('show');

        // Limpa timeout anterior se existir
        if (toastTimeout) {
            clearTimeout(toastTimeout);
        }

        // Auto-dismiss após duração especificada
        if (duracao > 0) {
            toastTimeout = setTimeout(() => {
                fecharNotificacao();
            }, duracao);
        }
    }

    function fecharNotificacao() {
        const toast = document.getElementById('toast-notification');
        if (toast) {
            toast.classList.remove('show');
        }
        if (toastTimeout) {
            clearTimeout(toastTimeout);
            toastTimeout = null;
        }
    }

    function aplicarTema(tema) {
        const temaEscolhido = temas.includes(tema) ? tema : "theme-blue";
        document.body.classList.remove(...temas);
        document.body.classList.add(temaEscolhido);
    }

    function aplicarCardsVisiveis() {
        const cards = Array.isArray(configuracoes.cards_visiveis)
            ? configuracoes.cards_visiveis
            : ["resumo_financeiro", "investimentos", "transacoes_recentes", "meta_economia"];

        document.querySelectorAll("[data-config-card]").forEach(elemento => {
            elemento.hidden = !cards.includes(elemento.dataset.configCard);
        });
    }

    async function salvarPreferencias(dados) {
        const resposta = await fetch("/api/configuracoes", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(dados)
        });
        const resultado = await resposta.json();
        if (!resposta.ok) {
            throw new Error(resultado.erro || "Não foi possível salvar as configurações.");
        }
        Object.assign(configuracoes, resultado.configuracoes || {});
        return configuracoes;
    }

    window.PFF = {
        configuracoes,
        csrfToken,
        formatarMoeda,
        formatarData,
        confirmarExclusao,
        aplicarTema,
        aplicarCardsVisiveis,
        salvarPreferencias,
        mostrarNotificacao,
        fecharNotificacao
    };

    aplicarTema(configuracoes.tema);
    document.addEventListener("DOMContentLoaded", function () {
        aplicarTema(configuracoes.tema);
        aplicarCardsVisiveis();
    });
})();
