# Requisitos Gerais

## Requisitos Funcionais (RF)

| ID | Descrição |
|---|---|
| RF-01 | Autenticação de usuários (cadastro, login, logout) |
| RF-02 | Dashboard com resumo financeiro e visualizações |
| RF-03 | CRUD de transações (criar, ler, atualizar, excluir) |
| RF-04 | Importação de transações via CSV com ETL |
| RF-05 | Categorização automática e gestão de categorias |
| RF-06 | Gestão de metas financeiras |
| RF-07 | Gestão de investimentos |
| RF-08 | Relatórios por período |
| RF-09 | Assistente financeiro conversacional |
| RF-10 | Configurações personalizadas do usuário |

## Requisitos Não Funcionais (RNF)

| ID | Descrição |
|---|---|
| RNF-01 | Isolamento estrito de dados entre usuários |
| RNF-02 | Senhas armazenadas como hash (nunca texto plano) |
| RNF-03 | Carregamento do dashboard em < 2s |
| RNF-04 | Interface responsiva para mobile |
| RNF-05 | Suporte a arquivos CSV de até ~10k linhas |
| RNF-06 | Fallback local do assistente sem OpenAI |

## Regras de Negócio (RN)

| ID | Descrição |
|---|---|
| RN-01 | Saldo = entradas - saídas - investimentos |
| RN-02 | Categoria "outros" não pode ser excluída |
| RN-03 | Ao excluir categoria, transações vão para "outros" |
| RN-04 | Apenas uma meta ativa por usuário |
| RN-05 | Progresso da meta tem teto de 100% |
| RN-06 | Moeda é apenas formatação, não conversão |
