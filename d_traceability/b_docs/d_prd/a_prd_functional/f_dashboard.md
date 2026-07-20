# PRD 08: Dashboard

## Objetivo

Página principal com visão geral das finanças do usuário.

## Fluxo de Geração do Dashboard

```mermaid
flowchart TD
    A[Usuário acessa /dashboard] --> B[Verificar autenticação]
    B -->|Não autenticado| C[Redirecionar para /login]
    B -->|Autenticado| D[Obter configuracoes_usuario]
    
    D --> E[Calcular métricas principais]
    E --> F[Total de entradas]
    E --> G[Total de saídas]
    E --> H[Total de investimentos]
    E --> I[Saldo = entradas - saídas - investimentos]
    
    I --> J[Buscar transações recentes]
    J --> K[Filtrar por configuracoes.qtd_transacoes_recentes]
    
    K --> L[Buscar meta ativa]
    L --> M[Calcular progresso percentual]
    M --> N[Calcular valor restante]
    
    N --> O[Buscar resumo investimentos]
    O --> P[Calcular rentabilidade]
    
    P --> Q[Gerar gráficos Chart.js]
    Q --> R[Gastos por categoria]
    Q --> S[Evolução do saldo]
    Q --> T[Comparativo mensal]
    
    T --> U[Aplicar tema configurado]
    U --> V[Aplicar formato de moeda]
    V --> W[Renderizar dashboard]
    
    style C fill:#ffcccc
    style W fill:#ccffcc
```

**Explicação:** O diagrama mostra o fluxo de geração do dashboard, desde a verificação de autenticação até a renderização final. O sistema obtém as configurações do usuário, calcula métricas financeiras, busca transações recentes, meta ativa e resumo de investimentos, gera gráficos com Chart.js e aplica as preferências de tema e moeda do usuário.

## Funcionalidades

### Cards de Métricas

- Total de entradas (período padrão)
- Total de saídas
- Total de investimentos
- Saldo calculado (entradas - saídas - investimentos)
- Cards visíveis configuráveis pelo usuário

### Gráficos (Chart.js)

- Gastos por categoria (gráfico de pizza/rosca)
- Evolução do saldo ao longo do tempo (linha)
- Comparativo entradas vs saídas mensais (barras)

### Outras Seções

- Transações recentes confirmadas (quantidade configurável)
- Resumo da meta ativa
- Resumo da carteira de investimentos
- Insights automáticos

## Critérios de Aceitação

- [ ] Todas as métricas calculadas corretamente
- [ ] Gráficos renderizados sem erros
- [ ] Atualizado em tempo real após alterações
- [ ] Respeita configurações do usuário (tema, moeda, etc.)
