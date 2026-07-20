# PRD 02: Banco de Dados

## Objetivo

Definir e implementar o schema do banco de dados MySQL.

## Modelo de Dados (ER Diagram)

```mermaid
erDiagram
    usuarios ||--o{ transacoes : "possui"
    usuarios ||--o{ categorias : "possui"
    usuarios ||--o{ metas : "define"
    usuarios ||--o{ investimentos : "gerencia"
    usuarios ||--|| configuracoes_usuario : "configura"
    
    transacoes ||--o| investimentos : "pode gerar"
    
    usuarios {
        int id PK
        string nome
        string email UK
        string telefone
        string senha_hash
        timestamp criado_em
    }
    
    transacoes {
        int id PK
        int usuario_id FK
        date data_transacao
        string descricao
        string categoria
        string tipo
        decimal valor
        string conta
        string instituicao
        string status
        timestamp criado_em
    }
    
    categorias {
        int id PK
        int usuario_id FK
        string nome
        text palavras_chave
        string cor
        timestamp criado_em
        timestamp atualizado_em
    }
    
    metas {
        int id PK
        int usuario_id FK
        string titulo
        decimal valor_meta
        decimal valor_atual
        date data_limite
        string status
        timestamp criado_em
        timestamp atualizado_em
    }
    
    investimentos {
        int id PK
        int usuario_id FK
        int transacao_id FK
        string nome
        string tipo
        string instituicao
        decimal valor_aplicado
        decimal valor_atual
        decimal rentabilidade_percentual
        date data_aplicacao
        date data_vencimento
        string status
        timestamp criado_em
        timestamp atualizado_em
    }
    
    configuracoes_usuario {
        int id PK
        int usuario_id FK UK
        string nome
        string tema
        string moeda
        string formato_data
        int qtd_transacoes_recentes
        boolean confirmar_exclusao
        text cards_visiveis
        timestamp criado_em
        timestamp atualizado_em
    }
```

**Explicação:** O diagrama ER mostra o modelo de dados do sistema, com a tabela `usuarios` como entidade central. Todas as tabelas de dados do usuário (exceto `usuarios`) possuem `usuario_id` como chave estrangeira para garantir isolamento de dados. A tabela `transacoes` pode gerar `investimentos` quando uma transação do tipo investimento é confirmada. A tabela `configuracoes_usuario` tem relacionamento um-para-um com `usuarios`.

## Isolamento de Dados por Usuário

```mermaid
flowchart TD
    A[Requisição HTTP] --> B[@app.before_request]
    B --> C{usuario_id na sessão?}
    C -->|Sim| D[definir_usuario_id ContextVar]
    C -->|Não| E[limpar_usuario_id ContextVar]
    
    D --> F[Módulo de domínio acessa ContextVar]
    F --> G[obter_usuario_id retorna ID]
    
    G --> H[Query SQL construída]
    H --> I[WHERE usuario_id = :usuario_id]
    
    I --> J[Executar query com parâmetro]
    J --> K[MySQL retorna apenas dados do usuário]
    
    K --> L[@app.teardown_request]
    L --> M[limpar_usuario_id ContextVar]
    
    M --> N[Resposta enviada ao usuário]
    
    style D fill:#ccffcc
    style G fill:#ccffcc
    style I fill:#e1f5ff
    style K fill:#ccffcc
    style M fill:#ffffcc
```

**Explicação:** O diagrama mostra o fluxo de isolamento de dados por usuário. O ContextVar é definido no before_request com o usuario_id da sessão. Módulos de domínio acessam o ContextVar para obter o ID atual. Todas as queries SQL incluem cláusula WHERE usuario_id = :usuario_id com parâmetro, garantindo que cada usuário acesse apenas seus próprios dados. O ContextVar é limpo no teardown_request.

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
