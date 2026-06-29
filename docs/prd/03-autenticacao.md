# PRD 03: Autenticação

## Objetivo

Implementar cadastro e login de usuários com segurança.

## Funcionalidades

### Cadastro

- Campos obrigatórios: nome, email, senha, confirmação de senha
- Campo opcional: telefone
- Validações:
  - Nome ≥ 3 caracteres
  - Email válido
  - Senha ≥ 6 caracteres
  - Senha e confirmação coincidem
  - Email único no sistema
- Senha armazenada como hash PBKDF2-SHA256 (nunca texto plano)

### Login

- Campos: email, senha
- Valida credenciais contra hash armazenado
- Cria sessão Flask com `usuario_id`, `usuario_nome`, `usuario_email`

## Critérios de Aceitação

- [ ] Página de cadastro funcional
- [ ] Página de login funcional
- [ ] Senhas armazenadas como hash
- [ ] Sessão criada após login
