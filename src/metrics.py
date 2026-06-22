# Módulo de métricas
# Responsável por calcular indicadores financeiros a partir do MySQL

import pandas as pd
from src.load import obter_engine


def buscar_transacoes():
    """
    Busca todas as transações da tabela transacoes no MySQL.
    
    Returns:
        pd.DataFrame: DataFrame com as transações
    """
    # Obtém o engine de conexão
    engine = obter_engine()
    
    # Executa a query e retorna como DataFrame
    query = "SELECT * FROM transacoes WHERE status = 'confirmado'"
    df = pd.read_sql(query, engine)
    
    return df


def calcular_resumo_financeiro():
    """
    Calcula o resumo financeiro geral.
    
    Returns:
        dict: Dicionário com total de entradas, saídas, investimentos, saldo e quantidade de transações
    """
    # Busca as transações
    df = buscar_transacoes()
    
    # Calcula totais por tipo
    total_entradas = df[df['tipo'] == 'entrada']['valor'].sum()
    total_saidas = df[df['tipo'] == 'saida']['valor'].sum()
    total_investido = df[df['tipo'] == 'investimento']['valor'].sum()
    
    # Calcula saldo final
    saldo_final = total_entradas - total_saidas - total_investido
    
    # Quantidade total de transações
    qtd_transacoes = len(df)
    
    return {
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'total_investido': total_investido,
        'saldo_final': saldo_final,
        'qtd_transacoes': qtd_transacoes
    }


def calcular_gastos_por_categoria():
    """
    Calcula o total de saídas agrupado por categoria.
    
    Returns:
        pd.DataFrame: DataFrame com gastos por categoria
    """
    # Busca as transações
    df = buscar_transacoes()
    
    # Filtra apenas saídas e agrupa por categoria
    saidas = df[df['tipo'] == 'saida']
    gastos_por_categoria = saidas.groupby('categoria')['valor'].sum().reset_index()
    
    return gastos_por_categoria


def calcular_movimento_por_tipo():
    """
    Calcula o total agrupado por tipo de transação.
    
    Returns:
        pd.DataFrame: DataFrame com movimento por tipo
    """
    # Busca as transações
    df = buscar_transacoes()
    
    # Agrupa por tipo e soma os valores
    movimento_por_tipo = df.groupby('tipo')['valor'].sum().reset_index()
    
    return movimento_por_tipo


def calcular_evolucao_mensal():
    """
    Calcula a evolução mensal de entradas, saídas, investimentos e saldo.
    
    Returns:
        pd.DataFrame: DataFrame com evolução mensal
    """
    # Busca as transações (já filtra apenas status "confirmado")
    df = buscar_transacoes()
    
    # Extrai o mês e ano da data como texto
    df['mes_ano'] = pd.to_datetime(df['data_transacao']).dt.to_period('M').astype(str)
    
    # Agrupa por mês e tipo
    evolucao = df.groupby(['mes_ano', 'tipo'])['valor'].sum().unstack(fill_value=0)
    
    # Arredonda valores financeiros para 2 casas decimais
    evolucao = evolucao.round(2)
    
    # Calcula o saldo mensal
    if 'entrada' in evolucao.columns:
        evolucao['saldo'] = evolucao.get('entrada', 0) - evolucao.get('saida', 0) - evolucao.get('investimento', 0)
    else:
        evolucao['saldo'] = 0
    
    # Reseta o índice para ter mes_ano como coluna
    evolucao = evolucao.reset_index()
    
    return evolucao


def gerar_metricas_dashboard():
    """
    Reúne todas as métricas em um dicionário simples para a dashboard.
    
    Returns:
        dict: Dicionário com todas as métricas calculadas
    """
    # Calcula o resumo financeiro
    resumo = calcular_resumo_financeiro()
    
    # Calcula gastos por categoria
    gastos_categoria = calcular_gastos_por_categoria()
    
    # Calcula movimento por tipo
    movimento_tipo = calcular_movimento_por_tipo()
    
    # Calcula evolução mensal
    evolucao_mensal = calcular_evolucao_mensal()
    
    return {
        'resumo_financeiro': resumo,
        'gastos_por_categoria': gastos_categoria.to_dict('records'),
        'movimento_por_tipo': movimento_tipo.to_dict('records'),
        'evolucao_mensal': evolucao_mensal.to_dict('records')
    }


def gerar_insights():
    """
    Gera insights baseados nos dados reais das transações.
    
    Returns:
        list: Lista de insights com tipo, título e mensagem
    """
    insights = []
    
    # Busca as transações
    df = buscar_transacoes()
    
    # Se não houver transações, retorna insight informativo
    if df.empty:
        return [{
            'tipo': 'informativo',
            'titulo': 'Sem dados',
            'mensagem': 'Nenhuma transação registrada ainda.'
        }]
    
    # Calcula resumo financeiro
    resumo = calcular_resumo_financeiro()
    
    # 1. Identificar categoria com maior gasto
    gastos_categoria = calcular_gastos_por_categoria()
    if not gastos_categoria.empty:
        maior_gasto = gastos_categoria.loc[gastos_categoria['valor'].idxmax()]
        valor_formatado = f"R$ {maior_gasto['valor']:.2f}"
        insights.append({
            'tipo': 'alerta',
            'titulo': 'Maior gasto',
            'mensagem': f"{maior_gasto['categoria']} foi sua maior categoria de gasto, com {valor_formatado}."
        })
    
    # 2. Calcular percentual das saídas em relação às entradas
    total_entradas = resumo['total_entradas']
    total_saidas = resumo['total_saidas']
    
    if total_entradas > 0:
        percentual_saidas = (total_saidas / total_entradas) * 100
        insights.append({
            'tipo': 'informativo',
            'titulo': 'Percentual de saídas',
            'mensagem': f"Suas saídas representam {percentual_saidas:.0f}% das entradas."
        })
    elif total_saidas > 0:
        insights.append({
            'tipo': 'alerta',
            'titulo': 'Sem entradas',
            'mensagem': f"Você tem R$ {total_saidas:.2f} em saídas, mas nenhuma entrada registrada."
        })
    
    # 3. Informar se o saldo está positivo, negativo ou zerado
    saldo_final = resumo['saldo_final']
    if saldo_final > 0:
        insights.append({
            'tipo': 'positivo',
            'titulo': 'Saldo positivo',
            'mensagem': f"Seu saldo está positivo em R$ {saldo_final:.2f}."
        })
    elif saldo_final < 0:
        insights.append({
            'tipo': 'negativo',
            'titulo': 'Saldo negativo',
            'mensagem': f"Seu saldo está negativo em R$ {saldo_final:.2f}."
        })
    else:
        insights.append({
            'tipo': 'informativo',
            'titulo': 'Saldo zerado',
            'mensagem': 'Seu saldo está zerado.'
        })
    
    # 4. Informar se existem investimentos registrados
    total_investido = resumo['total_investido']
    if total_investido > 0:
        insights.append({
            'tipo': 'positivo',
            'titulo': 'Investimentos',
            'mensagem': f"Você tem R$ {total_investido:.2f} em investimentos registrados."
        })
    else:
        insights.append({
            'tipo': 'informativo',
            'titulo': 'Sem investimentos',
            'mensagem': 'Nenhum investimento foi registrado no período.'
        })
    
    # Limita a no máximo 4 insights
    return insights[:4]


def buscar_ultimas_transacoes(limite=5):
    """
    Busca as últimas transações confirmadas no banco MySQL.
    Retorna uma lista de dicionários para ser usada pela API.
    """
    engine = obter_engine()

    query = f"""
        SELECT
            data_transacao,
            descricao,
            categoria,
            tipo,
            valor
        FROM transacoes
        WHERE status = 'confirmado'
        ORDER BY data_transacao DESC, id DESC
        LIMIT {limite}
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return []

    df["data_transacao"] = df["data_transacao"].astype(str)

    return df.to_dict(orient="records")