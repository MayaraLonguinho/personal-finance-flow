# PRD 01: Estrutura Inicial

## Objetivo

Criar a estrutura base do projeto, organização de pastas e arquivos fundamentais.

## Arquitetura de Componentes

```mermaid
flowchart TD
    subgraph "Frontend Layer"
        A[a_frontend_webclient/]
        A1[a_templates/]
        A2[a_static/]
        A1 --> A
        A2 --> A
    end
    
    subgraph "Backend Layer"
        B[b_backend/]
        B1[a_app.py]
        B2[b_src/]
        B2 --> B
        B1 --> B
    end
    
    subgraph "Domain Modules"
        C[b_src/]
        C1[a_auth.py]
        C2[b_usuario_contexto.py]
        C3[c_transacoes.py]
        C4[d_categorias.py]
        C5[e_metrics.py]
        C6[f_relatorios.py]
        C7[g_metas.py]
        C8[h_investimentos.py]
        C9[i_financial_agent.py]
        C10[j_ai_financial_agent.py]
        C11[k_configuracoes.py]
        C12[l_utils.py]
        
        C1 --> C
        C2 --> C
        C3 --> C
        C4 --> C
        C5 --> C
        C6 --> C
        C7 --> C
        C8 --> C
        C9 --> C
        C10 --> C
        C11 --> C
        C12 --> C
    end
    
    subgraph "ETL Pipeline"
        D[c_generate_rpa/]
        D1[a_extract.py]
        D2[b_transform.py]
        D3[c_categorization.py]
        D4[d_load.py]
        
        D1 --> D
        D2 --> D
        D3 --> D
        D4 --> D
    end
    
    subgraph "Database"
        E[h_database/]
        E1[a_schema.sql]
        E2[b_migrations/]
        
        E1 --> E
        E2 --> E
    end
    
    subgraph "Traceability"
        F[d_traceability/]
        F1[a_brain/]
        F2[b_docs/]
        F3[c_mcp/]
        F4[d_skills/]
        
        F1 --> F
        F2 --> F
        F3 --> F
        F4 --> F
    end
    
    subgraph "Tests"
        G[e_verify/]
        G1[a_unit/]
        G2[b_integration/]
        G3[c_security/]
        
        G1 --> G
        G2 --> G
        G3 --> G
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    
    style A fill:#fff4e1
    style B fill:#ffe1f5
    style C fill:#e1f5ff
    style D fill:#e1ffe1
    style E fill:#f0f0f0
    style F fill:#f5f0ff
    style G fill:#ffffe1
```

**Explicação:** O diagrama mostra a arquitetura de componentes do sistema, organizada em camadas: Frontend (templates e estáticos), Backend (app Flask e módulos de domínio), Pipeline ETL (extract, transform, categorization, load), Database (schema e migrations), Traceability (brain, docs, MCP, skills) e Tests (unit, integration, security). O fluxo de dados vai do Frontend através do Backend para os módulos de domínio e ETL, que interagem com o Database.

## Fluxo de Inicialização da Aplicação

```mermaid
flowchart TD
    A[Iniciar aplicação] --> B[Carregar variáveis de ambiente .env]
    B --> C[Verificar SECRET_KEY]
    C -->|SECRET_KEY ausente| D[Erro: variável obrigatória]
    C -->|SECRET_KEY presente| E[Configurar Flask app]
    
    E --> F[Configurar segurança de sessão]
    F --> G[Inicializar CSRFProtect]
    G --> H[Inicializar Rate Limiter]
    
    H --> I[Garantir colunas usuario_id]
    I --> J[Conectar ao MySQL]
    J --> K[Verificar/alterar tabelas]
    
    K --> L[Registrar before_request]
    L --> M[Registrar teardown_request]
    M --> N[Definir rotas Flask]
    
    N --> O[Iniciar servidor Flask]
    O --> P[Aplicação pronta]
    
    style D fill:#ffcccc
    style P fill:#ccffcc
```

**Explicação:** O diagrama mostra o fluxo de inicialização da aplicação Flask. O sistema carrega variáveis de ambiente, verifica a SECRET_KEY obrigatória, configura o app Flask, inicializa proteções (CSRF, rate limiter), garante colunas de isolamento no banco, conecta ao MySQL, registra hooks de request (before_request, teardown_request), define as rotas e inicia o servidor.

## Estrutura de Pastas

```
personal-finance-flow/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
├── src/                  # Módulos de domínio
├── templates/            # Templates Jinja2
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── h_database/           # Schema e migrações
├── data/                 # Dados de exemplo
├── docs/                 # Documentação
└── brain/                # Vault técnico
```

## Critérios de Aceitação

- [ ] Estrutura de pastas criada
- [ ] `requirements.txt` com dependências básicas
- [ ] `.env.example` com placeholders
- [ ] `README.md` básico com instruções de setup
