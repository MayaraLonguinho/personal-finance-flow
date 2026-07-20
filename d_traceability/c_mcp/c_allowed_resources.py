"""Resources MCP limitados a uma allowlist imutável do projeto."""

from pathlib import Path
from typing import Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_RESOURCE_BYTES = 256 * 1024

ALLOWED_RESOURCES: Dict[str, Path] = {
    "overview": PROJECT_ROOT / "d_traceability" / "a_brain" / "a_visao_geral.md",
    "architecture": PROJECT_ROOT / "d_traceability" / "a_brain" / "c_arquitetura.md",
    "data-model": PROJECT_ROOT / "d_traceability" / "a_brain" / "d_modelo_de_dados.md",
    "etl": PROJECT_ROOT / "d_traceability" / "a_brain" / "e_pipeline_etl.md",
    "schema": PROJECT_ROOT / "h_database" / "a_schema.sql",
}


class ControlledResourceError(RuntimeError):
    """Falha sanitizada de leitura de resource."""


def read_controlled_resource(name: str) -> str:
    """Lê somente um arquivo previamente cadastrado na allowlist."""
    if name not in ALLOWED_RESOURCES:
        raise ControlledResourceError("Resource não permitido.")

    root = PROJECT_ROOT.resolve()
    path = ALLOWED_RESOURCES[name].resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ControlledResourceError("Resource fora do projeto.") from None

    if path.suffix not in {".md", ".sql"}:
        raise ControlledResourceError("Tipo de resource não permitido.")
    try:
        size = path.stat().st_size
        if size > MAX_RESOURCE_BYTES:
            raise ControlledResourceError("Resource excede o limite permitido.")
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise ControlledResourceError("Não foi possível ler o resource.") from None
