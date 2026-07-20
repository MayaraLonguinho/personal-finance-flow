# Migrations do Banco de Dados

## 001 - Correção do Modelo Multiusuário das Categorias

### Por que esta migration?

O modelo anterior tinha os seguintes problemas:
1. `usuario_id` aceitava NULL, permitindo categorias sem associação a usuário
2. Constraint UNIQUE apenas na coluna `nome`, impedindo que dois usuários tivessem categorias com o mesmo nome
3. Sem Foreign Key para `usuarios(id)`, sem garantia referencial

### Como funciona a unicidade composta?

A nova constraint `uk_categorias_usuario_nome` garante que:
- O mesmo usuário não pode ter duas categorias com o mesmo nome
- Diferentes usuários podem ter categorias com nomes iguais

### Como executar a migration em banco de teste

1. Certifique-se de ter configurado o `.env` com as credenciais do banco de teste
2. Execute o script:

```bash
python h_database/b_migrations/a_categorias_multiusuario.py migrate
```

### Como validar após a execução

Verifique as constraints no banco:

```sql
-- Verificar que usuario_id é NOT NULL
DESCRIBE categorias;

-- Verificar constraints
SHOW CREATE TABLE categorias;

-- Verificar que não há conflitos
SELECT * FROM categorias WHERE usuario_id IS NULL;
SELECT usuario_id, nome, COUNT(*) FROM categorias GROUP BY usuario_id, nome HAVING COUNT(*) > 1;
```

### Como fazer rollback

Se precisar desfazer a migration:

```bash
python h_database/b_migrations/a_categorias_multiusuario.py rollback
```

---

## 002 - Integridade das Tabelas e Índices

### Por que esta migration?

O modelo anterior tinha os seguintes problemas:
1. `transacoes`: Sem Foreign Key para `usuarios(id)`, sem índice em `usuario_id`
2. `metas`: `usuario_id` aceitava NULL, sem Foreign Key, sem índice
3. `investimentos`: `usuario_id` aceitava NULL, sem Foreign Key, sem índice
4. `configuracoes_usuario`: Sem Foreign Key para `usuarios(id)`

### O que esta migration faz?

1. Verifica conflitos (registros sem usuário ou com usuários inexistentes)
2. Adiciona Foreign Keys em todas as tabelas para `usuarios(id)`
3. Altera `usuario_id` para NOT NULL em `metas` e `investimentos`
4. Adiciona índices em `usuario_id` para melhorar performance das consultas
5. Adiciona índices em campos usados para ordenação (`data_transacao` em transacoes, `data_aplicacao` em investimentos)

### Como executar a migration em banco de teste

1. Certifique-se de ter executado a migration 001 primeiro
2. Execute o script:

```bash
python h_database/b_migrations/b_integridade_tabelas.py migrate
```

### Como validar após a execução

Verifique todas as tabelas:

```sql
-- Verificar todas as tabelas
DESCRIBE transacoes;
DESCRIBE metas;
DESCRIBE investimentos;
DESCRIBE configuracoes_usuario;

-- Verificar constraints em todas as tabelas
SHOW CREATE TABLE transacoes;
SHOW CREATE TABLE metas;
SHOW CREATE TABLE investimentos;
SHOW CREATE TABLE configuracoes_usuario;

-- Verificar índices
SHOW INDEX FROM transacoes;
SHOW INDEX FROM metas;
SHOW INDEX FROM investimentos;
```

### Como fazer rollback

Se precisar desfazer a migration:

```bash
python h_database/b_migrations/b_integridade_tabelas.py rollback
```
