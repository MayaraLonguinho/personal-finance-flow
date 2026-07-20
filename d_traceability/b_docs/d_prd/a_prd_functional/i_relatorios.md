# PRD 11: Relatórios

## Objetivo

Relatórios financeiros por período selecionado.

## Fluxo de Geração de Relatórios

```mermaid
flowchart TD
    A[Usuário acessa /relatorios] --> B[Verificar autenticação]
    B -->|Não autenticado| C[Redirecionar para /login]
    B -->|Autenticado| D[Exibir formulário de filtros]
    
    D --> E[Usuário informa data início]
    E --> F[Usuário informa data fim]
    F --> G{Validação}
    
    G -->|data início > data fim| H[Erro: período inválido]
    G -->|Válido| I[Consultar transações do período]
    
    I --> J[Calcular resumo financeiro]
    J --> K[Total de entradas do período]
    J --> L[Total de saídas do período]
    J --> M[Saldo do período]
    
    M --> N[Calcular gastos por categoria]
    N --> O[Agrupar por categoria]
    O --> P[Calcular percentuais]
    
    P --> Q[Listar transações do período]
    Q --> R[Ordenar por data decrescente]
    
    R --> S[Buscar resumo carteira investimentos]
    S --> T[Total investido atual]
    T --> U[Valor atual total]
    U --> V[Rentabilidade]
    
    V --> W[Aplicar formato de moeda]
    W --> X[Renderizar relatório]
    X --> Y[Botão de impressão]
    
    style C fill:#ffcccc
    style H fill:#ffcccc
    style X fill:#ccffcc
```

**Explicação:** O diagrama mostra o fluxo de geração de relatórios, desde a seleção do período até a renderização final. O sistema valida as datas, consulta transações do período, calcula resumo financeiro, gastos por categoria, lista transações e busca resumo da carteira de investimentos, aplicando o formato de moeda configurado pelo usuário.

## Funcionalidades

### Filtros

- Data início (YYYY-MM-DD)
- Data fim (YYYY-MM-DD)
- Valida que data início ≤ data fim

### Conteúdo do Relatório

- Resumo financeiro do período (entradas, saídas, saldo)
- Gastos por categoria no período
- Lista de transações do período
- Resumo da carteira de investimentos (atual, não por período)
- Botão de impressão

## Critérios de Aceitação

- [ ] Filtros por período funcionais
- [ ] Dados do período corretos
- [ ] Impressão formatada
