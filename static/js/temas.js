function aplicarTemaSalvo() {
    const temaSalvo = localStorage.getItem("tema-dashboard") || "theme-blue";

    const temas = [
        "theme-blue",
        "theme-pink",
        "theme-green",
        "theme-red",
        "theme-dark"
    ];

    document.body.classList.remove(...temas);
    document.body.classList.add(temaSalvo);
}

document.addEventListener("DOMContentLoaded", aplicarTemaSalvo);