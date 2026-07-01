---
title: Erros e aprendizados
tags:
  - personal-finance-flow
  - dívida-técnica
  - aprendizados
---

# Erros e aprendizados

> [!warning]
> Esta nota registra somente inconsistências verificáveis nos arquivos. Ela não afirma que um erro ocorreu em produção.

## 1. README desatualizado

### Evidência

- `README.md` informa `http://localhost:5000`.
- `app.py` inicia em `127.0.0.1:5001`.
- O README lista upload, banco, ETL, métricas, gráficos e relatórios como próximos passos, embora existam implementações desses recursos.

### Aprendizado

A documentação de execução e o roadmap precisam acompanhar o ponto de entrada real; caso contrário, recursos existentes parecem ausentes e a porta informada falha.

## 2. Inexistência de ponto de entrada CLI

### Evidência

Não existe ponto de entrada CLI funcional. O pipeline web está alinhado com os contratos atuais.

### Aprendizado

Para uso programático, utilize os módulos diretamente com o contexto e os argumentos corretos.

## 3. Unicidade de categorias por usuário e nome

### Evidência

O schema atual declara `UNIQUE (usuario_id, nome)` na tabela `categorias`, o que permite que diferentes usuários tenham categorias com o mesmo nome.

### Aprendizado

A unicidade composta por usuário e nome está alinhada com o modelo multiusuário atual.

## 4. Relações sem chaves estrangeiras

### Evidência

Todas as tabelas usam `usuario_id`, mas `database/schema.sql` não possui nenhuma `FOREIGN KEY`. No schema atual, `usuario_id` é NOT NULL em todas as tabelas financeiras.

### Aprendizado

Filtrar por usuário na aplicação protege os fluxos atuais, mas não substitui integridade referencial no banco.

## 5. Métodos internos permitem consulta sem proprietário

### Evidência

`limpar_transacoes_mysql` agora exige `usuario_id` e remove apenas dados do usuário especificado. As rotas atuais fornecem o identificador.

### Aprendizado

O isolamento é mais robusto quando o identificador é obrigatório também na camada interna.

## 6. Exclusão de categoria dividida em conexões

### Evidência

`excluir_categoria` atualiza transações para `outros` em uma conexão sem `commit()` explícito e exclui a categoria em outra conexão, onde realiza commit.

### Aprendizado

Operações logicamente atômicas devem compartilhar uma transação. A implementação atual não garante atomicidade entre a recategorização e a exclusão.

## 7. Upload mantém nome original e arquivo

### Evidência

A rota concatena `uploads` com `arquivo.filename`, salva o conteúdo e não remove o arquivo após processá-lo. A validação de extensão usa `endswith('.csv')`.

### Aprendizado

O ciclo de vida, a normalização do nome e a política de retenção dos uploads precisam ser decisões explícitas. O projeto atual apenas mantém `uploads/.gitkeep` no versionamento.

## 8. Exceções silencenciadas em consultas

### Evidência

Funções de `src/auth.py` e `src/categorias.py` capturam `Exception` e retornam `None`, lista vazia ou zeros. `src/utils.py` também ignora erros ao obter preferências.

### Aprendizado

Valores vazios podem significar tanto ausência legítima quanto falha de banco. Sem registro estruturado, a distinção se perde e o diagnóstico fica mais difícil.

## 9. SECRET_KEY obrigatória

### Evidência

`app.py` falha ao iniciar se `SECRET_KEY` não estiver configurada no ambiente. Não existe fallback conhecido.

### Aprendizado

A configuração obrigatória deve estar documentada em `.env.example` e definida externamente antes da execução.


## 10. Comentário da API OpenAI não corresponde à chamada

### Evidência

O cabeçalho de `ai_financial_agent.py` menciona “Responses API”, porém o código chama `client.chat.completions.create()`.

### Aprendizado

Comentários de integração devem nomear a API efetivamente utilizada, especialmente quando o SDK oferece superfícies diferentes.

## 11. Migrações embutidas na inicialização

### Evidência

Importar `app.py` executa `garantir_colunas_usuario()`, que pode rodar `ALTER TABLE`. Consultar configurações executa antes um `CREATE TABLE IF NOT EXISTS`.

### Aprendizado

O comportamento facilita compatibilidade com bancos antigos, mas acopla inicialização e leitura a permissões de alteração de schema.

## 12. Testes existentes

### Evidência

A pasta `tests/` contém testes automatizados para MCP, categorias, categorização automática e upload API. Não existem testes para isolamento de usuário via SQL (a implementação atual usa ContextVar).

### Aprendizado

Testes existentes cobrem partes importantes do sistema, mas há lacunas em cobertura de integração e interface.

## 13. Documentação técnica organizada

### Evidência

`docs/arquitetura.md` agora é uma página de navegação. `docs/vibe-coding.md` contém a metodologia de desenvolvimento. O vault `brain/` contém documentação técnica detalhada.

### Aprendizado

Documentação organizada em níveis diferentes (índice, visão de produto, arquitetura técnica) facilita navegação e manutenção.

## 14. Conceitos de saldo e período diferem entre dashboard e relatório

### Evidência

`src/metrics.py` calcula `saldo_final = entradas - saídas - investimentos` usando somente transações confirmadas. `src/relatorios.py` calcula `saldo = entradas - saídas`, não restringe status e retorna separadamente `total_investido`. Além disso, o intervalo do relatório filtra as transações, mas `obter_resumo_investimentos()` recebe apenas `usuario_id` e representa a carteira atual completa.

### Aprendizado

Dashboard e relatório possuem semânticas distintas no código atual. A interface e a documentação precisam nomear essas diferenças para que valores corretos segundo fórmulas diferentes não pareçam inconsistentes por acaso.

## Ligações

- [[01-requisitos]]
- [[03-modelo-de-dados]]
- [[04-pipeline-etl]]
- [[05-decisoes-tecnicas]]
