# Prompt 08: Transações

Implemente CRUD completo de transações:

1. **Listagem**:
   - Mostra transações do usuário logado
   - Filtros: descrição, categoria, tipo (entrada/saída/investimento), status
   - Ordenada por data decrescente

2. **Criação/Edição**:
   - Campos: data, descrição, tipo, valor (>0), status, categoria (opcional)
   - Sugere categoria baseada em regras se não informada
   - Valida todos os campos

3. **Exclusão**:
   - Confirmação (configurável pelo usuário)
   - Remove apenas transação do usuário logado
