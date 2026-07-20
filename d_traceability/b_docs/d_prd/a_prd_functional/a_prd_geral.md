# PRD Geral

## Contextualização

Este documento agrupa as diretrizes gerais para todos os PRDs específicos do Personal Finance Flow.

## Arquitetura Funcional Geral

O sistema segue uma arquitetura funcional baseada em módulos de domínio, com fluxo de dados centralizado através do backend Flask.

```mermaid
flowchart TD
    A[Usuário] --> B[Frontend<br/>HTML/CSS/JS]
    B --> C[Flask Backend<br/>Rotas e APIs]
    C --> D[Módulos de Domínio<br/>src/]
    
    D --> E[Autenticação]
    D --> F[Transações]
    D --> G[Categorias]
    D --> H[Metas]
    D --> I[Investimentos]
    D --> J[Métricas/Dashboard]
    D --> K[Agent Financeiro]
    D --> L[Configurações]
    
    E --> M[MySQL<br/>usuarios]
    F --> N[MySQL<br/>transacoes]
    G --> O[MySQL<br/>categorias]
    H --> P[MySQL<br/>metas]
    I --> Q[MySQL<br/>investimentos]
    L --> R[MySQL<br/>configuracoes_usuario]
    
    C --> S[Pipeline ETL<br/>extract/transform/load]
    S --> N
    
    K --> T{OpenAI API}
    T -->|Sucesso| K
    T -->|Falha| U[Fallback Local]
    U --> K
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
    style D fill:#e1ffe1
    style M fill:#f0f0f0
    style N fill:#f0f0f0
    style O fill:#f0f0f0
    style P fill:#f0f0f0
    style Q fill:#f0f0f0
    style R fill:#f0f0f0
```

**Explicação:** O diagrama mostra o fluxo funcional geral do sistema, desde a interação do usuário através do frontend até os módulos de domínio no backend, que por sua vez interagem com o banco de dados MySQL. O pipeline ETL processa uploads CSV e o Agent Financeiro usa um sistema híbrido com OpenAI e fallback local.

## Princípios Gerais

1. **Privacidade primeiro**: Dados dos usuários nunca são enviados para servidores terceiros sem consentimento explícito
2. **Simplicidade**: Interface intuitiva, sem sobrecarga de funcionalidades
3. **Desempenho**: Resposta rápida, mesmo com muitos dados
4. **Extensibilidade**: Arquitetura modular para adicionar novas funcionalidades
5. **Segurança**: Senhas hasheadas, isolamento de dados, SQL parametrizado

## Stack Tecnológica Padronizada

- Backend: Python 3.9+, Flask 3.1.3
- Banco: MySQL via PyMySQL + SQLAlchemy 2.0.50
- Dados: Pandas 2.3.3
- Frontend: HTML, CSS, JavaScript vanilla + Chart.js
- IA (opcional): OpenAI API (GPT-4o-mini) com function calling
