# Prompt 18: MCP

Implemente o servidor MCP (Model Context Protocol):

1. **Estrutura**:
   - mcp/server.py
   - mcp/requirements-mcp.txt (dependências separadas, SDK MCP)
   - mcp/README.md
   - mcp/configuracao-exemplo.json

2. **Funcionalidades APENAS LEITURA**:
   - Ferramentas (tools): consultar_saldo, consultar_entradas, consultar_saidas, consultar_categorias, consultar_meta, consultar_transacoes_recentes, consultar_resumo_financeiro
   - Resources: allowlist de arquivos seguros (não .env, não dados sensíveis)

3. **Segurança MÁXIMA**:
   - Apenas SELECT, nenhum INSERT/UPDATE/DELETE
   - Usuário fixo configurado no servidor (não permite alterar via parâmetro)
   - Nenhuma tool aceita SQL arbitrário ou caminhos arbitrários
   - Credenciais via variáveis de ambiente (não hardcode)
   - Isolamento estrito

4. **Validação**:
   - Testes unitários em tests/test_mcp_readonly.py
   - Testar que não há escrita
   - Testar que usuário não pode ser sobrescrito
