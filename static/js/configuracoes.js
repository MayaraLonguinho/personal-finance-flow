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
            const resposta = await fetch("/api/configuracoes/restaurar", { method: "POST" });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro);
            window.location.reload();
        } catch (erro) {
            mostrarMensagem(erro.message || "Não foi possível restaurar os padrões.", true);
        }
    });
})();
