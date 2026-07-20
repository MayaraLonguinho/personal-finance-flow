# PRD 15: Brain (Vault Técnico)

## Objetivo

Criar e manter um vault técnico com documentação detalhada do projeto.

## Sequência Técnica do Assistente Financeiro com Ferramentas e Banco

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Flask Backend
    participant A as j_ai_financial_agent.py
    participant O as OpenAI API
    participant D as Módulos Domínio
    participant M as MySQL
    
    U->>F: POST /api/agent/pergunta
    F->>A: responder_pergunta_openai(pergunta)
    
    A->>A: Verificar OPENAI_API_KEY
    alt API Key disponível
        A->>O: Chat completion com tools
        O->>O: Analisar intenção
        O-->>A: Solicitar tool call
        
        loop Para cada ferramenta necessária
            alt consultar_saldo
                A->>D: calcular_resumo_financeiro(usuario_id)
                D->>M: SELECT SUM(entradas - saidas - investimentos)
                M-->>D: Resultado
                D-->>A: Dados do saldo
                A-->>O: Resultado da ferramenta
            end
            
            alt consultar_entradas
                A->>D: calcular_resumo_financeiro(usuario_id)
                D->>M: SELECT SUM(entradas)
                M-->>D: Resultado
                D-->>A: Total de entradas
                A-->>O: Resultado da ferramenta
            end
            
            alt consultar_categorias
                A->>D: buscar_todas_categorias(usuario_id)
                D->>M: SELECT categorias
                M-->>D: Categorias do usuário
                D-->>A: Lista de categorias
                A-->>O: Resultado da ferramenta
            end
            
            alt consultar_meta_ativa
                A->>D: buscar_meta_ativa(usuario_id)
                D->>M: SELECT meta WHERE status = 'ativa'
                M-->>D: Meta ativa
                D-->>A: Dados da meta
                A-->>O: Resultado da ferramenta
            end
        end
        
        O-->>A: Resposta formatada
        A-->>F: JSON com resposta
    else API Key indisponível
        A->>F: Erro ou fallback
        F->>F: Chamar i_financial_agent.py (fallback local)
        F-->>U: Resposta determinística
    end
    
    F-->>U: JSON com resposta
```

**Explicação:** O diagrama mostra a sequência técnica do assistente financeiro quando usando OpenAI. O backend chama o módulo j_ai_financial_agent.py, que interage com a OpenAI API usando function calling. A IA solicita chamadas de ferramentas específicas, que consultam os módulos de domínio, que por sua vez executam queries SELECT no MySQL. Os resultados são retornados à OpenAI, que formata a resposta final.

## Estrutura do Brain

```
brain/
├── 00-visao-geral.md
├── 01-requisitos.md
├── 02-arquitetura.md
├── 03-modelo-de-dados.md
├── 04-pipeline-etl.md
├── 05-decisoes-tecnicas.md
├── 06-erros-e-aprendizados.md
└── 07-prompts.md
```

## Conteúdo dos Arquivos

- **00-visao-geral**: Visão do produto, capacidades, stack, estrutura funcional
- **01-requisitos**: Requisitos funcionais e não funcionais, atores, restrições
- **02-arquitetura**: Camadas, módulos, fluxos, diagramas
- **03-modelo-de-dados**: Tabelas, colunas, relacionamentos
- **04-pipeline-etl**: Etapas, validações, deduplicação
- **05-decisoes-tecnicas**: Racional das escolhas de tecnologia
- **06-erros-e-aprendizados**: Problemas conhecidos, limitações
- **07-prompts**: Prompts usados na aplicação (ex: do agent)

## Critérios de Aceitação

- [ ] Todos os arquivos do brain existem
- [ ] Conteúdo é derivado do código existente
- [ ] Documentação está atualizada
