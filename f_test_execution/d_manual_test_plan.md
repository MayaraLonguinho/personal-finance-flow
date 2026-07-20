# Plano de Testes Manuais

Este documento lista os itens a serem verificados manualmente no projeto.

## Funcionalidades a testar

### Autenticação
- [ ] Cadastro de novo usuário
- [ ] Login com credenciais válidas
- [ ] Login com credenciais inválidas
- [ ] Logout
- [ ] Acesso a páginas protegidas sem login (redirecionamento)

### Dashboard
- [ ] Carregamento do dashboard após login
- [ ] Exibição de cards de resumo financeiro
- [ ] Exibição de gráficos
- [ ] Exibição de transações recentes

### Upload CSV
- [ ] Upload de arquivo CSV válido
- [ ] Validação de extensão .csv
- [ ] Rejeição de arquivo vazio
- [ ] Deduplicação de transações
- [ ] Categorização automática
- [ ] Feedback de resultado (quantidade importada/ignorada)

### CRUD de Transações
- [ ] Listagem de transações
- [ ] Criação de nova transação
- [ ] Edição de transação
- [ ] Exclusão de transação
- [ ] Filtros por período, tipo, categoria

### Sincronização com Investimentos
- [ ] Criação de investimento via transação do tipo investimento
- [ ] Atualização de investimento ao editar transação vinculada
- [ ] Remoção de investimento ao excluir transação vinculada

### CRUD de Investimentos
- [ ] Listagem de investimentos
- [ ] Criação manual de investimento
- [ ] Edição de investimento
- [ ] Exclusão de investimento
- [ ] Resumo da carteira

### CRUD de Metas
- [ ] Consulta de meta ativa
- [ ] Criação de nova meta
- [ ] Edição de meta
- [ ] Exclusão de meta
- [ ] Progresso calculado

### CRUD de Categorias
- [ ] Listagem de categorias
- [ ] Criação de nova categoria
- [ ] Edição de categoria
- [ ] Exclusão de categoria (exceto "outros")
- [ ] Estatísticas por categoria

### Relatórios
- [ ] Geração de relatório por período
- [ ] Exportação via window.print
- [ ] Visualização de gastos por categoria

### Assistente
- [ ] Assistente local (sem OPENAI_API_KEY)
- [ ] Assistente OpenAI (com OPENAI_API_KEY configurada)
- [ ] Consulta de saldo
- [ ] Consulta de entradas/saídas
- [ ] Consulta de categorias
- [ ] Consulta de metas
- [ ] Consulta de investimentos

### Limpar todos os dados
- [ ] Remoção de investimentos
- [ ] Remoção de transações
- [ ] Remoção de metas
- [ ] Remoção de categorias
- [ ] Preservação de usuário e configurações

### Isolamento entre usuários
- [ ] Usuário A não vê dados do usuário B
- [ ] Usuário B não vê dados do usuário A
- [ ] Categorias podem ter mesmo nome em usuários diferentes
