# PRD 17: MCP (Model Context Protocol Server)

## Objetivo

Implementar servidor MCP para integração com agentes/assistentes.

## Estrutura do MCP

```
mcp/
├── server.py
├── requirements-mcp.txt
├── README.md
├── configuracao-exemplo.json
└── (outros módulos se necessários)
```

## Funcionalidades do Servidor MCP

### Ferramentas (Tools) Apenas Leitura

- consultar_saldo
- consultar_entradas
- consultar_saidas
- consultar_categorias
- consultar_meta_ativa
- consultar_resumo_financeiro
- (outras ferramentas de leitura)

### Resources

- Acesso controlado apenas a arquivos seguros (não .env, não dados sensíveis)
- Allowlist de caminhos permitidos

### Segurança

- Apenas SELECT no banco, sem UPDATE/INSERT/DELETE
- Usuário fixo configurado no servidor, sem permitir sobrescrever
- Nenhuma ferramenta recebe SQL arbitrário ou caminhos arbitrários
- Variáveis de ambiente com credenciais, não hardcode

## Critérios de Aceitação

- [ ] Servidor MCP funcional
- [ ] Apenas operações de leitura
- [ ] Segurança implementada
- [ ] README com instruções
- [ ] Arquivo de configuração exemplo
