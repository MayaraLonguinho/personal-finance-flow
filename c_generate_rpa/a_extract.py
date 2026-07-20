# Módulo de extração de dados
# Responsável por ler arquivos CSV e extrair os dados brutos

import pandas as pd


def ler_csv(caminho_arquivo):
    """
    Lê um arquivo CSV e retorna um DataFrame.
    
    Args:
        caminho_arquivo (str): Caminho do arquivo CSV
        
    Returns:
        pd.DataFrame: DataFrame com os dados lidos
        
    Raises:
        FileNotFoundError: Caso o arquivo não exista
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
