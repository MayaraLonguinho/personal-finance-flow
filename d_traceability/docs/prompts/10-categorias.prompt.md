# Prompt 10: Categorias

Implemente gestão de categorias:

1. **Categorias padrão**:
   - Criadas automaticamente para novo usuário: Transporte, Alimentação, Lazer, Saúde, Casa, Salário, Investimentos, Outros
   - "Outros" não pode ser excluída

2. **CRUD**:
   - Campos: nome, cor, palavras-chave (JSON)
   - Ao excluir categoria com transações, move elas para "Outros"

3. **Categorização automática**:
   - Usa palavras-chave para categorizar transações no upload e criação manual
   - Usuário pode editar palavras-chave nas categorias
