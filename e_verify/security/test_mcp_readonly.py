import ast
from decimal import Decimal
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROOT = PROJECT_ROOT.parent
MCP_ROOT = ROOT / "d_traceability" / "mcp"
sys.path.insert(0, str(ROOT))

from d_traceability.mcp.allowed_resources import (  # noqa: E402
    ALLOWED_RESOURCES,
    ControlledResourceError,
    read_controlled_resource,
)
from d_traceability.mcp.readonly_service import (  # noqa: E402
    FORBIDDEN_SQL,
    QUERIES,
    ReadOnlyFinanceService,
    validate_readonly_queries,
)


class FakeMappings:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return FakeMappings(self._rows)


class FakeConnection:
    def __init__(self, engine):
        self._engine = engine

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, parameters):
        sql = " ".join(str(statement).split())
        self._engine.calls.append((sql, dict(parameters)))
        for marker, rows in self._engine.responses.items():
            if marker in sql:
                return FakeResult(rows)
        return FakeResult([])


class FakeEngine:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def connect(self):
        return FakeConnection(self)


class ReadOnlyQueryTests(unittest.TestCase):
    def test_all_queries_are_select_and_scoped(self):
        validate_readonly_queries()
        for query in QUERIES.values():
            normalized = " ".join(query.split())
            self.assertTrue(normalized.upper().startswith("SELECT "))
            self.assertIsNone(FORBIDDEN_SQL.search(normalized))
            self.assertIn(":usuario_id", normalized)

    def test_user_id_is_always_injected_by_service(self):
        engine = FakeEngine()
        service = ReadOnlyFinanceService(engine=engine, user_id=37)
        service.get_recent_transactions(limit=3)
        self.assertTrue(engine.calls)
        for _sql, parameters in engine.calls:
            self.assertEqual(parameters["usuario_id"], 37)

    def test_internal_parameters_cannot_override_fixed_user_id(self):
        engine = FakeEngine()
        service = ReadOnlyFinanceService(engine=engine, user_id=37)

        service._fetch_all("currency", {"usuario_id": 999})

        self.assertEqual(engine.calls[0][1]["usuario_id"], 37)

    def test_limits_are_bounded(self):
        service = ReadOnlyFinanceService(engine=FakeEngine(), user_id=1)
        for invalid in (0, 21, True, "5"):
            with self.assertRaises(ValueError):
                service.get_recent_transactions(limit=invalid)

    def test_summary_preserves_financial_formula(self):
        engine = FakeEngine(
            {
                "FROM transacoes": [
                    {
                        "total_entradas": Decimal("1000.00"),
                        "total_saidas": Decimal("250.00"),
                        "total_investido": Decimal("100.00"),
                        "quantidade_transacoes": 4,
                    }
                ],
                "FROM configuracoes_usuario": [{"moeda": "BRL"}],
            }
        )
        service = ReadOnlyFinanceService(engine=engine, user_id=1)
        summary = service.get_financial_summary()
        self.assertEqual(summary["saldo_final"], 650.0)
        self.assertEqual(summary["quantidade_transacoes"], 4)
        self.assertEqual(summary["moeda"], "BRL")

    def test_active_goal_is_derived_without_writing(self):
        engine = FakeEngine(
            {
                "FROM metas": [
                    {
                        "titulo": "Reserva",
                        "valor_meta": Decimal("1000"),
                        "valor_atual": Decimal("400"),
                        "data_limite": None,
                    }
                ]
            }
        )
        goal = ReadOnlyFinanceService(engine=engine, user_id=1).get_active_goal()
        self.assertEqual(goal["meta"]["percentual"], 40.0)
        self.assertEqual(goal["meta"]["valor_restante"], 600.0)


class ToolSurfaceTests(unittest.TestCase):
    def test_only_approved_tools_are_declared_without_user_id(self):
        tree = ast.parse((MCP_ROOT / "server.py").read_text(encoding="utf-8"))
        tools = {}
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            is_tool = any(
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "tool"
                for decorator in node.decorator_list
            )
            if is_tool:
                tools[node.name] = [argument.arg for argument in node.args.args]
        self.assertEqual(
            set(tools),
            {
                "get_financial_summary",
                "get_recent_transactions",
                "get_spending_by_category",
                "get_active_goal",
                "get_investment_summary",
                "list_categories",
            },
        )
        for arguments in tools.values():
            self.assertNotIn("usuario_id", arguments)
            self.assertNotIn("user_id", arguments)
            self.assertNotIn("sql", arguments)
            self.assertNotIn("query", arguments)

    def test_server_does_not_import_application_or_write_modules(self):
        source = (MCP_ROOT / "server.py").read_text(encoding="utf-8")
        self.assertNotIn("import app", source)
        self.assertNotIn("src.load", source)
        self.assertNotIn("src.configuracoes", source)


class ControlledResourceTests(unittest.TestCase):
    def test_allowlist_contains_only_documentation_and_schema(self):
        self.assertEqual(
            set(ALLOWED_RESOURCES),
            {"overview", "architecture", "data-model", "etl", "schema"},
        )
        for path in ALLOWED_RESOURCES.values():
            self.assertIn(path.suffix, {".md", ".sql"})
            self.assertNotIn(".env", path.name)
            self.assertNotIn("uploads", path.parts)

    def test_unknown_resource_is_rejected(self):
        with self.assertRaises(ControlledResourceError):
            read_controlled_resource("../../.env")

    def test_allowed_resource_can_be_read(self):
        content = read_controlled_resource("overview")
        self.assertIn("Personal Finance Flow", content)


if __name__ == "__main__":
    unittest.main()
