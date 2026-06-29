"""Módulo de transformação de dados."""

import pandas as pd

from src.categorias import (
    inicializar_categorias_padrao,
    obter_regras_categorizacao_do_banco,
)
from src.categorization import categorizar_dataframe


def _normalizar_texto_arquivo(serie):
    return (
        serie.fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def tratar_transacoes(df, usuario_id=None):
    """
    Trata e limpa os dados das transações.
    
    Args:
        df (pd.DataFrame): DataFrame com dados brutos
        
    Returns:
        tuple: (pd.DataFrame, int) - DataFrame com dados tratados e contador de transações categorizadas
    """
    df = df.copy()

    df = df.drop_duplicates()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )

    for coluna in ["descricao", "categoria", "tipo", "status", "conta", "instituicao"]:
        if coluna not in df.columns:
            df[coluna] = None

    df["descricao"] = _normalizar_texto_arquivo(df["descricao"])
    df["categoria"] = _normalizar_texto_arquivo(df["categoria"]).replace("", pd.NA)
    df["tipo"] = _normalizar_texto_arquivo(df["tipo"]).str.lower()
    df["status"] = _normalizar_texto_arquivo(df["status"]).str.lower()
    df["conta"] = _normalizar_texto_arquivo(df["conta"]).replace("", pd.NA)
    df["instituicao"] = _normalizar_texto_arquivo(df["instituicao"]).replace("", pd.NA)

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df["tipo"] = df["tipo"].replace(
        {
            "receita": "entrada",
            "despesa": "saida",
            "saída": "saida",
        }
    )
    df["status"] = df["status"].replace(
        {
            "concluído": "confirmado",
            "concluido": "confirmado",
        }
    )

    inicializar_categorias_padrao(usuario_id=usuario_id)
    regras_categorizacao = obter_regras_categorizacao_do_banco(usuario_id=usuario_id)

    df, contador_categorizadas = categorizar_dataframe(
        df,
        regras_categorizacao=regras_categorizacao,
        categorias_usuario=regras_categorizacao,
    )

    df = df.dropna(subset=["valor", "data"])

    return df, contador_categorizadas
