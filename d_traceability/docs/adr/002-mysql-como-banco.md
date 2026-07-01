# ADR 002: MySQL como Banco de Dados

## Status

✅ Aceito

## Contexto

Necessidade de banco de dados relacional para armazenar usuários, transações, categorias, metas, investimentos e configurações.

## Decisão

Utilizar **MySQL** via PyMySQL e SQLAlchemy Core (não ORM).

## Justificativa

- Banco relacional, perfeito para a estrutura de dados do projeto
- Integração excelente com Pandas (read_sql, to_sql)
- Já havia sido escolhido no início do projeto
- Ampla documentação e suporte
- Funciona bem com o isolamento por usuário (WHERE usuario_id)

## Consequências

### Positivas
- ACID compliance para transações financeiras
- Integração Pandas direta (ótima para ETL e relatórios)
- Robusto e confiável
- Suporta escalabilidade

### Negativas
- Requer servidor MySQL rodando (mais complexo que SQLite para setup inicial)
- Sem chaves estrangeiras definidas no schema atual (dependência de código para integridade)
- Não é serverless como SQLite

## Alternativas Consideradas
- SQLite (simples, mas menos adequado para multi-usuário produção)
- PostgreSQL (similar, mas MySQL já havia sido escolhido)
