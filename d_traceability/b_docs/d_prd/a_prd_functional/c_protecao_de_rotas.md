# PRD 04: Proteção de Rotas

## Objetivo

Garantir que apenas usuários autenticados acessem rotas internas e que cada usuário só veja seus próprios dados.

## Funcionalidades

### Decorator `login_obrigatorio`

- Verifica se `usuario_id` existe na sessão
- Se não existir:
  - Redireciona para `/login` em rotas de página
  - Retorna HTTP 401 em APIs
- Se existir: permite acesso

### ContextVar para Usuário

- `before_request`: copia `session["usuario_id"]` para `ContextVar`
- `teardown_request`: limpa o `ContextVar`
- Módulos de domínio podem acessar o usuário atual sem receber parâmetro

### Isolamento em Consultas

Todas as consultas SQL devem incluir `WHERE usuario_id = :usuario_id`

## Critérios de Aceitação

- [ ] Rotas protegidas redirecionam para login sem sessão
- [ ] APIs retornam 401 sem sessão
- [ ] Todas as consultas filtram por `usuario_id`
- [ ] Nenhum usuário acessa dados de outro usuário
