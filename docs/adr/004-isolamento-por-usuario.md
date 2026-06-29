# ADR 004: Isolamento por Usuário

## Status

✅ Aceito

## Contexto

Aplicação multi-usuário: cada usuário deve ver APENAS seus próprios dados, nunca de outros.

## Decisão

Implementar **isolamento por usuário** em múltiplas camadas:

1. **Sessão Flask**: armazena `usuario_id`
2. **ContextVar**: propaga `usuario_id` pelos módulos sem passar explicitamente em tudo
3. **Todas as consultas SQL**: incluem `WHERE usuario_id = :usuario_id`
4. **Validação de propriedade**: operações de update/delete verificam `usuario_id` + `id`

## Justificativa

- Segurança: nenhum usuário acessa dados alheios
- Simplicidade: não usa schema separado por usuário ou multi-tenant complexo
- Flexível: funciona bem com MySQL
- Já havia sido implementado

## Consequências

### Positivas
- Isolamento forte
- Simples de entender e manter
- Não depende de features específicas do banco

### Negativas
- Depende do desenvolvedor lembrar de SEMPRE incluir `WHERE usuario_id` (risco de bugs se esquecer)
- Sem constraint de FK no banco como segunda linha de defesa
- Overhead de propagação do `usuario_id`

## Alternativas Consideradas
- Schemas separados por usuário (complexo para gerenciar)
- Row Level Security do PostgreSQL (requeria mudar de banco)
- Multi-tenant com coluna (o que já está implementado)
