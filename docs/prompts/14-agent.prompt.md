# Prompt 14: Agent

Implemente o assistente financeiro híbrido:

1. **Sistema híbrido**:
   - Primeiro tenta OpenAI (GPT-4o-mini) com function calling
   - Se falhar (sem chave, erro API), usa fallback local sem LLM

2. **OpenAI**:
   - Ferramentas (tools) para consultar saldo, entradas, saídas, categorias, meta, investimentos, transações recentes, etc.
   - Prompt sistema: responder em pt-BR, usar apenas tools para dados, não inventar, não dar aconselhamento financeiro personalizado
   - Function calling: até 4 iterações

3. **Fallback local**:
   - Normaliza texto, remove acentos
   - Detecta intenção por palavras-chave
   - Consulta módulos de domínio diretamente
   - Retorna resposta determinística

4. **Interface de chat**:
   - Página dedicada
   - Pergunta até 500 caracteres
   - Histórico durante a sessão
