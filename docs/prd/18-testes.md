# PRD 18: Testes

## Objetivo

Garantir qualidade do código através de testes automatizados.

## Tipos de Testes

### Testes Unitários

- Testar funções isoladamente
- Módulos como `src/metrics.py`, `src/categorias.py`, `src/utils.py`
- Mockar banco quando necessário

### Testes de Integração (se aplicável)

- Testar APIs Flask
- Testar pipeline ETL completo

### Testes de Segurança

- Isolamento por usuário: um usuário não vê dados de outro
- SQL Injection: tentar passar SQL malicioso, deve ser tratado como parâmetro
- Autenticação: rotas protegidas retornam 401 sem sessão

## Cobertura

- Testar fluxos principais
- Testar validações
- Testar limites (ex: valores negativos, datas inválidas)

## Critérios de Aceitação

- [ ] Pasta `tests/` existe
- [ ] Testes unitários para módulos principais
- [ ] Testes de segurança para isolamento
- [ ] Todos os testes passam
