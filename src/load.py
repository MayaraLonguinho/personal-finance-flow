# Módulo de carregamento de dados
# Responsável por salvar os dados tratados no banco de dados MySQL

import pandas as pd
from sqlalchemy import create_engine, URL, text
from dotenv import load_dotenv
import os


def obter_engine():
    """
    Cria e retorna o engine de conexão com o MySQL usando URL.create.
    
    Returns:
        Engine: Engine do SQLAlchemy para conexão com o banco
    """
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    
    # Cria a URL de conexão usando URL.create (lida melhor com caracteres especiais)
    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name
    )
    
    # Cria o engine de conexão
    engine = create_engine(connection_url)
    
    return engine


def carregar_transacoes_mysql(df):
    """
    Carrega somente transações que ainda não existem no MySQL.

    Returns:
        dict: quantidade recebida, importada e ignorada.
    """
    engine = obter_engine()

    colunas_esperadas = [
        "data_transacao",
        "descricao",
        "categoria",
        "tipo",
        "valor",
        "conta",
        "instituicao",
        "status"
    ]

    try:
        df = df.copy()

        if "data" in df.columns:
            df = df.rename(columns={"data": "data_transacao"})

        # Garante que todas as colunas necessárias existam
        for coluna in colunas_esperadas:
            if coluna not in df.columns:
                df[coluna] = None

        df_para_carregar = df[colunas_esperadas].copy()

        # Padroniza os dados antes da comparação
        df_para_carregar["data_transacao"] = pd.to_datetime(
            df_para_carregar["data_transacao"],
            errors="coerce"
        ).dt.date

        df_para_carregar["valor"] = pd.to_numeric(
            df_para_carregar["valor"],
            errors="coerce"
        ).round(2)

        colunas_texto = [
            "descricao",
            "categoria",
            "tipo",
            "conta",
            "instituicao",
            "status"
        ]

        for coluna in colunas_texto:
            df_para_carregar[coluna] = (
                df_para_carregar[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
            )

        # Remove duplicações dentro do próprio arquivo enviado
        quantidade_recebida = len(df_para_carregar)

        df_para_carregar = df_para_carregar.drop_duplicates(
            subset=colunas_esperadas
        )

        # Busca as transações existentes no banco
        query = """
            SELECT
                data_transacao,
                descricao,
                categoria,
                tipo,
                valor,
                conta,
                instituicao,
                status
            FROM transacoes
        """

        df_existente = pd.read_sql(query, engine)

        if not df_existente.empty:
            df_existente["data_transacao"] = pd.to_datetime(
                df_existente["data_transacao"],
                errors="coerce"
            ).dt.date

            df_existente["valor"] = pd.to_numeric(
                df_existente["valor"],
                errors="coerce"
            ).round(2)

            for coluna in colunas_texto:
                df_existente[coluna] = (
                    df_existente[coluna]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

            # Cria uma chave de comparação para cada transação
            chaves_existentes = set(
                df_existente[colunas_esperadas]
                .astype(str)
                .agg("|".join, axis=1)
            )

            chaves_novas = (
                df_para_carregar[colunas_esperadas]
                .astype(str)
                .agg("|".join, axis=1)
            )

            df_para_carregar = df_para_carregar[
                ~chaves_novas.isin(chaves_existentes)
            ]

        quantidade_importada = len(df_para_carregar)
        quantidade_ignorada = quantidade_recebida - quantidade_importada

        if quantidade_importada > 0:
            # Converte campos vazios novamente para NULL
            for coluna in ["conta", "instituicao"]:
                df_para_carregar[coluna] = df_para_carregar[coluna].replace(
                    "",
                    None
                )

            df_para_carregar.to_sql(
                "transacoes",
                engine,
                if_exists="append",
                index=False
            )

        print(f"Registros recebidos: {quantidade_recebida}")
        print(f"Registros importados: {quantidade_importada}")
        print(f"Registros ignorados: {quantidade_ignorada}")

        return {
            "recebidos": quantidade_recebida,
            "importados": quantidade_importada,
            "ignorados": quantidade_ignorada
        }

    except Exception as erro:
        print(f"Erro ao carregar dados: {erro}")
        raise




def limpar_transacoes_mysql():
    """
    Remove todas as transações cadastradas no banco.
    """
    engine = obter_engine()

    with engine.begin() as conexao:
        conexao.execute(text("DELETE FROM transacoes"))

    print("Todas as transações foram removidas.")
