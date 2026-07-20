# PRD 04: Proteção de Rotas

## Objetivo

Garantir que apenas usuários autenticados acessem rotas internas e que cada usuário só veja seus próprios dados.

## Fluxo de Proteção de Rotas

```mermaid
flowchart TD
    A[Requisição HTTP] --> B[@app.before_request]
    B --> C{usuario_id na sessão?}
    C -->|Não| D[limpar_usuario_id ContextVar]
    C -->|Sim| E[definir_usuario_id ContextVar]
    
    E --> F[@login_obrigatorio decorator]
    D --> F
    
    F --> G{Rota é API?}
    G -->|Sim /api/*| H{usuario_id na sessão?}
    G -->|Não página| I{usuario_id na sessão?}
    
    H -->|Não| J[Retornar HTTP 401]
    H -->|Sim| K[Permitir acesso]
    
    I -->|Não| L[Redirecionar para /login]
    I -->|Sim| M[Permitir acesso]
    
    K --> N[Executar handler da rota]
    M --> N
    
    N --> O[Consultas SQL com WHERE usuario_id]
    O --> P[@app.teardown_request]
    P --> Q[limpar_usuario_id ContextVar]
    Q --> R[Resposta HTTP]
    
    J --> R
    L --> R
    
    style J fill:#ffcccc
    style L fill:#ffcccc
    style K fill:#ccffcc
    style M fill:#ccffcc
    style N fill:#e1f5ff
```

**Explicação:** O diagrama mostra o fluxo de proteção de rotas, incluindo o uso de before_request para definir o ContextVar, o decorator login_obrigatorio para verificar autenticação, redirecionamento para páginas não autenticadas, retorno 401 para APIs não autenticadas, e teardown_request para limpar o ContextVar. Todas as consultas SQL incluem filtro por usuario_id.

## Funcionalidades

### Decorator `login_obrigatorio`

- Verifica se `usuario_id` existe na sessão
- Se não existir:
  - Redireciona para `/login` em rotas de página
  - Retorna HTTP 401 em APIs
- Se existir: permite acesso

### ContextVar para Usuário

- `before_request`: copia `session["usuario_id"]` para `ContextVar`
- `teardown_request`: limpa o `ContextVar`
- Módulos de domínio podem acessar o usuário atual sem receber parâmetro

### Isolamento em Consultas

Todas as consultas SQL devem incluir `WHERE usuario_id = :usuario_id`

## Critérios de Aceitação

- [ ] Rotas protegidas redirecionam para login sem sessão
- [ ] APIs retornam 401 sem sessão
- [ ] Todas as consultas filtram por `usuario_id`
- [ ] Nenhum usuário acessa dados de outro usuário
