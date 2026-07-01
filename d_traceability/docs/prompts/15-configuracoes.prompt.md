# Prompt 15: Configurações

Implemente configurações do usuário:

1. **Preferências**:
   - Nome de exibição
   - Tema (azul, rosa, verde, vermelho, escuro)
   - Moeda (BRL, USD, EUR) - apenas formatação, não conversão
   - Formato de data (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)
   - Qtd transações recentes (3-20)
   - Confirmação de exclusão (on/off)
   - Cards visíveis no dashboard (checklist)

2. **Funcionalidades**:
   - Botão "Restaurar padrão"
   - Atualização parcial (altera só um campo sem enviar todos)
   - Preferências injetadas no frontend (window.PFF_CONFIG)
   - Aplicadas em todas as páginas

3. **Armazenamento**:
   - Tabela configuracoes_usuario com usuario_id
   - Upsert: cria se não existe, atualiza se existe
