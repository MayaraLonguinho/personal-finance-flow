(function () {
    // Constantes
    const STORAGE_KEY_FONT_SCALE = 'pff_font_scale';
    const STORAGE_KEY_THEME = 'pff_theme';
    const MIN_FONT_SCALE = 0.8;
    const MAX_FONT_SCALE = 1.6;
    const DEFAULT_FONT_SCALE = 1;
    const FONT_SCALE_STEP = 0.1;

    let chartInstances = [];

    /**
     * Aplica a escala visual no conteúdo principal (sidebar permanece fixa).
     * A regra de zoom fica no CSS via --font-scale.
     */
    function applyFontScale(scale) {
        const validScale = Math.max(MIN_FONT_SCALE, Math.min(scale, MAX_FONT_SCALE));

        document.documentElement.style.setProperty('--font-scale', validScale);
        localStorage.setItem(STORAGE_KEY_FONT_SCALE, validScale);

        requestAnimationFrame(resizeChartInstances);

        return validScale;
    }

    /**
     * Redimensiona gráficos registrados após mudança de escala
     */
    function resizeChartInstances() {
        chartInstances.forEach(function (chart) {
            if (chart && typeof chart.resize === 'function') {
                try {
                    chart.resize();
                } catch (error) {
                    /* ignora instâncias já destruídas */
                }
            }
        });
    }

    /**
     * Aumenta o tamanho da fonte
     */
    function increaseFontSize() {
        const currentScale = parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE;
        const newScale = currentScale + FONT_SCALE_STEP;
        applyFontScale(newScale);
        updateAccessibilityButtonStates();
        notifyThemeChange();
    }

    /**
     * Diminui o tamanho da fonte
     */
    function decreaseFontSize() {
        const currentScale = parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE;
        const newScale = currentScale - FONT_SCALE_STEP;
        applyFontScale(newScale);
        updateAccessibilityButtonStates();
        notifyThemeChange();
    }

    /**
     * Restaura o tamanho padrão da fonte
     */
    function resetFontSize() {
        applyFontScale(DEFAULT_FONT_SCALE);
        updateAccessibilityButtonStates();
        notifyThemeChange();
    }

    /**
     * Alterna entre tema claro e escuro
     */
    function toggleDarkMode() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        if (newTheme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem(STORAGE_KEY_THEME, 'dark');
        } else {
            html.removeAttribute('data-theme');
            localStorage.setItem(STORAGE_KEY_THEME, 'light');
        }

        updateAccessibilityButtonStates();
        notifyThemeChange();
    }

    /**
     * Atualiza o estado visual dos botões de acessibilidade
     */
    function updateAccessibilityButtonStates() {
        const fontScale = parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE;
        const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';

        // Desabilita/habilita botões de zoom
        const btnIncrease = document.getElementById('btn-accessibility-increase');
        const btnDecrease = document.getElementById('btn-accessibility-decrease');
        const btnReset = document.getElementById('btn-accessibility-reset');

        if (btnIncrease) {
            btnIncrease.disabled = fontScale >= MAX_FONT_SCALE;
        }
        if (btnDecrease) {
            btnDecrease.disabled = fontScale <= MIN_FONT_SCALE;
        }

        // Atualiza indicador do tema
        const btnTheme = document.getElementById('btn-accessibility-theme');
        if (btnTheme) {
            if (isDarkMode) {
                btnTheme.classList.add('dark-mode-active');
                btnTheme.setAttribute('aria-pressed', 'true');
            } else {
                btnTheme.classList.remove('dark-mode-active');
                btnTheme.setAttribute('aria-pressed', 'false');
            }
        }
    }

    /**
     * Restaura as preferências salvas no localStorage
     */
    function restorePreferences() {
        // Restaurar tamanho de fonte
        const savedFontScale = parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE;
        applyFontScale(savedFontScale);

        // Restaurar tema
        const savedTheme = localStorage.getItem(STORAGE_KEY_THEME) || 'light';
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }

        updateAccessibilityButtonStates();
    }

    /**
     * Emite evento para notificar mudanças no tema/acessibilidade
     */
    function notifyThemeChange() {
        const event = new CustomEvent('pff:theme-changed', {
            detail: {
                isDarkMode: document.documentElement.getAttribute('data-theme') === 'dark',
                fontScale: parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Registra instâncias de gráficos para atualização posterior
     */
    function registerChartInstance(chart) {
        if (chart && chartInstances.indexOf(chart) === -1) {
            chartInstances.push(chart);
        }
    }

    /**
     * Limpa todas as instâncias de gráficos registradas
     */
    function clearChartInstances() {
        chartInstances.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        chartInstances = [];
    }

    /**
     * Configura os botões de acessibilidade
     */
    function setupAccessibilityButtons() {
        const btnIncrease = document.getElementById('btn-accessibility-increase');
        const btnDecrease = document.getElementById('btn-accessibility-decrease');
        const btnReset = document.getElementById('btn-accessibility-reset');
        const btnTheme = document.getElementById('btn-accessibility-theme');

        if (btnIncrease) {
            btnIncrease.addEventListener('click', increaseFontSize);
        }
        if (btnDecrease) {
            btnDecrease.addEventListener('click', decreaseFontSize);
        }
        if (btnReset) {
            btnReset.addEventListener('click', resetFontSize);
        }
        if (btnTheme) {
            btnTheme.addEventListener('click', toggleDarkMode);
        }

        updateAccessibilityButtonStates();
    }

    /**
     * Inicializa o módulo de acessibilidade
     */
    function init() {
        // Restaurar preferências ao carregar
        restorePreferences();

        // Configurar botões quando o DOM estiver pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupAccessibilityButtons);
        } else {
            setupAccessibilityButtons();
        }
    }

    // Expor API global
    window.PFF = window.PFF || {};
    window.PFF.accessibility = {
        increaseFontSize,
        decreaseFontSize,
        resetFontSize,
        toggleDarkMode,
        restorePreferences,
        registerChartInstance,
        clearChartInstances,
        resizeChartInstances,
        updateAccessibilityButtonStates,
        getFontScale: () => parseFloat(localStorage.getItem(STORAGE_KEY_FONT_SCALE)) || DEFAULT_FONT_SCALE,
        isDarkMode: () => document.documentElement.getAttribute('data-theme') === 'dark'
    };

    // Inicializar quando o script for carregado
    init();
})();
