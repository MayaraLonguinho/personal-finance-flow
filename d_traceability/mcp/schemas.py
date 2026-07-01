"""Contratos estruturados expostos pelas tools MCP."""

from typing import List, Optional

from pydantic import BaseModel, Field


class FinancialSummary(BaseModel):
    total_entradas: float
    total_saidas: float
    total_investido: float
    saldo_final: float
    quantidade_transacoes: int
    moeda: str
    criterio: str


class Transaction(BaseModel):
    data_transacao: str
    descricao: str
    categoria: Optional[str] = None
    tipo: str
    valor: float


class RecentTransactions(BaseModel):
    transacoes: List[Transaction]
    quantidade: int
    limite: int = Field(ge=1, le=20)
    criterio: str


class CategoryAmount(BaseModel):
    categoria: str
    valor: float


class SpendingByCategory(BaseModel):
    categorias: List[CategoryAmount]
    quantidade: int
    filtro_categoria: Optional[str] = None
    criterio: str


class Goal(BaseModel):
    titulo: str
    valor_meta: float
    valor_atual: float
    data_limite: Optional[str] = None
    percentual: float
    valor_restante: float


class ActiveGoal(BaseModel):
    meta: Optional[Goal] = None
    mensagem: Optional[str] = None


class InvestmentDistribution(BaseModel):
    tipo: str
    quantidade: int
    valor_atual: float


class InvestmentSummary(BaseModel):
    quantidade_total: int
    quantidade_ativos: int
    total_aplicado: float
    valor_atual_total: float
    lucro_prejuizo: float
    rentabilidade_total: float
    distribuicao_por_tipo: List[InvestmentDistribution]
    criterio: str


class CategoryList(BaseModel):
    categorias: List[str]
    quantidade: int

