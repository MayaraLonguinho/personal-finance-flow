# Módulo de transações
# Responsável por buscar, inserir, editar e excluir transações do MySQL

import pandas as pd
from sqlalchemy import text

from b_backend.src.categorias import (
    inicializar_categorias_padrao,
    obter_regras_categorizacao_do_banco,
)
from c_generate_rpa.categorization import categorizar_transacao
from c_generate_rpa.load import obter_engine


def buscar_todas_transacoes(
    filtros=None,
    usuario_id=None,
):
    """
    Busca todas as transações do usuário no MySQL.

    Args:
        filtros: Filtros opcionais de descrição, categoria,
            tipo e status.
        usuario_id: ID do usuário.

    Returns:
        pd.DataFrame: Transações ordenadas da mais recente
        para a mais antiga.
    """
    engine = obter_engine()

    query = """
        SELECT *
        FROM transacoes
        WHERE 1=1
    """

    parametros = {}

    if filtros:
        if filtros.get("descricao"):
            query += " AND descricao LIKE :descricao"
            parametros["descricao"] = (
                f"%{filtros['descricao']}%"
            )

        if filtros.get("categoria"):
            query += " AND categoria = :categoria"
            parametros["categoria"] = (
                filtros["categoria"]
            )

        if filtros.get("tipo"):
            query += " AND tipo = :tipo"
            parametros["tipo"] = filtros["tipo"]

        if filtros.get("status"):
            query += " AND status = :status"
            parametros["status"] = (
                filtros["status"]
            )

    if usuario_id is not None:
        query += " AND usuario_id = :usuario_id"
        parametros["usuario_id"] = usuario_id

    query += """
        ORDER BY data_transacao DESC, id DESC
    """

    return pd.read_sql(
        text(query),
        engine,
        params=parametros,
    )


def criar_transacao(
    data_transacao,
    descricao,
    categoria,
    tipo,
    valor,
    conta,
    instituicao,
    status,
    usuario_id=None,
):
    """
    Cria uma nova transação.

    Quando a transação for um investimento confirmado,
    cria também um investimento vinculado por transacao_id.
    """
    try:
        if usuario_id is None:
            raise ValueError(
                "usuario_id não fornecido "
                "para criar_transacao"
            )

        inicializar_categorias_padrao()

        if (
            not categoria
            or str(categoria).strip().lower()
            == "outros"
        ):
            regras_categorizacao = (
                obter_regras_categorizacao_do_banco()
            )

            categoria_sugerida, _ = (
                categorizar_transacao(
                    descricao,
                    categoria,
                    regras_categorizacao,
                )
            )

            categoria = (
                categoria_sugerida or "Outros"
            )

        tipo = str(tipo).strip().lower()
        status = str(status).strip().lower()

        engine = obter_engine()

        query_transacao = text(
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

        query_investimento = text(
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
            resultado_transacao = conexao.execute(
                query_transacao,
                {
                    "usuario_id": usuario_id,
                    "data_transacao": data_transacao,
                    "descricao": descricao,
                    "categoria": categoria,
                    "tipo": tipo,
                    "valor": valor,
                    "conta": conta or None,
                    "instituicao": (
                        instituicao or None
                    ),
                    "status": status,
                },
            )

            transacao_id = (
                resultado_transacao.lastrowid
            )

            if (
                tipo == "investimento"
                and status == "confirmado"
            ):
                conexao.execute(
                    query_investimento,
                    {
                        "usuario_id": usuario_id,
                        "transacao_id": transacao_id,
                        "nome": descricao,
                        "tipo_investimento": (
                            categoria
                            or "Investimento"
                        ),
                        "instituicao": (
                            instituicao or None
                        ),
                        "valor_aplicado": valor,
                        "valor_atual": valor,
                        "data_aplicacao": (
                            data_transacao
                        ),
                    },
                )

        return {
            "sucesso": True,
            "mensagem": (
                "Transação criada com sucesso"
            ),
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro),
        }


def editar_transacao(
    id_transacao,
    data_transacao,
    descricao,
    categoria,
    tipo,
    valor,
    conta,
    instituicao,
    status,
    usuario_id=None,
):
    """
    Edita uma transação e sincroniza o investimento vinculado.

    Regras:
    - investimento confirmado: cria ou atualiza o investimento;
    - investimento pendente ou cancelado: remove o investimento;
    - entrada ou saída: remove o investimento vinculado.
    """
    try:
        if usuario_id is None:
            raise ValueError(
                "usuario_id não fornecido "
                "para editar_transacao"
            )

        tipo = str(tipo).strip().lower()
        status = str(status).strip().lower()

        categoria = (
            str(categoria).strip()
            if categoria is not None
            else ""
        )

        if not categoria:
            categoria = "Outros"

        engine = obter_engine()

        query_buscar_transacao = text(
            """
            SELECT id
            FROM transacoes
            WHERE id = :id
              AND usuario_id = :usuario_id
            LIMIT 1
            """
        )

        query_atualizar_transacao = text(
            """
            UPDATE transacoes
            SET
                data_transacao = :data_transacao,
                descricao = :descricao,
                categoria = :categoria,
                tipo = :tipo,
                valor = :valor,
                conta = :conta,
                instituicao = :instituicao,
                status = :status
            WHERE id = :id
              AND usuario_id = :usuario_id
            """
        )

        query_buscar_investimento = text(
            """
            SELECT id
            FROM investimentos
            WHERE transacao_id = :transacao_id
              AND usuario_id = :usuario_id
            LIMIT 1
            """
        )

        query_criar_investimento = text(
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

        query_atualizar_investimento = text(
            """
            UPDATE investimentos
            SET
                nome = :nome,
                tipo = :tipo_investimento,
                instituicao = :instituicao,
                valor_aplicado = :valor_aplicado,
                valor_atual = :valor_atual,
                data_aplicacao = :data_aplicacao,
                status = 'ativo'
            WHERE transacao_id = :transacao_id
              AND usuario_id = :usuario_id
            """
        )

        query_excluir_investimento = text(
            """
            DELETE FROM investimentos
            WHERE transacao_id = :transacao_id
              AND usuario_id = :usuario_id
            """
        )

        parametros_investimento = {
            "usuario_id": usuario_id,
            "transacao_id": id_transacao,
            "nome": descricao,
            "tipo_investimento": (
                categoria or "Investimento"
            ),
            "instituicao": (
                instituicao or None
            ),
            "valor_aplicado": valor,
            "valor_atual": valor,
            "data_aplicacao": data_transacao,
        }

        with engine.begin() as conexao:
            transacao_existente = conexao.execute(
                query_buscar_transacao,
                {
                    "id": id_transacao,
                    "usuario_id": usuario_id,
                },
            ).first()

            if transacao_existente is None:
                raise ValueError(
                    "Transação não encontrada"
                )

            conexao.execute(
                query_atualizar_transacao,
                {
                    "id": id_transacao,
                    "usuario_id": usuario_id,
                    "data_transacao": (
                        data_transacao
                    ),
                    "descricao": descricao,
                    "categoria": categoria,
                    "tipo": tipo,
                    "valor": valor,
                    "conta": conta or None,
                    "instituicao": (
                        instituicao or None
                    ),
                    "status": status,
                },
            )

            deve_possuir_investimento = (
                tipo == "investimento"
                and status == "confirmado"
            )

            investimento_existente = (
                conexao.execute(
                    query_buscar_investimento,
                    {
                        "transacao_id": (
                            id_transacao
                        ),
                        "usuario_id": usuario_id,
                    },
                ).first()
            )

            if deve_possuir_investimento:
                if investimento_existente:
                    conexao.execute(
                        query_atualizar_investimento,
                        parametros_investimento,
                    )
                else:
                    conexao.execute(
                        query_criar_investimento,
                        parametros_investimento,
                    )

            elif investimento_existente:
                conexao.execute(
                    query_excluir_investimento,
                    {
                        "transacao_id": (
                            id_transacao
                        ),
                        "usuario_id": usuario_id,
                    },
                )

        return {
            "sucesso": True,
            "mensagem": (
                "Transação atualizada com sucesso"
            ),
        }

    except ValueError as erro:
        return {
            "sucesso": False,
            "erro": str(erro),
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro),
        }


def excluir_transacao(
    id_transacao,
    usuario_id=None,
):
    """
    Exclui uma transação e seu investimento vinculado.

    Investimentos criados diretamente na tela de
    investimentos não são removidos, pois possuem
    transacao_id igual a NULL.
    """
    try:
        if usuario_id is None:
            raise ValueError(
                "usuario_id não fornecido "
                "para excluir_transacao"
            )

        engine = obter_engine()

        query_buscar_transacao = text(
            """
            SELECT id
            FROM transacoes
            WHERE id = :id
              AND usuario_id = :usuario_id
            LIMIT 1
            """
        )

        query_excluir_investimento = text(
            """
            DELETE FROM investimentos
            WHERE transacao_id = :transacao_id
              AND usuario_id = :usuario_id
            """
        )

        query_excluir_transacao = text(
            """
            DELETE FROM transacoes
            WHERE id = :id
              AND usuario_id = :usuario_id
            """
        )

        with engine.begin() as conexao:
            transacao_existente = conexao.execute(
                query_buscar_transacao,
                {
                    "id": id_transacao,
                    "usuario_id": usuario_id,
                },
            ).first()

            if transacao_existente is None:
                raise ValueError(
                    "Transação não encontrada"
                )

            conexao.execute(
                query_excluir_investimento,
                {
                    "transacao_id": id_transacao,
                    "usuario_id": usuario_id,
                },
            )

            conexao.execute(
                query_excluir_transacao,
                {
                    "id": id_transacao,
                    "usuario_id": usuario_id,
                },
            )

        return {
            "sucesso": True,
            "mensagem": (
                "Transação excluída com sucesso"
            ),
        }

    except ValueError as erro:
        return {
            "sucesso": False,
            "erro": str(erro),
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro),
        }