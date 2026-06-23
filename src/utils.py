# Módulo de utilitários
# Funções auxiliares usadas em todo o projeto


def formatar_moeda(valor):
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
        
        # Formata com separador de milhar e decimal brasileiro
        return f"R$ {valor_float:,.2f}".replace('.', '_').replace(',', '.').replace('_', ',')
    except (ValueError, TypeError):
        return "R$ 0,00"
