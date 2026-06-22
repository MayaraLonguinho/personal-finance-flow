# Módulo de transformação de dados
# Responsável por limpar e tratar os dados extraídos

import pandas as pd


def tratar_transacoes(df):
    """
    Trata e limpa os dados das transações.
    
    Args:
        df (pd.DataFrame): DataFrame com dados brutos
        
    Returns:
        pd.DataFrame: DataFrame com dados tratados
    """
    # Remove linhas duplicadas
    df = df.drop_duplicates()
    
    # Padroniza nomes das colunas para minúsculas
    df.columns = df.columns.str.lower()
    
    # Converte a coluna data para formato de data
    df['data'] = pd.to_datetime(df['data'])
    
    # Converte a coluna valor para número
    df['valor'] = pd.to_numeric(df['valor'])
    
    # Padroniza o campo tipo
    # Mapeia: receita -> entrada, despesa -> saida
    df['tipo'] = df['tipo'].str.lower()
    df['tipo'] = df['tipo'].replace({
        'receita': 'entrada',
        'despesa': 'saida'
    })
    
    # Padroniza o campo status
    # Mapeia: concluído -> confirmado
    df['status'] = df['status'].str.lower()
    df['status'] = df['status'].replace({
        'concluído': 'confirmado',
        'concluido': 'confirmado'
    })
    
    # Preenche categorias vazias como "outros"
    df['categoria'] = df['categoria'].fillna('outros')
    
    # Remove linhas sem valor
    df = df.dropna(subset=['valor'])
    
    # Remove linhas sem data
    df = df.dropna(subset=['data'])
    
    return df
