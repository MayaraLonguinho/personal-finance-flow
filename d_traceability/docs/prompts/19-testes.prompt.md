# Prompt 19: Testes

Adicione testes automatizados:

1. **Estrutura**:
   - tests/
   - tests/test_mcp_readonly.py (se houver MCP)
   - Outros arquivos de teste conforme necessidade

2. **Testes unitários**:
   - Testar módulos src/metrics.py, src/categorias.py, src/utils.py
   - Mockar banco quando necessário

3. **Testes de segurança**:
   - Isolamento: um usuário NÃO vê dados de outro
   - SQL Injection: passar SQL malicioso deve ser tratado como parâmetro, não executado
   - Autenticação: rotas protegidas retornam 401 sem sessão

4. **Cobertura**:
   - Fluxos principais
   - Validações
   - Casos limites (valores negativos, datas inválidas)
