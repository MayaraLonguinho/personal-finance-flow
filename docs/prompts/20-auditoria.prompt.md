# Prompt 20: Auditoria

Realize auditoria de segurança e qualidade:

1. **Segurança**:
   - Verificar todas as consultas: têm WHERE usuario_id?
   - Verificar senhas: todas hash PBKDF2-SHA256? Nenhuma texto plano?
   - Verificar SQL: todas parametrizadas? Nenhuma concatenação?
   - Verificar credenciais: nenhuma no código, só no .env?
   - Verificar .gitignore: .env, .venv, __pycache__, uploads/ estão lá?

2. **Qualidade**:
   - Nenhum arquivo temporário na raiz
   - .env.example completo
   - requirements.txt com todas dependências
   - README principal atualizado
   - Documentação em docs/ organizada

3. **Isolamento**:
   - Testar que usuário A não vê transações do usuário B
   - Testar que categorias/metas/investimentos também são isolados
