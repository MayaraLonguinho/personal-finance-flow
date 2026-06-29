# Personal Finance Flow — roteiro de 3 slides

## Slide 1 — Do problema à proposta

**Problema**

- Dados financeiros dispersos e difíceis de acompanhar.
- Importações manuais sujeitas a repetição e inconsistências.
- Necessidade de separar com segurança os dados de cada usuário.

**Proposta**

- Aplicação web para importar, organizar e consultar finanças pessoais.
- Dashboard, relatórios e assistente em uma experiência integrada.

**Objetivo**

- Transformar transações em informação clara, preservando o isolamento por usuário.

## Slide 2 — Arquitetura end-to-end

**Fluxo principal**

`CSV → Pandas → categorização → deduplicação → MySQL → Flask/Jinja → dashboard`

- **Banco:** usuários, transações, categorias, metas, investimentos e configurações.
- **CRUDs:** transações, categorias, metas e investimentos; configurações com restauração.
- **Agent:** OpenAI com tools financeiras e fallback local baseado em regras.
- **Skill:** orienta a análise e importação de CSV usando o pipeline existente.
- **Brain:** vault Obsidian com requisitos, arquitetura, dados, ETL e aprendizados.
- **MCP:** servidor local somente leitura, com 6 tools e 5 resources controlados.

**Segurança**

- Sessão Flask e consultas filtradas por `usuario_id`.
- MCP sem escrita, SQL arbitrário ou acesso livre a arquivos.

## Slide 3 — Demonstração e evolução

**Demonstração sugerida**

1. Entrar e importar um CSV.
2. Exibir dashboard, filtros, meta e investimentos.
3. Fazer uma pergunta ao assistente financeiro.
4. Mostrar a superfície somente leitura do MCP.

**Resultados confirmados**

- Fluxo web integrado do CSV ao dashboard.
- Preferências e dados financeiros isolados por usuário nas rotas atuais.
- MCP com 11 testes automatizados e protocolo `stdio` validado.

**Aprendizados**

- Contratos entre módulos precisam de testes.
- Isolamento deve existir na rota e na consulta.
- IA deve acessar números por ferramentas controladas.

**Próximos passos**

- Testar Flask, CRUDs, ETL e isolamento com MySQL.
- Corrigir o pipeline standalone e fortalecer a integridade do schema.
- Validar o MCP com uma conta real somente leitura no Windsurf.
