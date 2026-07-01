# PRD 10: Metas

## Objetivo

Permitir usuário definir e acompanhar metas financeiras.

## Funcionalidades

### CRUD de Metas

- Campos:
  - Título (obrigatório)
  - Valor alvo (> 0, obrigatório)
  - Valor atual (≥ 0)
  - Status (ativa/concluída/cancelada)
- Apenas uma meta pode estar com status "ativa" por vez

### Acompanhamento

- Cálculo automático do progresso percentual (teto de 100%)
- Cálculo do valor restante (piso de 0)
- Visualização no dashboard

## Critérios de Aceitação

- [ ] CRUD completo funcional
- [ ] Apenas uma meta ativa permitida
- [ ] Cálculos de progresso corretos
- [ ] Visualização no dashboard
