# Documentação do Personal Finance Flow

Bem-vindo à documentação organizada do Personal Finance Flow!

## Estrutura

```
docs/
├── README.md
├── agent.md
├── arquitetura.md
├── vibe-coding.md
├── product/
│   ├── visao-do-produto.md
│   ├── requisitos-gerais.md
│   ├── arquitetura-geral.md
│   └── roadmap.md
├── prd/
│   ├── 00-prd-geral.md
│   ├── 01-estrutura-inicial.md
│   ├── 02-banco-de-dados.md
│   ├── 03-autenticacao.md
│   ├── 04-protecao-de-rotas.md
│   ├── 05-pipeline-etl.md
│   ├── 06-upload-csv.md
│   ├── 07-transacoes.md
│   ├── 08-dashboard.md
│   ├── 09-categorias.md
│   ├── 10-metas.md
│   ├── 11-relatorios.md
│   ├── 12-investimentos.md
│   ├── 13-agent-financeiro.md
│   ├── 14-configuracoes.md
│   ├── 15-brain.md
│   ├── 16-skill.md
│   ├── 17-mcp.md
│   ├── 18-testes.md
│   ├── 19-seguranca.md
│   └── 20-entrega.md
├── prompts/
│   ├── README.md
│   ├── 01-estrutura-inicial.prompt.md
│   ├── 02-banco-de-dados.prompt.md
│   ├── 03-cadastro.prompt.md
│   ├── 04-login-sessao.prompt.md
│   ├── 05-protecao-rotas.prompt.md
│   ├── 06-pipeline-etl.prompt.md
│   ├── 07-upload-csv.prompt.md
│   ├── 08-transacoes.prompt.md
│   ├── 09-dashboard.prompt.md
│   ├── 10-categorias.prompt.md
│   ├── 11-metas.prompt.md
│   ├── 12-relatorios.prompt.md
│   ├── 13-investimentos.prompt.md
│   ├── 14-agent.prompt.md
│   ├── 15-configuracoes.prompt.md
│   ├── 16-brain.prompt.md
│   ├── 17-skill.prompt.md
│   ├── 18-mcp.prompt.md
│   ├── 19-testes.prompt.md
│   ├── 20-auditoria.prompt.md
│   └── 21-zip-entrega.prompt.md
└── adr/
    ├── 001-flask-como-backend.md
    ├── 002-mysql-como-banco.md
    ├── 003-pandas-no-pipeline.md
    └── 004-isolamento-por-usuario.md
```

## Navegação

### 🎯 Product - Documentação de Negócio
- [Visão do Produto](product/visao-do-produto.md) - Problema, público-alvo, value proposition
- [Requisitos Gerais](product/requisitos-gerais.md) - RFs, RNFs, regras de negócio
- [Arquitetura Geral](product/arquitetura-geral.md) - Visão de alto nível da stack
- [Roadmap](product/roadmap.md) - Features concluídas e próximos passos

### 📋 PRDs - Product Requirements Documents
PRDs detalhados por feature (00 a 20)

### 💬 Prompts - Histórico de Desenvolvimento
Sequência completa de prompts usados no desenvolvimento (01 a 21)

### 🏗️ ADRs - Architectural Decision Records
Decisões técnicas importantes (001 a 004)

### 📄 Documentos Gerais
- [Agent](agent.md) - Assistente financeiro híbrido
- [Arquitetura](arquitetura.md) - Arquitetura técnica detalhada
- [Vibe Coding](vibe-coding.md) - Metodologia de desenvolvimento

## Documentação Técnica Detalhada

A documentação técnica mais profunda (modelo de dados, pipeline ETL, etc.) ainda está disponível no vault em [`../brain/`](../brain/).
