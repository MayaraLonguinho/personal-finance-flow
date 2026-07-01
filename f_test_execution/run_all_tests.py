#!/usr/bin/env python3
"""
Executa todos os testes automatizados do projeto.
Gera relatório com timestamp em f_test_execution/reports/.
"""

import os
import sys
import unittest
from pathlib import Path
from datetime import datetime

# Adiciona raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def use_preferred_python():
    if os.getenv("VIRTUAL_ENV"):
        preferred = Path(os.getenv("VIRTUAL_ENV")) / "bin" / "python"
        if preferred.exists():
            return str(preferred)
    fallback = PROJECT_ROOT / ".venv" / "bin" / "python3"
    if fallback.exists():
        return str(fallback)
    return None


def reexec_if_needed():
    preferred = use_preferred_python()
    if preferred is None:
        return
    current = Path(sys.executable)
    preferred_path = Path(preferred)
    if current != preferred_path:
        os.execv(preferred, [preferred, str(Path(__file__).resolve())] + sys.argv[1:])

# Diretório de relatórios
REPORTS_DIR = PROJECT_ROOT / "f_test_execution" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp para nome do relatório
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
REPORT_FILE = REPORTS_DIR / f"test_report_{TIMESTAMP}.txt"


def discover_suite(loader, start_dir):
    if not start_dir.exists():
        return None
    return loader.discover(
        start_dir=str(start_dir),
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT),
    )


def main():
    """Executa todos os testes e gera relatório."""
    print(f"Executando todos os testes...")
    print(f"Relatório será salvo em: {REPORT_FILE}")
    print("-" * 60)

    loader = unittest.TestLoader()
    suites = {}
    suite_directories = {
        "unit": PROJECT_ROOT / "e_verify" / "unit",
        "integration": PROJECT_ROOT / "e_verify" / "integration",
        "security": PROJECT_ROOT / "e_verify" / "security",
    }

    total_tests = 0
    for label, path in suite_directories.items():
        if path.exists():
            suite = discover_suite(loader, path)
            if suite is None:
                continue
            suites[label] = suite
            total_tests += suite.countTestCases()
            print(f"Suíte {label}: {suite.countTestCases()} testes encontrados")
        else:
            print(f"Suíte {label} não encontrada em: {path}")

    if total_tests == 0:
        print("Erro: nenhuma suíte de testes encontrada ou nenhum teste foi descoberto.")
        sys.exit(2)

    combined_suite = unittest.TestSuite(suites.values())

    with open(REPORT_FILE, "w") as report:
        runner = unittest.TextTestRunner(
            stream=report,
            verbosity=2,
            failfast=False,
        )
        result = runner.run(combined_suite)

    successes = result.testsRun - len(result.failures) - len(result.errors)
    print("-" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Sucessos: {successes}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Relatório salvo em: {REPORT_FILE}")

    if result.testsRun == 0 or result.failures or result.errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    reexec_if_needed()
    main()
