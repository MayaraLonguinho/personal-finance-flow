# ADR 003: Pandas no Pipeline ETL

## Status

✅ Aceito

## Contexto

Pipeline ETL para importar CSVs bancários precisava de:
- Leitura flexível de arquivos CSV
- Limpeza e transformação de dados tabulares
- Deduplicação
- Integração com banco de dados

## Decisão

Utilizar **Pandas 2.3.3** como principal biblioteca para o pipeline ETL.

## Justificativa

- Excelente para manipulação de dados tabulares
- Funções built-in para limpeza, normalização, deduplicação
- Integração direta com SQL (read_sql, to_sql)
- Já havia sido escolhida no projeto
- Python é a linguagem principal do backend

## Consequências

### Positivas
- ETL rápido e flexível
- Deduplicação fácil de implementar (comparar DataFrames)
- Transformações complexas simplificadas
- Integração MySQL perfeita

### Negativas
- Overhead de memória para CSVs muito grandes (mas o projeto tem limite razoável)
- Dependência adicional (mas já está no requirements.txt)
- Aprendizado de Pandas para quem não conhece

## Alternativas Consideradas
- csv module padrão do Python (muito manual para transformações complexas)
- Dask (para dados maiores que memória, overkill para o escopo)
- PySpark (muito complexo para o projeto)
