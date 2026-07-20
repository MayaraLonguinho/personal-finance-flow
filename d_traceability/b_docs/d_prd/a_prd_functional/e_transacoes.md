# PRD 07: Transações

## Objetivo

CRUD completo de transações financeiras.

## Estados de Transação

```mermaid
stateDiagram-v2
    [*] --> pendente: Criação
    pendente --> confirmado: Confirmação
    pendente --> cancelado: Cancelamento
    confirmado --> cancelado: Cancelamento
    cancelado --> [*]
    confirmado --> [*]
    
    note right of pendente
        Estado inicial
        Aguardando confirmação
    end note
    
    note right of confirmado
        Transação válida
        Incluída nos cálculos
    end note
    
    note right of cancelado
        Transação invalidada
        Não afeta saldo
    end note
```

**Explicação:** O diagrama mostra os estados possíveis de uma transação: pendente (estado inicial), confirmado (transação válida) e cancelado (transação invalidada). Transações podem ser confirmadas ou canceladas a partir do estado pendente, e transações confirmadas podem ser canceladas.

## Funcionalidades

### Listagem

- Mostra transações do usuário logado
- Filtros:
  - Por descrição (busca textual)
  - Por categoria
  - Por tipo (entrada/saída/investimento)
  - Por status (confirmado/pendente/cancelado)
- Ordenada por data decrescente

### Criação/Edição

- Campos obrigatórios:
  - Data
  - Descrição
  - Tipo (entrada/saída/investimento)
  - Valor (> 0)
  - Status
- Campo opcional: categoria
- Se categoria não informada, sugere baseada em regras

### Exclusão

- Confirmação antes de excluir (configurável pelo usuário)
- Remove apenas transação do usuário logado

## Critérios de Aceitação

- [ ] Listagem com filtros funcional
- [ ] Criação/edição com validações
- [ ] Exclusão com confirmação
- [ ] Todas operações respeitam `usuario_id`
