# Módulo de transformação de dados
# Responsável por limpar e tratar os dados extraídos

import pandas as pd
from src.categorization import categorizar_dataframe
from src.categorias import obter_regras_categorizacao_do_banco, inicializar_categorias_padrao


def tratar_transacoes(df):
    """
    Trata e limpa os dados das transações.
    
    Args:
        df (pd.DataFrame): DataFrame com dados brutos
        
    Returns:
        tuple: (pd.DataFrame, int) - DataFrame com dados tratados e contador de transações categorizadas
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
    
    # Preenche categorias vazias como "outros" temporariamente
    df['categoria'] = df['categoria'].fillna('outros')
    
    # Inicializa categorias padrão se necessário
    inicializar_categorias_padrao()
    
    # Obtém regras de categorização do banco
    regras_categorizacao = obter_regras_categorizacao_do_banco()
    
    # Aplica categorização automática
    df, contador_categorizadas = categorizar_dataframe(df, regras_categorizacao)
    
    # Remove linhas sem valor
    df = df.dropna(subset=['valor'])
    
    # Remove linhas sem data
    df = df.dropna(subset=['data'])
    
    return df, contador_categorizadas
