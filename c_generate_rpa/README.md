# Pipeline RPA/ETL

Esta pasta contém os módulos do pipeline de extração, transformação, categorização e carga de dados financeiros.

## Fluxo

extract → transform → categorization → load

## Módulos

- `extract.py`: Extração de dados de arquivos CSV
- `transform.py`: Transformação e normalização de dados
- `categorization.py`: Categorização automática de transações
- `load.py`: Carga de dados no banco MySQL

## Formato esperado do CSV

O CSV deve conter as colunas obrigatórias:
- data
- descricao
- tipo (entrada, saida, investimento)
- valor
- status

## Uso

O pipeline é utilizado principalmente pela rota web `POST /api/upload` em `b_backend/app.py`.
