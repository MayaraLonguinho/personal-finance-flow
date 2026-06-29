# Módulo de métricas
# Responsável por calcular indicadores financeiros a partir do MySQL

import pandas as pd
from sqlalchemy import text
from src.load import obter_engine
from src.utils import formatar_moeda
from src.usuario_contexto import obter_usuario_id


def _resolver_usuario_id(usuario_id=None):
    if usuario_id is not None:
        return usuario_id

    contexto_usuario_id = obter_usuario_id()
    if contexto_usuario_id is not None:
        return contexto_usuario_id

    raise PermissionError("Usuário não autenticado para consultar dados financeiros")


def buscar_transacoes(usuario_id=None):
    """
    Busca todas as transações da tabela transacoes no MySQL.
    
    Returns:
        pd.DataFrame: DataFrame com as transações
    """
    usuario_id = _resolver_usuario_id(usuario_id)

    # Obtém o engine de conexão
    engine = obter_engine()
    
    # Executa a query e retorna como DataFrame
    query = text("SELECT * FROM transacoes WHERE status = 'confirmado' AND usuario_id = :usuario_id")
    df = pd.read_sql(query, engine, params={'usuario_id': usuario_id})
    
    return df


def _normalizar_categoria(valor):
    if valor is None:
        return "Outros"

    texto = str(valor).strip()
    return texto or "Outros"


def _preparar_gastos_por_categoria(df):
    saidas = df[df['tipo'] == 'saida'].copy()
    if saidas.empty:
        return pd.DataFrame(columns=['categoria', 'valor'])

    saidas['categoria'] = saidas['categoria'].apply(_normalizar_categoria)
    gastos_por_categoria = (
        saidas.groupby('categoria', as_index=False)['valor']
        .sum()
        .sort_values(by='valor', ascending=False, kind='stable')
        .reset_index(drop=True)
    )
    return gastos_por_categoria


def _preparar_evolucao_mensal(df):
    colunas = ['mes_ano', 'entrada', 'saida', 'investimento', 'saldo']
    periodo_atual = pd.Timestamp.today().to_period('M')
    periodos = pd.period_range(end=periodo_atual, periods=5, freq='M')

    if df.empty:
        return pd.DataFrame([
            {
                'mes_ano': str(periodo),
                'entrada': 0.0,
                'saida': 0.0,
                'investimento': 0.0,
                'saldo': 0.0,
            }
            for periodo in periodos
        ], columns=colunas)

    df_local = df.copy()
    df_local['data_transacao'] = pd.to_datetime(df_local['data_transacao'], errors='coerce')
    df_local = df_local.dropna(subset=['data_transacao'])

    if df_local.empty:
        return pd.DataFrame([
            {
                'mes_ano': str(periodo),
                'entrada': 0.0,
                'saida': 0.0,
                'investimento': 0.0,
                'saldo': 0.0,
            }
            for periodo in periodos
        ], columns=colunas)

    df_local['mes_ano'] = df_local['data_transacao'].dt.to_period('M')
    df_local = df_local[df_local['mes_ano'].isin(periodos)]

    if df_local.empty:
        return pd.DataFrame([
            {
                'mes_ano': str(periodo),
                'entrada': 0.0,
                'saida': 0.0,
                'investimento': 0.0,
                'saldo': 0.0,
            }
            for periodo in periodos
        ], columns=colunas)

    evolucao = (
        df_local.groupby(['mes_ano', 'tipo'])['valor']
        .sum()
        .unstack(fill_value=0)
        .reindex(periodos, fill_value=0)
        .round(2)
    )

    for coluna in ['entrada', 'saida', 'investimento']:
        if coluna not in evolucao.columns:
            evolucao[coluna] = 0.0

    evolucao = evolucao[['entrada', 'saida', 'investimento']]
    evolucao['saldo'] = (
        evolucao['entrada']
        - evolucao['saida']
        - evolucao['investimento']
    )
    evolucao = evolucao.reset_index()
    evolucao['mes_ano'] = evolucao['mes_ano'].astype(str)
    return evolucao[colunas]


def calcular_resumo_financeiro(usuario_id=None):
    """
    Calcula o resumo financeiro geral.
    
    Returns:
        dict: Dicionário com total de entradas, saídas, investimentos, saldo e quantidade de transações
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    df = buscar_transacoes(usuario_id=usuario_id)
    
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


def calcular_gastos_por_categoria(usuario_id=None):
    """
    Calcula o total de saídas agrupado por categoria.
    
    Returns:
        pd.DataFrame: DataFrame com gastos por categoria
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    df = buscar_transacoes(usuario_id=usuario_id)
    
    return _preparar_gastos_por_categoria(df)


def calcular_movimento_por_tipo(usuario_id=None):
    """
    Calcula o total agrupado por tipo de transação.
    
    Returns:
        pd.DataFrame: DataFrame com movimento por tipo
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    df = buscar_transacoes(usuario_id=usuario_id)
    
    # Agrupa por tipo e soma os valores
    movimento_por_tipo = df.groupby('tipo')['valor'].sum().reset_index()
    
    return movimento_por_tipo


def calcular_evolucao_mensal(usuario_id=None):
    """
    Calcula a evolução mensal de entradas, saídas, investimentos e saldo.
    
    Returns:
        pd.DataFrame: DataFrame com evolução mensal
    """
    usuario_id = _resolver_usuario_id(usuario_id)

    df = buscar_transacoes(usuario_id=usuario_id)
    return _preparar_evolucao_mensal(df)


def gerar_metricas_dashboard(usuario_id=None):
    """
    Reúne todas as métricas em um dicionário simples para a dashboard.
    
    Returns:
        dict: Dicionário com todas as métricas calculadas
    """
    # Calcula o resumo financeiro usando apenas transações do usuário
    # Ajusta chamadas para passar usuario_id às funções que consultam o banco
    df = buscar_transacoes(usuario_id=usuario_id)

    # Calcula o resumo financeiro a partir do DataFrame filtrado
    total_entradas = df[df['tipo'] == 'entrada']['valor'].sum()
    total_saidas = df[df['tipo'] == 'saida']['valor'].sum()
    total_investido = df[df['tipo'] == 'investimento']['valor'].sum()
    saldo_final = total_entradas - total_saidas - total_investido
    resumo = {
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'total_investido': total_investido,
        'saldo_final': saldo_final,
        'qtd_transacoes': len(df)
    }
    
    gastos_categoria = _preparar_gastos_por_categoria(df)

    # Calcula movimento por tipo
    movimento_tipo = df.groupby('tipo')['valor'].sum().reset_index()

    evolucao_mensal = _preparar_evolucao_mensal(df)
    
    return {
        'resumo_financeiro': resumo,
        'gastos_por_categoria': gastos_categoria.to_dict('records'),
        'movimento_por_tipo': movimento_tipo.to_dict('records'),
        'evolucao_mensal': evolucao_mensal.to_dict('records')
    }


def gerar_insights(usuario_id=None):
    """
    Gera insights baseados nos dados reais das transações.
    
    Returns:
        list: Lista de insights com tipo, título e mensagem
    """
    insights = []
    
    usuario_id = _resolver_usuario_id(usuario_id)

    # Busca as transações do usuário
    df = buscar_transacoes(usuario_id=usuario_id)
    
    # Se não houver transações, retorna insight informativo
    if df.empty:
        return [{
            'tipo': 'informativo',
            'titulo': 'Sem dados',
            'mensagem': 'Nenhuma transação registrada ainda.'
        }]
    
    # Calcula resumo financeiro a partir do DataFrame filtrado
    resumo = {
        'total_entradas': df[df['tipo'] == 'entrada']['valor'].sum(),
        'total_saidas': df[df['tipo'] == 'saida']['valor'].sum(),
        'total_investido': df[df['tipo'] == 'investimento']['valor'].sum(),
        'saldo_final': df[df['tipo'] == 'entrada']['valor'].sum() - df[df['tipo'] == 'saida']['valor'].sum() - df[df['tipo'] == 'investimento']['valor'].sum(),
        'qtd_transacoes': len(df)
    }
    
    # 1. Identificar categoria com maior gasto
    gastos_categoria = calcular_gastos_por_categoria(usuario_id=usuario_id)
    if not gastos_categoria.empty:
        maior_gasto = gastos_categoria.loc[gastos_categoria['valor'].idxmax()]
        valor_formatado = formatar_moeda(maior_gasto['valor'])
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
            'mensagem': f"Você tem {formatar_moeda(total_saidas)} em saídas, mas nenhuma entrada registrada."
        })
    
    # 3. Informar se o saldo está positivo, negativo ou zerado
    saldo_final = resumo['saldo_final']
    if saldo_final > 0:
        insights.append({
            'tipo': 'positivo',
            'titulo': 'Saldo positivo',
            'mensagem': f"Seu saldo está positivo em {formatar_moeda(saldo_final)}."
        })
    elif saldo_final < 0:
        insights.append({
            'tipo': 'negativo',
            'titulo': 'Saldo negativo',
            'mensagem': f"Seu saldo está negativo em {formatar_moeda(saldo_final)}."
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
            'mensagem': f"Você tem {formatar_moeda(total_investido)} em investimentos registrados."
        })
    else:
        insights.append({
            'tipo': 'informativo',
            'titulo': 'Sem investimentos',
            'mensagem': 'Nenhum investimento foi registrado no período.'
        })
    
    # Limita a no máximo 4 insights
    return insights[:4]


def buscar_ultimas_transacoes(limite=5, usuario_id=None):
    """
    Busca as últimas transações confirmadas no banco MySQL.
    Retorna uma lista de dicionários para ser usada pela API.
    """
    engine = obter_engine()

    usuario_id = _resolver_usuario_id(usuario_id)

    query = f"""
        SELECT
            data_transacao,
            descricao,
            categoria,
            tipo,
            valor
        FROM transacoes
        WHERE status = 'confirmado' AND usuario_id = :usuario_id
        ORDER BY data_transacao DESC, id DESC
        LIMIT {limite}
    """

    df = pd.read_sql(text(query), engine, params={'usuario_id': usuario_id})

    if df.empty:
        return []

    df["data_transacao"] = df["data_transacao"].astype(str)

    return df.to_dict(orient="records")
