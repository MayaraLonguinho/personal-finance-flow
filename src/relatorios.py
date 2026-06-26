from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text

from src.investimentos import obter_resumo_investimentos
from src.load import obter_engine


def converter_valor(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, datetime):
        return valor.isoformat()

    if hasattr(valor, "isoformat"):
        return valor.isoformat()

    return valor


def validar_data(
    data_texto: Optional[str],
) -> Optional[str]:
    if not data_texto:
        return None

    try:
        datetime.strptime(
            data_texto,
            "%Y-%m-%d",
        )

        return data_texto

    except ValueError as erro:
        raise ValueError(
            "A data deve estar no formato YYYY-MM-DD."
        ) from erro


def obter_relatorio(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
) -> dict:
    data_inicio = validar_data(data_inicio)
    data_fim = validar_data(data_fim)

    if (
        data_inicio
        and data_fim
        and data_inicio > data_fim
    ):
        raise ValueError(
            "A data inicial não pode ser maior "
            "que a data final."
        )

    filtros = []
    parametros = {}

    if data_inicio:
        filtros.append(
            "DATE(data_transacao) >= :data_inicio"
        )

        parametros["data_inicio"] = data_inicio

    if data_fim:
        filtros.append(
            "DATE(data_transacao) <= :data_fim"
        )

        parametros["data_fim"] = data_fim

    where_sql = ""

    if filtros:
        where_sql = (
            "WHERE "
            + " AND ".join(filtros)
        )

    consulta_resumo = text(
        f"""
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN tipo = 'entrada'
                        THEN valor
                        ELSE 0
                    END
                ),
                0
            ) AS total_entradas,

            COALESCE(
                SUM(
                    CASE
                        WHEN tipo = 'saida'
                        THEN valor
                        ELSE 0
                    END
                ),
                0
            ) AS total_saidas,

            COALESCE(
                SUM(
                    CASE
                        WHEN tipo = 'investimento'
                        THEN valor
                        ELSE 0
                    END
                ),
                0
            ) AS total_investido,

            COUNT(*) AS quantidade_transacoes
        FROM transacoes
        {where_sql}
        """
    )

    consulta_categorias = text(
        f"""
        SELECT
            COALESCE(
                categoria,
                'Outros'
            ) AS categoria,

            COALESCE(
                SUM(valor),
                0
            ) AS valor,

            COUNT(*) AS quantidade
        FROM transacoes
        {where_sql}
        {"AND" if where_sql else "WHERE"}
            tipo = 'saida'
        GROUP BY categoria
        ORDER BY valor DESC
        """
    )

    consulta_transacoes = text(
        f"""
        SELECT
            id,
            data_transacao,
            descricao,
            categoria,
            tipo,
            valor,
            conta,
            instituicao,
            status
        FROM transacoes
        {where_sql}
        ORDER BY
            data_transacao DESC,
            id DESC
        """
    )

    engine = obter_engine()

    with engine.connect() as conexao:
        resultado_resumo = conexao.execute(
            consulta_resumo,
            parametros,
        ).mappings().first()

        resultado_categorias = conexao.execute(
            consulta_categorias,
            parametros,
        ).mappings().all()

        resultado_transacoes = conexao.execute(
            consulta_transacoes,
            parametros,
        ).mappings().all()

    total_entradas = float(
        resultado_resumo["total_entradas"]
        or 0
    )

    total_saidas = float(
        resultado_resumo["total_saidas"]
        or 0
    )

    total_investido = float(
        resultado_resumo["total_investido"]
        or 0
    )

    quantidade_transacoes = int(
        resultado_resumo[
            "quantidade_transacoes"
        ]
        or 0
    )

    saldo = (
        total_entradas
        - total_saidas
    )

    categorias = []

    for categoria in resultado_categorias:
        categorias.append(
            {
                "categoria": (
                    categoria["categoria"]
                    or "Outros"
                ),
                "valor": float(
                    categoria["valor"]
                    or 0
                ),
                "quantidade": int(
                    categoria["quantidade"]
                    or 0
                ),
            }
        )

    transacoes = []

    for transacao in resultado_transacoes:
        transacoes.append(
            {
                chave: converter_valor(valor)
                for chave, valor
                in transacao.items()
            }
        )

    resumo_investimentos = (
        obter_resumo_investimentos()
    )

    return {
        "periodo": {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        },
        "resumo": {
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo": saldo,
            "total_investido": total_investido,
            "quantidade_transacoes": (
                quantidade_transacoes
            ),
        },
        "investimentos": (
            resumo_investimentos
        ),
        "categorias": categorias,
        "transacoes": transacoes,
    }