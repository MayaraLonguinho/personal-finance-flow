# PRD 06: Upload CSV

## Objetivo

Interface para usuário enviar arquivos CSV e visualizar resultado do pipeline ETL.

## Fluxo de Importação CSV

```mermaid
flowchart TD
    A[Usuário seleciona arquivo CSV] --> B{Validação inicial}
    B -->|Arquivo vazio| C[Erro: arquivo vazio]
    B -->|Extensão inválida| D[Erro: apenas .csv]
    B -->|Válido| E[Armazenar em g_uploads/]
    
    E --> F[Ler CSV com Pandas]
    F --> G[Validar colunas obrigatórias]
    G -->|Faltando colunas| H[Erro: colunas obrigatórias]
    G -->|Colunas OK| I[Normalizar dados]
    
    I --> J[Padronizar datas e valores]
    J --> K[Aplicar categorização automática]
    K --> L[Detectar duplicatas no arquivo]
    L --> M[Remover duplicatas do arquivo]
    
    M --> N[Comparar com banco MySQL]
    N --> O[Ignorar duplicatas do banco]
    O --> P[Inserir transações novas]
    
    P --> Q[Gerar relatório]
    Q --> R[Exibir: total recebidas]
    R --> S[Exibir: importadas com sucesso]
    S --> T[Exibir: ignoradas]
    T --> U[Exibir: categorizadas automaticamente]
    U --> V[Limpar arquivo temporário]
    
    style C fill:#ffcccc
    style D fill:#ffcccc
    style H fill:#ffcccc
    style V fill:#ccffcc
```

**Explicação:** O diagrama mostra o fluxo completo de importação CSV, desde a seleção do arquivo pelo usuário até a exibição do relatório final, incluindo validações, normalização, categorização automática, deduplicação e carga no banco MySQL.

## Funcionalidades

### Upload

- Área de drop/upload no dashboard
- Aceita apenas arquivos `.csv`
- Valida:
  - Arquivo não está vazio
  - Extensão correta
- Armazena arquivo temporariamente em `g_uploads/`

### Feedback

- Mostra progresso durante o processamento
- Apresenta relatório com:
  - Total de linhas recebidas
  - Total importadas com sucesso
  - Total ignoradas (duplicatas ou inválidas)
  - Total categorizadas automaticamente

## Critérios de Aceitação

- [ ] Upload funcional com validação
- [ ] Relatório de resultado exibido
- [ ] Arquivos temporários são limpos após uso
