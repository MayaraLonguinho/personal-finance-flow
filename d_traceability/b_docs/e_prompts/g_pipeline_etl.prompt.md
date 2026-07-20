# Prompt 06: Pipeline ETL

Implemente o pipeline ETL para CSV:

1. **Extract**: Lê arquivo CSV usando Pandas, detecta encoding/separador, valida colunas
2. **Transform**:
   - Limpa dados (remove espaços, padroniza datas/valores)
   - Normaliza texto
   - Aplica categorização automática baseada em palavras-chave
3. **Load**:
   - Compara com transações existentes para evitar duplicatas
   - Insere apenas transações novas
   - Retorna estatísticas: recebidas, importadas, ignoradas, categorizadas

Crie módulos separados: extract.py, transform.py, load.py, categorization.py.
