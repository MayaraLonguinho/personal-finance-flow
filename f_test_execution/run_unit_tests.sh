#!/bin/bash
# Executa testes unitários do projeto

set -e

if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
elif [ -x ".venv/bin/python3" ]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON="python3"
fi

echo "Executando testes unitários com $PYTHON..."
$PYTHON -m unittest discover -s e_verify/unit -v
