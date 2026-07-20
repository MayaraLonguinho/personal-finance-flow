# Módulo de utilitários
# Funções auxiliares usadas em todo o projeto


def _preferencias_usuario():
    try:
        from b_backend.b_src.k_configuracoes import obter_configuracoes_usuario
        from b_backend.b_src.b_usuario_contexto import obter_usuario_id

        usuario_id = obter_usuario_id()
        if usuario_id is not None:
            return obter_configuracoes_usuario(usuario_id)
    except Exception:
        pass
    return {}


def formatar_moeda(valor, moeda=None):
    """
    Formata um valor numérico para o formato de moeda brasileiro (R$).
    
    Args:
        valor (float, int, Decimal): Valor a ser formatado
        
    Returns:
        str: Valor formatado como R$ X.XXX,XX
    """
    try:
        # Converte para float se necessário
        valor_float = float(valor)
        
        moeda = moeda or _preferencias_usuario().get("moeda", "BRL")
        if moeda == "USD":
            return f"$ {valor_float:,.2f}"

        valor_formatado = f"{valor_float:,.2f}".replace('.', '_').replace(',', '.').replace('_', ',')
        if moeda == "EUR":
            return f"{valor_formatado} €"
        return f"R$ {valor_formatado}"
    except (ValueError, TypeError):
        return formatar_moeda(0, moeda=moeda or "BRL")


def formatar_data(valor, formato=None):
    if not valor:
        return "-"

    texto = str(valor)[:10]
    partes = texto.split("-")
    if len(partes) != 3:
        return texto

    ano, mes, dia = partes
    formato = formato or _preferencias_usuario().get("formato_data", "DD/MM/YYYY")
    if formato == "MM/DD/YYYY":
        return f"{mes}/{dia}/{ano}"
    if formato == "YYYY-MM-DD":
        return f"{ano}-{mes}-{dia}"
    return f"{dia}/{mes}/{ano}"
