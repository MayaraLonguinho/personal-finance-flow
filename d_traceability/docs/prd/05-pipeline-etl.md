# PRD 05: Pipeline ETL

## Objetivo

Implementar pipeline de Extract, Transform, Load para importar transações de arquivos CSV.

## Etapas do Pipeline

### 1. Extract (Extração)

- Lê arquivo CSV usando Pandas
- Detecta encoding e separador automaticamente (se possível)
- Valida que as colunas mínimas existem

### 2. Transform (Transformação)

- Limpa dados:
  - Remove espaços em branco
  - Padroniza datas
  - Padroniza valores monetários
  - Normaliza texto
- Aplica categorização automática baseada em palavras-chave

### 3. Load (Carga)

- Compara linhas do CSV com transações existentes
- Ignora duplicatas
- Insere apenas transações novas no banco
- Retorna estatísticas: total recebidas, importadas, ignoradas, categorizadas

## Critérios de Aceitação

- [ ] CSV válido é processado completamente
- [ ] Dados são limpos e padronizados
- [ ] Categorização automática é aplicada
- [ ] Duplicatas são ignoradas
- [ ] Estatísticas são retornadas
