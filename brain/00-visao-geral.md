---
title: Visão geral
tags:
  - personal-finance-flow
  - visão-geral
  - projeto
---

# Visão geral

> [!info] Escopo desta nota
> Retrato do projeto conforme os arquivos atuais do repositório. As divergências conhecidas estão detalhadas em [[06-erros-e-aprendizados]].

## O que é

Personal Finance Flow é uma aplicação web de finanças pessoais. O sistema combina uma interface Flask renderizada com Jinja, APIs JSON, processamento tabular com Pandas e persistência em MySQL por meio de SQLAlchemy.

O objetivo declarado no `README.md` é permitir importar transações de CSV, tratá-las, armazená-las no MySQL e visualizar indicadores financeiros. O código atual amplia esse escopo com autenticação, CRUD de transações, categorias, metas, investimentos, relatórios, configurações por usuário e um assistente financeiro com OpenAI e fallback local.

## Capacidades implementadas

- Cadastro, login e logout de usuários.
- Sessão Flask com `usuario_id`, nome e e-mail.
- Dashboard com resumo financeiro, gráficos, insights e transações recentes.
- Cadastro, edição, exclusão, filtro e importação CSV de transações.
- Categorização automática baseada em palavras-chave.
- CRUD de categorias e estatísticas por categoria.
- Gestão de uma meta ativa e cálculo de progresso.
- CRUD, filtros e resumo de investimentos.
- Relatórios por intervalo de datas.
- Assistente financeiro baseado em ferramentas OpenAI, com agente local como fallback.
- Preferências individuais de nome, tema, moeda, formato de data, limite de transações recentes, confirmação de exclusão e cards visíveis.

## Tecnologias confirmadas

| Área | Tecnologia |
|---|---|
| Backend web | Python, Flask 3.1.3 |
| Templates | Jinja2 |
| Frontend | HTML, CSS e JavaScript sem framework |
| Dados tabulares | Pandas 2.3.3 e NumPy |
| Banco | MySQL via PyMySQL |
| Acesso a dados | SQLAlchemy 2.0.50, SQL textual e `pandas.read_sql`/`to_sql` |
| Autenticação | Sessão Flask e hashes Werkzeug PBKDF2-SHA256 |
| IA | OpenAI Python SDK; modelo padrão `gpt-4o-mini` |
| Configuração | Variáveis de ambiente com `python-dotenv` |
| Gráficos | Chart.js carregado pelo template do dashboard |

## Fluxo principal do usuário

1. O visitante acessa a página pública, cadastra uma conta ou realiza login.
2. Após o login, o Flask grava o identificador do usuário na sessão.
3. As páginas protegidas consultam APIs que passam o `usuario_id` aos módulos de domínio.
4. O usuário pode cadastrar transações manualmente ou importar um CSV.
5. As transações confirmadas alimentam métricas, gráficos, insights e consultas do assistente; os relatórios consultam as transações do período sem impor o mesmo filtro de status.
6. Metas, categorias, investimentos e configurações são consultados no escopo da conta ativa.

## Estrutura funcional

| Caminho | Responsabilidade |
|---|---|
| `app.py` | Aplicação Flask, páginas, APIs, sessão e orquestração |
| `src/` | Regras de domínio, acesso ao banco, ETL, métricas e agentes |
| `templates/` | Páginas Jinja |
| `static/` | CSS, JavaScript e imagens |
| `database/schema.sql` | Definição declarativa das tabelas MySQL |
| `data/raw/` | CSV de entrada de exemplo |
| `data/processed/` | CSV tratado de exemplo |
| `uploads/` | Destino dos CSVs enviados pela aplicação |
| `brain/` | Este vault técnico |

## Estado observado

- A aplicação principal executa em `127.0.0.1:5001` com `debug=True` quando `app.py` é iniciado diretamente.
- O schema possui seis tabelas: `usuarios`, `transacoes`, `metas`, `categorias`, `investimentos` e `configuracoes_usuario`.
- A pasta `tests/` contém testes automatizados para MCP, categorias, categorização automática, upload API e isolamento de usuário.
- `docs/arquitetura.md` agora é uma página de navegação; `docs/vibe-coding.md` contém a metodologia de desenvolvimento.

## Navegação do vault

- [[01-requisitos|Requisitos]]
- [[02-arquitetura|Arquitetura]]
- [[03-modelo-de-dados|Modelo de dados]]
- [[04-pipeline-etl|Pipeline ETL]]
- [[05-decisoes-tecnicas|Decisões técnicas]]
- [[06-erros-e-aprendizados|Erros e aprendizados]]
- [[07-prompts|Prompts utilizados]]

## Fontes principais

`README.md`, `requirements.txt`, `app.py`, `database/schema.sql`, módulos de `src/`, templates e scripts de `static/js/`.
