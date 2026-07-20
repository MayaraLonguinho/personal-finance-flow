# PRD 13: Agent Financeiro

## Objetivo

Assistente conversacional que responde perguntas sobre os dados do usuário.

## Sequência do Assistente Financeiro

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant B as Backend Flask
    participant O as OpenAI API
    participant L as Fallback Local
    participant M as MySQL
    
    U->>F: Envia pergunta (≤ 500 chars)
    F->>B: POST /api/agent/pergunta
    B->>B: Verificar autenticação
    B->>B: Normalizar texto
    
    alt OpenAI disponível
        B->>O: Enviar pergunta + ferramentas
        O->>O: Analisar intenção
        O->>B: Solicitar chamada de ferramenta
        
        alt Ferramenta de saldo
            B->>M: SELECT SUM(entradas - saidas - investimentos)
            M-->>B: Resultado
            B-->>O: Dados do saldo
        end
        
        alt Ferramenta de categorias
            B->>M: SELECT categorias
            M-->>B: Categorias do usuário
            B-->>O: Dados das categorias
        end
        
        alt Ferramenta de metas
            B->>M: SELECT meta ativa
            M-->>B: Meta atual
            B-->>O: Dados da meta
        end
        
        O-->>B: Resposta formatada
        B-->>F: JSON com resposta
        F-->>U: Exibir resposta no chat
    else OpenAI indisponível
        B->>L: Normalizar texto
        L->>L: Detectar intenção
        L->>L: Consultar módulos de domínio
        
        alt Intenção: saldo
            L->>M: SELECT resumo financeiro
            M-->>L: Dados
        end
        
        alt Intenção: categorias
            L->>M: SELECT gastos por categoria
            M-->>L: Dados
        end
        
        L-->>B: Resposta determinística
        B-->>F: JSON com resposta
        F-->>U: Exibir resposta no chat
    end
```

**Explicação:** O diagrama mostra o fluxo de interação do assistente financeiro. O sistema tenta primeiro usar a OpenAI API com function calling; se disponível, a IA analisa a intenção e solicita chamadas de ferramentas específicas para consultar o banco MySQL. Se a OpenAI falhar, o sistema usa um fallback local que normaliza o texto, detecta a intenção e consulta os módulos de domínio diretamente.

## Funcionalidades

### Sistema Híbrido

1. **Primeiro tenta OpenAI**:
   - Usa GPT-4o-mini com function calling
   - Ferramentas disponíveis: consultar saldo, entradas, saídas, categorias, meta, transações recentes, etc.
   - Prompt instrui a usar apenas ferramentas para obter dados, não inventar

2. **Fallback local**:
   - Se OpenAI falhar (sem chave, erro de API, etc.), usa regras locais
   - Normaliza texto, detecta intenção, consulta módulos de domínio, retorna resposta determinística
   - Não usa nenhum LLM

### Interface

- Chat similar a apps de mensagem
- Pergunta limitada a 500 caracteres
- Histórico durante a sessão

### Segurança

- Apenas leitura (nenhuma ferramenta de escrita)
- Apenas dados do usuário logado
- Não fornece aconselhamento financeiro personalizado

## Critérios de Aceitação

- [ ] Chat funcional
- [ ] Respostas usam dados reais
- [ ] Fallback funciona sem OpenAI
- [ ] Nenhum dado de outro usuário é exposto
