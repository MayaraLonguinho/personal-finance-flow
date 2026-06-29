# PRD 19: Segurança

## Objetivo

Garantir que a aplicação é segura e os dados dos usuários estão protegidos.

## Medidas de Segurança

### Autenticação

- Senhas armazenadas como hash PBKDF2-SHA256 (nunca texto plano)
- Sessões Flask com `SECRET_KEY` forte (deve ser configurada via env)
- Logout invalida sessão

### Isolamento de Dados

- Toda consulta SQL tem `WHERE usuario_id = :usuario_id`
- `ContextVar` garante usuário correto
- Nenhum usuário acessa dados de outro

### Prevenção de Ataques

- SQL Injection: usar apenas SQL parametrizado (nunca concatenação)
- XSS: escapar dados no frontend, usar Jinja2 autoescape
- CSRF: usar proteção CSRF do Flask (se aplicável)
- Validação de todas as entradas do usuário

### Credenciais

- Armazenadas em `.env`, não no código
- `.env` no `.gitignore`
- `.env.example` fornecido sem valores reais

## Critérios de Aceitação

- [ ] Senhas são hasheadas
- [ ] Isolamento entre usuários funciona
- [ ] SQL parametrizado sempre
- [ ] Credenciais não estão no repositório
