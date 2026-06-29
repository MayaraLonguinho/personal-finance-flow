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


def garantir_colunas_usuario():
    """
    Garante que as tabelas que agora armazenam dados por usuário
    possuam a coluna `usuario_id`.
    """
    engine = obter_engine()

    tabelas_colunas = {
        "metas": "usuario_id",
        "categorias": "usuario_id",
        "investimentos": "usuario_id",
    }

    with engine.begin() as conexao:
        for tabela, coluna in tabelas_colunas.items():
            existe = conexao.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = :tabela
                      AND COLUMN_NAME = :coluna
                    """
                ),
                {"tabela": tabela, "coluna": coluna},
            ).scalar()

            if existe == 0:
                conexao.execute(
                    text(f"ALTER TABLE {tabela} ADD COLUMN {coluna} INT NULL")
                )
                print(f"Coluna {coluna} adicionada à tabela {tabela}.")


def carregar_transacoes_mysql(df, usuario_id):
    """
    Carrega somente transações que ainda não existem no MySQL,
    associando os registros ao usuário informado.

    Args:
        df: DataFrame com as transações tratadas.
        usuario_id: ID do usuário responsável pelos dados.

    Returns:
        dict: quantidades recebidas, importadas e ignoradas.
    """
    engine = obter_engine()

    colunas_transacao = [
        "data_transacao",
        "descricao",
        "categoria",
        "tipo",
        "valor",
        "conta",
        "instituicao",
        "status",
    ]

    colunas_carga = [
        "usuario_id",
        "data_transacao",
        "descricao",
        "categoria",
        "tipo",
        "valor",
        "conta",
        "instituicao",
        "status",
    ]

    try:
        df = df.copy()

        if "data" in df.columns:
            df = df.rename(
                columns={
                    "data": "data_transacao",
                }
            )

        for coluna in colunas_transacao:
            if coluna not in df.columns:
                df[coluna] = None

        df_para_carregar = df[colunas_transacao].copy()

        df_para_carregar["usuario_id"] = usuario_id

        df_para_carregar["data_transacao"] = pd.to_datetime(
            df_para_carregar["data_transacao"],
            errors="coerce",
        ).dt.date

        df_para_carregar["valor"] = pd.to_numeric(
            df_para_carregar["valor"],
            errors="coerce",
        ).round(2)

        colunas_texto = [
            "descricao",
            "categoria",
            "tipo",
            "conta",
            "instituicao",
            "status",
        ]

        for coluna in colunas_texto:
            df_para_carregar[coluna] = (
                df_para_carregar[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
            )

        df_para_carregar = df_para_carregar.dropna(
            subset=[
                "data_transacao",
                "valor",
            ]
        )

        quantidade_recebida = len(df_para_carregar)

        df_para_carregar = (
            df_para_carregar.drop_duplicates(
                subset=colunas_carga
            )
        )

        query = text(
            """
            SELECT
                usuario_id,
                data_transacao,
                descricao,
                categoria,
                tipo,
                valor,
                conta,
                instituicao,
                status
            FROM transacoes
            WHERE usuario_id = :usuario_id
            """
        )

        df_existente = pd.read_sql(
            query,
            engine,
            params={
                "usuario_id": usuario_id,
            },
        )

        if not df_existente.empty:
            df_existente["data_transacao"] = pd.to_datetime(
                df_existente["data_transacao"],
                errors="coerce",
            ).dt.date

            df_existente["valor"] = pd.to_numeric(
                df_existente["valor"],
                errors="coerce",
            ).round(2)

            for coluna in colunas_texto:
                df_existente[coluna] = (
                    df_existente[coluna]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

            chaves_existentes = set(
                df_existente[colunas_carga]
                .astype(str)
                .agg("|".join, axis=1)
            )

            chaves_novas = (
                df_para_carregar[colunas_carga]
                .astype(str)
                .agg("|".join, axis=1)
            )

            df_para_carregar = df_para_carregar[
                ~chaves_novas.isin(
                    chaves_existentes
                )
            ]

        quantidade_importada = len(
            df_para_carregar
        )

        quantidade_ignorada = (
            quantidade_recebida
            - quantidade_importada
        )

        if quantidade_importada > 0:
            for coluna in [
                "conta",
                "instituicao",
            ]:
                df_para_carregar[coluna] = (
                    df_para_carregar[coluna]
                    .replace("", None)
                )

            df_para_carregar[colunas_carga].to_sql(
                "transacoes",
                engine,
                if_exists="append",
                index=False,
            )

        print(
            f"Registros recebidos: "
            f"{quantidade_recebida}"
        )

        print(
            f"Registros importados: "
            f"{quantidade_importada}"
        )

        print(
            f"Registros ignorados: "
            f"{quantidade_ignorada}"
        )

        return {
            "recebidos": quantidade_recebida,
            "importados": quantidade_importada,
            "ignorados": quantidade_ignorada,
        }

    except Exception as erro:
        print(
            f"Erro ao carregar dados: {erro}"
        )

        raise

def limpar_transacoes_mysql(usuario_id=None):
    """
    Remove transações cadastradas no banco.

    Se `usuario_id` for informado, remove apenas as transações desse usuário.
    Caso contrário, remove todas (uso restrito).
    """
    engine = obter_engine()

    with engine.begin() as conexao:
        if usuario_id is None:
            conexao.execute(text("DELETE FROM transacoes"))
            print("Todas as transações foram removidas.")
        else:
            conexao.execute(text("DELETE FROM transacoes WHERE usuario_id = :usuario_id"), {'usuario_id': usuario_id})
            print(f"Transações do usuário {usuario_id} foram removidas.")
