"""Servidor MCP local e somente leitura do Personal Finance Flow."""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from d_traceability.c_mcp.c_allowed_resources import read_controlled_resource
from d_traceability.c_mcp.d_readonly_service import ReadOnlyFinanceService
from d_traceability.c_mcp.b_schemas import (
    ActiveGoal,
    CategoryList,
    FinancialSummary,
    InvestmentSummary,
    RecentTransactions,
    SpendingByCategory,
)


mcp = FastMCP(
    "Personal Finance Flow Read-only",
    instructions=(
        "Consultar somente dados financeiros do usuário fixado no processo. "
        "Não há ferramentas de escrita, SQL arbitrário ou acesso livre a arquivos."
    ),
    json_response=True,
)

SERVICE = ReadOnlyFinanceService.from_environment()


@mcp.tool()
def get_financial_summary() -> FinancialSummary:
    """Retorna entradas, saídas, investimentos, saldo e quantidade confirmada."""
    return FinancialSummary.model_validate(SERVICE.get_financial_summary())


@mcp.tool()
def get_recent_transactions(
    limit: Annotated[int, Field(ge=1, le=20)] = 5,
) -> RecentTransactions:
    """Lista de 1 a 20 transações confirmadas, das mais recentes para as antigas."""
    return RecentTransactions.model_validate(
        SERVICE.get_recent_transactions(limit=limit)
    )


@mcp.tool()
def get_spending_by_category(
    category: Annotated[
        Optional[str],
        Field(max_length=100),
    ] = None,
    limit: Annotated[int, Field(ge=1, le=20)] = 10,
) -> SpendingByCategory:
    """Agrupa saídas confirmadas por categoria, com filtro exato opcional."""
    return SpendingByCategory.model_validate(
        SERVICE.get_spending_by_category(category=category, limit=limit)
    )


@mcp.tool()
def get_active_goal() -> ActiveGoal:
    """Retorna a meta ativa mais recente e seu progresso calculado."""
    return ActiveGoal.model_validate(SERVICE.get_active_goal())


@mcp.tool()
def get_investment_summary() -> InvestmentSummary:
    """Retorna resumo e distribuição da carteira de investimentos ativos."""
    return InvestmentSummary.model_validate(SERVICE.get_investment_summary())


@mcp.tool()
def list_categories() -> CategoryList:
    """Lista somente os nomes das categorias pertencentes ao usuário configurado."""
    return CategoryList.model_validate(SERVICE.list_categories())


@mcp.resource("pff://project/overview", mime_type="text/markdown")
def project_overview() -> str:
    """Visão geral controlada do projeto."""
    return read_controlled_resource("overview")


@mcp.resource("pff://project/architecture", mime_type="text/markdown")
def project_architecture() -> str:
    """Arquitetura controlada do projeto."""
    return read_controlled_resource("architecture")


@mcp.resource("pff://project/data-model", mime_type="text/markdown")
def project_data_model() -> str:
    """Modelo de dados controlado do projeto."""
    return read_controlled_resource("data-model")


@mcp.resource("pff://project/etl", mime_type="text/markdown")
def project_etl() -> str:
    """Documentação controlada do pipeline ETL."""
    return read_controlled_resource("etl")


@mcp.resource("pff://project/schema", mime_type="text/plain")
def project_schema() -> str:
    """Schema SQL controlado; o resource é texto e nunca é executado."""
    return read_controlled_resource("schema")


if __name__ == "__main__":
    mcp.run(transport="stdio")
