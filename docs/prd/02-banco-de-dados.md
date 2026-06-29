# PRD 02: Banco de Dados

## Objetivo

Definir e implementar o schema do banco de dados MySQL.

## Tabelas Principais

| Tabela | Objetivo |
|---|---|
| `usuarios` | Dados dos usuários (nome, email, hash da senha) |
| `transacoes` | Transações financeiras (data, descrição, valor, tipo, categoria) |
| `categorias` | Categorias de transações (nome, palavras-chave, cor) |
| `metas` | Metas financeiras (título, valor alvo, valor atual, status) |
| `investimentos` | Dados de investimentos (nome, tipo, valor aplicado, valor atual) |
| `configuracoes_usuario` | Preferências do usuário (tema, moeda, formato de data, etc.) |

## Isolamento por Usuário

Todas as tabelas (exceto `usuarios`) devem ter coluna `usuario_id` para garantir que cada usuário acesse apenas seus próprios dados.

## Critérios de Aceitação

- [ ] Schema SQL criado
- [ ] Todas as tabelas com `usuario_id` (exceto `usuarios`)
- [ ] Índices nas colunas de busca frequente
