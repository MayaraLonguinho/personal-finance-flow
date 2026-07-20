# PRD 05: Pipeline ETL

## Objetivo

Implementar pipeline de Extract, Transform, Load para importar transações de arquivos CSV.

## Pipeline ETL

```mermaid
flowchart LR
    subgraph Extract
        A[Arquivo CSV] --> B[a_extract.py]
        B --> C[pd.read_csv]
        C --> D[DataFrame bruto]
    end
    
    subgraph Transform
        D --> E[b_transform.py]
        E --> F[Normalizar colunas]
        F --> G[Validar colunas obrigatórias]
        G --> H[Padronizar datas e valores]
        H --> I[Normalizar texto]
        I --> J[c_categorization.py]
        J --> K[Aplicar regras de palavras-chave]
        K --> L[Detectar duplicatas no arquivo]
        L --> M[DataFrame tratado]
    end
    
    subgraph Load
        M --> N[d_load.py]
        N --> O[Comparar com banco MySQL]
        O --> P[Identificar duplicatas do banco]
        P --> Q[INSERT transações novas]
        Q --> R[Vincular investimentos]
        R --> S[Retornar estatísticas]
    end
    
    S --> T[Relatório final]
    
    style A fill:#fff4e1
    style D fill:#ffe1f5
    style M fill:#e1f5ff
    style T fill:#ccffcc
```

**Explicação:** O diagrama mostra o pipeline ETL completo. Na fase Extract, o arquivo CSV é lido com Pandas. Na fase Transform, os dados são normalizados, validados, padronizados e categorizados automaticamente. Na fase Load, os dados são comparados com o banco MySQL para evitar duplicatas, transações novas são inseridas, investimentos são vinculados e estatísticas são retornadas.

## Sequência Técnica do Upload CSV

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant B as Backend Flask
    participant E as a_extract.py
    participant T as b_transform.py
    participant C as c_categorization.py
    participant L as d_load.py
    participant M as MySQL
    
    U->>F: Seleciona arquivo CSV
    F->>B: POST /api/upload
    B->>B: Validar extensão .csv
    B->>B: Armazenar em g_uploads/
    
    B->>E: ler_csv(caminho)
    E-->>B: DataFrame bruto
    
    B->>T: processar_upload_csv(df, usuario_id)
    T->>T: Validar colunas obrigatórias
    T->>T: Normalizar dados
    T->>C: categorizar_dataframe(df, regras)
    C-->>T: DataFrame categorizado
    T->>T: Remover duplicatas do arquivo
    T-->>B: DataFrame tratado + relatório
    
    B->>L: carregar_transacoes_mysql(df, usuario_id)
    L->>M: SELECT transações existentes
    M-->>L: DataFrame existente
    L->>L: Comparar e identificar duplicatas
    L->>M: INSERT transações novas
    L->>M: INSERT investimentos (se aplicável)
    L-->>B: Estatísticas de carga
    
    B->>B: Limpar arquivo temporário
    B-->>F: JSON com relatório final
    F-->>U: Exibir resultado
```

**Explicação:** O diagrama de sequência mostra o fluxo técnico do upload CSV, desde a seleção do arquivo pelo usuário até a exibição do resultado final. O backend coordena a chamada dos módulos ETL (extract, transform, categorization, load), que interagem com o banco MySQL para deduplicação e carga de dados.

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
