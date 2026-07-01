import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

from c_generate_rpa.categorization import normalizar_texto


def obter_engine():
    """
    Cria e retorna o engine de conexão com o MySQL.

    Returns:
        Engine: Engine do SQLAlchemy.
    """
    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
    )

    return create_engine(connection_url)


def _normalizar_texto_livre(valor):
    if valor is None or pd.isna(valor):
        return None

    texto = " ".join(str(valor).split()).strip()

    return texto or None


def _normalizar_texto_para_comparacao(valor):
    return normalizar_texto(valor) or ""


def _normalizar_categoria_para_armazenamento(
    valor,
):
    categoria = _normalizar_texto_livre(valor)

    if not categoria:
        return "Outros"

    return categoria


def garantir_colunas_usuario():
    """
    Garante que as tabelas que armazenam dados por usuário
    possuam a coluna usuario_id.
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
                {
                    "tabela": tabela,
                    "coluna": coluna,
                },
            ).scalar()

            if existe == 0:
                conexao.execute(
                    text(
                        f"""
                        ALTER TABLE {tabela}
                        ADD COLUMN {coluna} INT NULL
                        """
                    )
                )

                print(
                    f"Coluna {coluna} adicionada "
                    f"à tabela {tabela}."
                )


def carregar_transacoes_mysql(
    df,
    usuario_id,
):
    """
    Carrega somente transações ainda não existentes.

    Investimentos confirmados também são inseridos na
    tabela investimentos e vinculados por transacao_id.

    Args:
        df: DataFrame com as transações tratadas.
        usuario_id: ID do usuário responsável pelos dados.

    Returns:
        dict: Quantidades recebidas, importadas e ignoradas.
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
        if usuario_id is None:
            raise ValueError(
                "usuario_id não fornecido "
                "para carregar_transacoes_mysql"
            )

        df = df.copy()
        linhas_ignoradas_duplicadas = []

        if "data" in df.columns:
            df = df.rename(
                columns={
                    "data": "data_transacao",
                }
            )

        colunas_processamento = list(
            colunas_transacao
        )

        if "_linha_csv" in df.columns:
            colunas_processamento.append(
                "_linha_csv"
            )

        for coluna in colunas_processamento:
            if coluna not in df.columns:
                df[coluna] = None

        df_para_carregar = df[
            colunas_processamento
        ].copy()

        df_para_carregar["usuario_id"] = (
            usuario_id
        )

        df_para_carregar["data_transacao"] = (
            pd.to_datetime(
                df_para_carregar[
                    "data_transacao"
                ],
                errors="coerce",
            ).dt.date
        )

        df_para_carregar["valor"] = (
            pd.to_numeric(
                df_para_carregar["valor"],
                errors="coerce",
            ).round(2)
        )

        for coluna in [
            "descricao",
            "conta",
            "instituicao",
        ]:
            df_para_carregar[coluna] = (
                df_para_carregar[coluna].apply(
                    _normalizar_texto_livre
                )
            )

        df_para_carregar["categoria"] = (
            df_para_carregar[
                "categoria"
            ].apply(
                _normalizar_categoria_para_armazenamento
            )
        )

        df_para_carregar["tipo"] = (
            df_para_carregar["tipo"].apply(
                lambda valor: (
                    _normalizar_texto_livre(valor)
                    or ""
                ).lower()
            )
        )

        df_para_carregar["status"] = (
            df_para_carregar[
                "status"
            ].apply(
                lambda valor: (
                    _normalizar_texto_livre(valor)
                    or ""
                ).lower()
            )
        )

        df_para_carregar = (
            df_para_carregar.dropna(
                subset=[
                    "data_transacao",
                    "valor",
                ]
            )
        )

        quantidade_recebida = len(
            df_para_carregar
        )

        df_para_carregar = (
            df_para_carregar.drop_duplicates(
                subset=colunas_carga
            )
        )

        query_transacoes_existentes = text(
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
            query_transacoes_existentes,
            engine,
            params={
                "usuario_id": usuario_id,
            },
        )

        if not df_existente.empty:
            df_existente["data_transacao"] = (
                pd.to_datetime(
                    df_existente[
                        "data_transacao"
                    ],
                    errors="coerce",
                ).dt.date
            )

            df_existente["valor"] = (
                pd.to_numeric(
                    df_existente["valor"],
                    errors="coerce",
                ).round(2)
            )

            for coluna in [
                "descricao",
                "conta",
                "instituicao",
            ]:
                df_existente[coluna] = (
                    df_existente[
                        coluna
                    ].apply(
                        _normalizar_texto_livre
                    )
                )

            df_existente["categoria"] = (
                df_existente[
                    "categoria"
                ].apply(
                    _normalizar_categoria_para_armazenamento
                )
            )

            df_existente["tipo"] = (
                df_existente["tipo"].apply(
                    lambda valor: (
                        _normalizar_texto_livre(
                            valor
                        )
                        or ""
                    ).lower()
                )
            )

            df_existente["status"] = (
                df_existente[
                    "status"
                ].apply(
                    lambda valor: (
                        _normalizar_texto_livre(
                            valor
                        )
                        or ""
                    ).lower()
                )
            )

            colunas_comparacao = [
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

            df_existente_comparacao = (
                df_existente[
                    colunas_comparacao
                ].copy()
            )

            df_novo_comparacao = (
                df_para_carregar[
                    colunas_comparacao
                ].copy()
            )

            for coluna in [
                "descricao",
                "categoria",
                "conta",
                "instituicao",
                "tipo",
                "status",
            ]:
                df_existente_comparacao[
                    coluna
                ] = (
                    df_existente_comparacao[
                        coluna
                    ].apply(
                        _normalizar_texto_para_comparacao
                    )
                )

                df_novo_comparacao[
                    coluna
                ] = (
                    df_novo_comparacao[
                        coluna
                    ].apply(
                        _normalizar_texto_para_comparacao
                    )
                )

            chaves_existentes = set(
                df_existente_comparacao[
                    colunas_comparacao
                ]
                .astype(str)
                .agg("|".join, axis=1)
            )

            chaves_novas = (
                df_novo_comparacao[
                    colunas_comparacao
                ]
                .astype(str)
                .agg("|".join, axis=1)
            )

            mascara_duplicadas_banco = (
                chaves_novas.isin(
                    chaves_existentes
                )
            )

            if (
                "_linha_csv"
                in df_para_carregar.columns
            ):
                linhas_ignoradas_duplicadas = (
                    df_para_carregar.loc[
                        mascara_duplicadas_banco,
                        "_linha_csv",
                    ]
                    .dropna()
                    .astype(int)
                    .tolist()
                )

            df_para_carregar = (
                df_para_carregar.loc[
                    ~mascara_duplicadas_banco
                ].copy()
            )

        quantidade_importada = len(
            df_para_carregar
        )

        quantidade_ignorada = (
            quantidade_recebida
            - quantidade_importada
        )

        if quantidade_importada > 0:
            df_para_carregar = (
                df_para_carregar.copy()
            )

            for coluna in [
                "conta",
                "instituicao",
            ]:
                df_para_carregar[coluna] = (
                    df_para_carregar[coluna]
                    .replace("", None)
                )

            query_inserir_transacao = text(
                """
                INSERT INTO transacoes (
                    usuario_id,
                    data_transacao,
                    descricao,
                    categoria,
                    tipo,
                    valor,
                    conta,
                    instituicao,
                    status
                )
                VALUES (
                    :usuario_id,
                    :data_transacao,
                    :descricao,
                    :categoria,
                    :tipo,
                    :valor,
                    :conta,
                    :instituicao,
                    :status
                )
                """
            )

            query_inserir_investimento = text(
                """
                INSERT INTO investimentos (
                    usuario_id,
                    transacao_id,
                    nome,
                    tipo,
                    instituicao,
                    valor_aplicado,
                    valor_atual,
                    rentabilidade_percentual,
                    data_aplicacao,
                    data_vencimento,
                    status
                )
                VALUES (
                    :usuario_id,
                    :transacao_id,
                    :nome,
                    :tipo_investimento,
                    :instituicao,
                    :valor_aplicado,
                    :valor_atual,
                    0,
                    :data_aplicacao,
                    NULL,
                    'ativo'
                )
                """
            )

            with engine.begin() as conexao:
                for _, registro in (
                    df_para_carregar.iterrows()
                ):
                    parametros_transacao = {
                        "usuario_id": int(
                            registro[
                                "usuario_id"
                            ]
                        ),
                        "data_transacao": (
                            registro[
                                "data_transacao"
                            ]
                        ),
                        "descricao": (
                            registro["descricao"]
                        ),
                        "categoria": (
                            registro["categoria"]
                        ),
                        "tipo": registro["tipo"],
                        "valor": float(
                            registro["valor"]
                        ),
                        "conta": (
                            registro["conta"]
                        ),
                        "instituicao": (
                            registro[
                                "instituicao"
                            ]
                        ),
                        "status": (
                            registro["status"]
                        ),
                    }

                    resultado_transacao = (
                        conexao.execute(
                            query_inserir_transacao,
                            parametros_transacao,
                        )
                    )

                    transacao_id = (
                        resultado_transacao.lastrowid
                    )

                    if (
                        registro["tipo"]
                        == "investimento"
                        and registro["status"]
                        == "confirmado"
                    ):
                        conexao.execute(
                            query_inserir_investimento,
                            {
                                "usuario_id": int(
                                    registro[
                                        "usuario_id"
                                    ]
                                ),
                                "transacao_id": (
                                    transacao_id
                                ),
                                "nome": (
                                    registro[
                                        "descricao"
                                    ]
                                ),
                                "tipo_investimento": (
                                    registro[
                                        "categoria"
                                    ]
                                    or "Investimento"
                                ),
                                "instituicao": (
                                    registro[
                                        "instituicao"
                                    ]
                                ),
                                "valor_aplicado": (
                                    float(
                                        registro[
                                            "valor"
                                        ]
                                    )
                                ),
                                "valor_atual": (
                                    float(
                                        registro[
                                            "valor"
                                        ]
                                    )
                                ),
                                "data_aplicacao": (
                                    registro[
                                        "data_transacao"
                                    ]
                                ),
                            },
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
            "linhas_ignoradas_duplicadas": (
                linhas_ignoradas_duplicadas
            ),
        }

    except Exception as erro:
        print(
            f"Erro ao carregar dados: {erro}"
        )

        raise


def limpar_transacoes_mysql(
    usuario_id=None,
):
    """
    Remove todos os dados financeiros do usuário.

    São removidos:
    - investimentos vinculados ou cadastrados diretamente;
    - transações;
    - metas;
    - categorias.

    O usuário, as credenciais e as configurações da conta
    são preservados.
    """
    if usuario_id is None:
        raise ValueError(
            "usuario_id não fornecido "
            "para limpar_transacoes_mysql"
        )

    engine = obter_engine()

    query_excluir_investimentos = text(
        """
        DELETE FROM investimentos
        WHERE usuario_id = :usuario_id
        """
    )

    query_excluir_transacoes = text(
        """
        DELETE FROM transacoes
        WHERE usuario_id = :usuario_id
        """
    )

    query_excluir_metas = text(
        """
        DELETE FROM metas
        WHERE usuario_id = :usuario_id
        """
    )

    query_excluir_categorias = text(
        """
        DELETE FROM categorias
        WHERE usuario_id = :usuario_id
        """
    )

    parametros = {
        "usuario_id": usuario_id,
    }

    with engine.begin() as conexao:
        resultado_investimentos = conexao.execute(
            query_excluir_investimentos,
            parametros,
        )

        resultado_transacoes = conexao.execute(
            query_excluir_transacoes,
            parametros,
        )

        resultado_metas = conexao.execute(
            query_excluir_metas,
            parametros,
        )

        resultado_categorias = conexao.execute(
            query_excluir_categorias,
            parametros,
        )

    resultado = {
        "investimentos_removidos": (
            resultado_investimentos.rowcount
        ),
        "transacoes_removidas": (
            resultado_transacoes.rowcount
        ),
        "metas_removidas": (
            resultado_metas.rowcount
        ),
        "categorias_removidas": (
            resultado_categorias.rowcount
        ),
    }

    print(
        "Dados financeiros removidos do usuário "
        f"{usuario_id}: {resultado}"
    )

    return resultado