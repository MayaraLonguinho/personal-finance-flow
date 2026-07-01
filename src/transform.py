"""Módulo de transformação de dados."""

import pandas as pd

from src.categorias import (
    inicializar_categorias_padrao,
    obter_regras_categorizacao_do_banco,
)
from src.categorization import categorizar_dataframe


COLUNAS_OBRIGATORIAS_UPLOAD = {
    "data",
    "descricao",
    "tipo",
    "valor",
    "status",
}
TIPOS_VALIDOS = {"entrada", "saida", "investimento"}
STATUS_VALIDOS = {"confirmado", "pendente", "cancelado"}


def _normalizar_texto_arquivo(serie):
    return (
        serie.fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def _normalizar_dataframe_upload(df):
    df = df.copy()
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

    df["data"] = pd.to_datetime(
        df["data"],
        errors="coerce",
    )
    df["valor"] = pd.to_numeric(
        df["valor"],
        errors="coerce",
    )
    return df


def processar_upload_csv(df, usuario_id):
    """
    Valida e trata um CSV enviado pelo usuário autenticado.

    Returns:
        tuple[pd.DataFrame, int, dict]: DataFrame aceito, quantidade categorizada e relatório.
    """
    if usuario_id is None:
        raise PermissionError("Usuário não autenticado para importar transações")

    if df is None or df.empty:
        raise ValueError("O arquivo CSV está vazio.")

    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )

    colunas_faltantes = sorted(
        coluna
        for coluna in COLUNAS_OBRIGATORIAS_UPLOAD
        if coluna not in df.columns
    )
    if colunas_faltantes:
        colunas_formatadas = ", ".join(colunas_faltantes)
        raise ValueError(
            f"O CSV deve conter as colunas obrigatórias: {colunas_formatadas}."
        )

    total_linhas = len(df.index)
    df = _normalizar_dataframe_upload(df)
    df["_linha_csv"] = range(2, len(df.index) + 2)

    rejeicoes = []
    linhas_aceitas = []

    for _, linha in df.iterrows():
        motivos = []

        if not linha["descricao"]:
            motivos.append("descrição ausente")
        if pd.isna(linha["data"]):
            motivos.append("data inválida")
        if pd.isna(linha["valor"]):
            motivos.append("valor inválido")
        if linha["tipo"] not in TIPOS_VALIDOS:
            motivos.append("tipo inválido")
        if linha["status"] not in STATUS_VALIDOS:
            motivos.append("status inválido")

        if motivos:
            rejeicoes.append(
                {
                    "linha": int(linha["_linha_csv"]),
                    "motivo": ", ".join(motivos),
                }
            )
            continue

        linhas_aceitas.append(linha.to_dict())

    df_aceito = pd.DataFrame(linhas_aceitas)

    if df_aceito.empty:
        relatorio = {
            "total_linhas": total_linhas,
            "linhas_aceitas": 0,
            "linhas_rejeitadas": len(rejeicoes),
            "rejeicoes": rejeicoes,
        }
        return df_aceito, 0, relatorio

    inicializar_categorias_padrao(usuario_id=usuario_id)
    regras_categorizacao = obter_regras_categorizacao_do_banco(usuario_id=usuario_id)

    df_aceito, contador_categorizadas = categorizar_dataframe(
        df_aceito,
        regras_categorizacao=regras_categorizacao,
        categorias_usuario=regras_categorizacao,
    )

    chaves_duplicidade = (
        df_aceito[
            ["data", "descricao", "categoria", "tipo", "valor", "conta", "instituicao", "status"]
        ]
        .astype(str)
        .agg("|".join, axis=1)
    )
    mascara_duplicadas = chaves_duplicidade.duplicated(keep="first")

    if mascara_duplicadas.any():
        for _, linha in df_aceito[mascara_duplicadas].iterrows():
            rejeicoes.append(
                {
                    "linha": int(linha["_linha_csv"]),
                    "motivo": "linha duplicada no arquivo",
                }
            )
        df_aceito = df_aceito[~mascara_duplicadas].copy()

    relatorio = {
        "total_linhas": total_linhas,
        "linhas_aceitas": len(df_aceito.index),
        "linhas_rejeitadas": len(rejeicoes),
        "rejeicoes": sorted(rejeicoes, key=lambda item: item["linha"]),
    }

    return df_aceito, contador_categorizadas, relatorio


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

    df = _normalizar_dataframe_upload(df)

    inicializar_categorias_padrao(usuario_id=usuario_id)
    regras_categorizacao = obter_regras_categorizacao_do_banco(usuario_id=usuario_id)

    df, contador_categorizadas = categorizar_dataframe(
        df,
        regras_categorizacao=regras_categorizacao,
        categorias_usuario=regras_categorizacao,
    )

    df = df.dropna(subset=["valor", "data"])

    return df, contador_categorizadas
