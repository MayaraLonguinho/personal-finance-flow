"""Fachada de consultas financeiras estritamente somente leitura."""

from datetime import date, datetime
from decimal import Decimal
import os
import re
from typing import Any, Dict, List, Mapping, Optional

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|ALTER|CREATE|DROP|TRUNCATE|GRANT|REVOKE|CALL|EXECUTE|LOAD|INTO\s+OUTFILE)\b",
    re.IGNORECASE,
)


QUERIES: Mapping[str, str] = {
    "financial_summary": """
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) AS total_entradas,
            COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) AS total_saidas,
            COALESCE(SUM(CASE WHEN tipo = 'investimento' THEN valor ELSE 0 END), 0) AS total_investido,
            COUNT(*) AS quantidade_transacoes
        FROM transacoes
        WHERE status = 'confirmado' AND usuario_id = :usuario_id
    """,
    "currency": """
        SELECT moeda
        FROM configuracoes_usuario
        WHERE usuario_id = :usuario_id
        LIMIT 1
    """,
    "recent_transactions": """
        SELECT data_transacao, descricao, categoria, tipo, valor
        FROM transacoes
        WHERE status = 'confirmado' AND usuario_id = :usuario_id
        ORDER BY data_transacao DESC, id DESC
        LIMIT :limite
    """,
    "spending_by_category": """
        SELECT COALESCE(categoria, 'outros') AS categoria, COALESCE(SUM(valor), 0) AS valor
        FROM transacoes
        WHERE status = 'confirmado'
          AND tipo = 'saida'
          AND usuario_id = :usuario_id
          AND (:categoria IS NULL OR LOWER(categoria) = LOWER(:categoria))
        GROUP BY COALESCE(categoria, 'outros')
        ORDER BY valor DESC
        LIMIT :limite
    """,
    "active_goal": """
        SELECT titulo, valor_meta, valor_atual, data_limite
        FROM metas
        WHERE status = 'ativa' AND usuario_id = :usuario_id
        ORDER BY id DESC
        LIMIT 1
    """,
    "investment_summary": """
        SELECT
            COUNT(*) AS quantidade_total,
            COALESCE(SUM(CASE WHEN status = 'ativo' THEN valor_aplicado ELSE 0 END), 0) AS total_aplicado,
            COALESCE(SUM(CASE WHEN status = 'ativo' THEN valor_atual ELSE 0 END), 0) AS valor_atual_total,
            COALESCE(SUM(CASE WHEN status = 'ativo' THEN valor_atual - valor_aplicado ELSE 0 END), 0) AS lucro_prejuizo,
            COALESCE(SUM(CASE WHEN status = 'ativo' THEN 1 ELSE 0 END), 0) AS quantidade_ativos
        FROM investimentos
        WHERE usuario_id = :usuario_id
    """,
    "investment_distribution": """
        SELECT tipo, COUNT(*) AS quantidade, COALESCE(SUM(valor_atual), 0) AS valor_atual
        FROM investimentos
        WHERE status = 'ativo' AND usuario_id = :usuario_id
        GROUP BY tipo
        ORDER BY valor_atual DESC
    """,
    "categories": """
        SELECT nome
        FROM categorias
        WHERE usuario_id = :usuario_id
        ORDER BY nome
    """,
}


class ReadOnlyConfigurationError(RuntimeError):
    """Configuração obrigatória ausente ou inválida."""


class ReadOnlyDataError(RuntimeError):
    """Falha sanitizada de uma consulta somente leitura."""


def validate_readonly_queries() -> None:
    """Falha cedo se uma consulta estática deixar de ser somente leitura."""
    for name, query in QUERIES.items():
        normalized = " ".join(query.split())
        if not normalized.upper().startswith("SELECT "):
            raise ReadOnlyConfigurationError(
                "A consulta '{}' não começa com SELECT.".format(name)
            )
        if FORBIDDEN_SQL.search(normalized):
            raise ReadOnlyConfigurationError(
                "A consulta '{}' contém operação não permitida.".format(name)
            )
        if ":usuario_id" not in normalized:
            raise ReadOnlyConfigurationError(
                "A consulta '{}' não restringe usuario_id.".format(name)
            )


def _required_environment(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ReadOnlyConfigurationError(
            "Variável obrigatória ausente: {}".format(name)
        )
    return value


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _serialize_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: _serialize_value(value) for key, value in row.items()}


class ReadOnlyFinanceService:
    """Executa apenas consultas pré-definidas para um único usuário."""

    def __init__(self, engine: Engine, user_id: int):
        validate_readonly_queries()
        if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
            raise ReadOnlyConfigurationError(
                "PFF_MCP_USER_ID deve ser um inteiro positivo."
            )
        self._engine = engine
        self._user_id = user_id

    @classmethod
    def from_environment(cls) -> "ReadOnlyFinanceService":
        env_file = os.getenv("PFF_MCP_ENV_FILE", "").strip()
        if env_file:
            load_dotenv(env_file, override=False)

        raw_user_id = _required_environment("PFF_MCP_USER_ID")
        try:
            user_id = int(raw_user_id)
        except ValueError as error:
            raise ReadOnlyConfigurationError(
                "PFF_MCP_USER_ID deve ser um inteiro positivo."
            ) from error

        port_text = _required_environment("PFF_MCP_DB_PORT")
        try:
            port = int(port_text)
        except ValueError as error:
            raise ReadOnlyConfigurationError(
                "PFF_MCP_DB_PORT deve ser um inteiro."
            ) from error

        connection_url = URL.create(
            drivername="mysql+pymysql",
            username=_required_environment("PFF_MCP_DB_USER"),
            password=_required_environment("PFF_MCP_DB_PASSWORD"),
            host=_required_environment("PFF_MCP_DB_HOST"),
            port=port,
            database=_required_environment("PFF_MCP_DB_NAME"),
        )
        engine = create_engine(
            connection_url,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        return cls(engine=engine, user_id=user_id)

    def _fetch_all(
        self,
        query_name: str,
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if query_name not in QUERIES:
            raise ReadOnlyConfigurationError("Consulta não registrada.")
        query_parameters: Dict[str, Any] = dict(parameters or {})
        # A identidade do processo sempre prevalece, inclusive para futuros
        # chamadores internos da fachada.
        query_parameters["usuario_id"] = self._user_id
        try:
            with self._engine.connect() as connection:
                result = connection.execute(
                    text(QUERIES[query_name]),
                    query_parameters,
                ).mappings().all()
            return [_serialize_row(row) for row in result]
        except SQLAlchemyError:
            raise ReadOnlyDataError(
                "Não foi possível consultar os dados financeiros."
            ) from None

    def _fetch_one(
        self,
        query_name: str,
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        rows = self._fetch_all(query_name, parameters)
        return rows[0] if rows else None

    @staticmethod
    def _validate_limit(limit: int, maximum: int = 20) -> int:
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ValueError("O limite deve ser um número inteiro.")
        if limit < 1 or limit > maximum:
            raise ValueError(
                "O limite deve estar entre 1 e {}.".format(maximum)
            )
        return limit

    def get_financial_summary(self) -> Dict[str, Any]:
        row = self._fetch_one("financial_summary") or {}
        total_entradas = float(row.get("total_entradas") or 0)
        total_saidas = float(row.get("total_saidas") or 0)
        total_investido = float(row.get("total_investido") or 0)
        currency = self._fetch_one("currency") or {}
        return {
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "total_investido": total_investido,
            "saldo_final": total_entradas - total_saidas - total_investido,
            "quantidade_transacoes": int(row.get("quantidade_transacoes") or 0),
            "moeda": currency.get("moeda") or "BRL",
            "criterio": "somente transacoes confirmadas",
        }

    def get_recent_transactions(self, limit: int = 5) -> Dict[str, Any]:
        valid_limit = self._validate_limit(limit)
        transactions = self._fetch_all(
            "recent_transactions",
            {"limite": valid_limit},
        )
        return {
            "transacoes": transactions,
            "quantidade": len(transactions),
            "limite": valid_limit,
            "criterio": "somente transacoes confirmadas",
        }

    def get_spending_by_category(
        self,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        valid_limit = self._validate_limit(limit)
        normalized_category = None
        if category is not None:
            normalized_category = str(category).strip()
            if not normalized_category:
                normalized_category = None
            elif len(normalized_category) > 100:
                raise ValueError("A categoria deve possuir no máximo 100 caracteres.")
        rows = self._fetch_all(
            "spending_by_category",
            {"categoria": normalized_category, "limite": valid_limit},
        )
        categories = [
            {
                "categoria": row.get("categoria") or "outros",
                "valor": float(row.get("valor") or 0),
            }
            for row in rows
        ]
        return {
            "categorias": categories,
            "quantidade": len(categories),
            "filtro_categoria": normalized_category,
            "criterio": "somente saidas confirmadas",
        }

    def get_active_goal(self) -> Dict[str, Any]:
        row = self._fetch_one("active_goal")
        if row is None:
            return {"meta": None, "mensagem": "Nenhuma meta ativa encontrada."}
        target = float(row.get("valor_meta") or 0)
        current = float(row.get("valor_atual") or 0)
        percentage = min((current / target) * 100, 100) if target > 0 else 0
        return {
            "meta": {
                "titulo": row.get("titulo"),
                "valor_meta": target,
                "valor_atual": current,
                "data_limite": row.get("data_limite"),
                "percentual": round(percentage, 1),
                "valor_restante": round(max(target - current, 0), 2),
            }
        }

    def get_investment_summary(self) -> Dict[str, Any]:
        row = self._fetch_one("investment_summary") or {}
        total_aplicado = float(row.get("total_aplicado") or 0)
        valor_atual = float(row.get("valor_atual_total") or 0)
        result = float(row.get("lucro_prejuizo") or 0)
        distribution_rows = self._fetch_all("investment_distribution")
        distribution = [
            {
                "tipo": item.get("tipo"),
                "quantidade": int(item.get("quantidade") or 0),
                "valor_atual": float(item.get("valor_atual") or 0),
            }
            for item in distribution_rows
        ]
        return {
            "quantidade_total": int(row.get("quantidade_total") or 0),
            "quantidade_ativos": int(row.get("quantidade_ativos") or 0),
            "total_aplicado": total_aplicado,
            "valor_atual_total": valor_atual,
            "lucro_prejuizo": result,
            "rentabilidade_total": (
                (result / total_aplicado) * 100 if total_aplicado > 0 else 0
            ),
            "distribuicao_por_tipo": distribution,
            "criterio": "valores monetarios somente de investimentos ativos",
        }

    def list_categories(self) -> Dict[str, Any]:
        rows = self._fetch_all("categories")
        categories = [str(row["nome"]) for row in rows if row.get("nome")]
        return {"categorias": categories, "quantidade": len(categories)}
