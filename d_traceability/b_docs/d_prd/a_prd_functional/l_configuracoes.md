# PRD 14: Configurações

## Objetivo

Permitir usuário personalizar sua experiência no app.

## Fluxo de Configurações do Usuário

```mermaid
flowchart TD
    A[Usuário acessa /configuracoes] --> B[Verificar autenticação]
    B -->|Não autenticado| C[Redirecionar para /login]
    B -->|Autenticado| D[Carregar configuracoes_usuario]
    
    D --> E[Exibir formulário com valores atuais]
    E --> F[Usuário altera preferências]
    
    F --> G{Botão clicado?}
    G -->|Salvar| H[Validar alterações]
    G -->|Restaurar padrão| I[Resetar para valores padrão]
    
    H --> J{Validações}
    J -->|qtd_transacoes_recentes fora de range| K[Erro: 3-20]
    J -->|Válido| L[Atualizar no MySQL]
    
    I --> M[Atualizar no MySQL]
    L --> N[Aplicar em todas as páginas]
    M --> N
    
    N --> O[Tema aplicado via CSS]
    N --> P[Moeda formatada em todas views]
    N --> Q[Data formatada em todas views]
    N --> R[Dashboard atualizado]
    
    style C fill:#ffcccc
    style K fill:#ffcccc
    style N fill:#ccffcc
```

**Explicação:** O diagrama mostra o fluxo de configurações do usuário, desde o acesso à página até a aplicação das preferências. O usuário pode salvar alterações específicas ou restaurar os padrões. As configurações são aplicadas globalmente: tema via CSS, moeda e data formatadas em todas as views, e dashboard atualizado com as novas preferências.

## Funcionalidades

### Preferências Disponíveis

| Preferência | Opções | Padrão |
|---|---|---|
| Nome de exibição | Texto | (nome do cadastro) |
| Tema | Azul, Rosa, Verde, Vermelho, Escuro | Azul |
| Moeda | BRL, USD, EUR | BRL |
| Formato de data | DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD | DD/MM/YYYY |
| Qtd transações recentes | 3-20 | 5 |
| Confirmação de exclusão | On/Off | On |
| Cards visíveis no dashboard | Checklist | (todos) |

### Funcionalidades Adicionais

- Botão "Restaurar padrão" para resetar todas preferências
- Atualização parcial: pode alterar apenas um campo sem enviar todos
- Preferências aplicadas em todas as páginas

## Critérios de Aceitação

- [ ] Todas preferências são salvas e persistem
- [ ] Tema é aplicado em todas as páginas
- [ ] Moeda e data são formatados corretamente
- [ ] Restaurar padrão funciona
