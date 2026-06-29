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

## 2. Pipeline standalone incompatível com o transformador e a carga

### Evidência

`src/main.py` atribui `df_tratado = tratar_transacoes(df_bruto)`, mas a função retorna `(df, contador)`. Em seguida, tenta chamar `.to_csv()` nessa tupla. O mesmo arquivo chama `carregar_transacoes_mysql(df_tratado)` sem o `usuario_id` exigido pela assinatura atual.

### Aprendizado

Mudanças de contrato entre módulos precisam atualizar todos os pontos de entrada. O pipeline web está alinhado com o contrato atual; o standalone não está.

## 3. Unicidade de categorias conflita com o escopo por usuário

### Evidência

O schema declara `nome VARCHAR(100) NOT NULL UNIQUE`, enquanto todas as consultas de categoria filtram por `usuario_id` e cada usuário tenta inicializar as mesmas categorias padrão.

### Aprendizado

Em um modelo multiusuário, a unicidade esperada pelo código seria por proprietário e nome. O schema atual pode impedir que dois usuários tenham uma categoria homônima.

## 4. Relações sem chaves estrangeiras

### Evidência

Todas as tabelas usam `usuario_id`, mas `database/schema.sql` não possui nenhuma `FOREIGN KEY`. Além disso, metas, categorias e investimentos aceitam `NULL` nessa coluna.

### Aprendizado

Filtrar por usuário na aplicação protege os fluxos atuais, mas não substitui integridade referencial no banco nem impede registros órfãos criados por outros caminhos.

## 5. Métodos internos permitem consulta sem proprietário

### Evidência

`buscar_todas_transacoes`, `listar_investimentos`, `buscar_investimento_por_id`, `obter_resumo_investimentos` e `limpar_transacoes_mysql` possuem comportamentos sem `usuario_id`. No caso da limpeza, a ausência do usuário remove todas as transações. As rotas atuais fornecem o identificador.

### Aprendizado

O isolamento é mais robusto quando o identificador é obrigatório também na camada interna, e não somente na borda HTTP.

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

## 9. Segredo de sessão com fallback conhecido

### Evidência

`app.py` usa `os.getenv('SECRET_KEY', 'chave-secreta-desenvolvimento-pff-2026')`. `SECRET_KEY` não está listada em `.env.example`.

### Aprendizado

O fallback é útil em desenvolvimento, mas a configuração necessária para outro ambiente precisa estar documentada e definida externamente.

## 10. Duas fábricas de conexão

### Evidência

`src/load.py::obter_engine` e `src/database.py::get_connection` repetem a montagem da URL e a criação de engine. O código de domínio usa predominantemente `obter_engine`.

### Aprendizado

Uma única composição de infraestrutura reduz divergência de configuração e facilita testes.

## 11. Comentário da API OpenAI não corresponde à chamada

### Evidência

O cabeçalho de `ai_financial_agent.py` menciona “Responses API”, porém o código chama `client.chat.completions.create()`.

### Aprendizado

Comentários de integração devem nomear a API efetivamente utilizada, especialmente quando o SDK oferece superfícies diferentes.

## 12. Migrações embutidas na inicialização

### Evidência

Importar `app.py` executa `garantir_colunas_usuario()`, que pode rodar `ALTER TABLE`. Consultar configurações executa antes um `CREATE TABLE IF NOT EXISTS`.

### Aprendizado

O comportamento facilita compatibilidade com bancos antigos, mas acopla inicialização e leitura a permissões de alteração de schema.

## 13. Ausência de testes versionados

### Evidência

A árvore atual não contém diretório ou arquivos de teste, e `requirements.txt` não inclui framework de testes.

### Aprendizado

Contratos críticos — isolamento por usuário, ETL, deduplicação, métricas e validações — estão documentados no código, mas não protegidos por uma suíte presente no repositório.

## 14. Documentação técnica anterior vazia

### Evidência

Antes deste vault, os arquivos de `brain/` continham apenas títulos. `docs/arquitetura.md` e `docs/vibe-coding.md` também contêm somente um título.

### Aprendizado

Um vault útil precisa indicar fontes, estado atual e divergências, além de conectar conceitos por links internos.

## 15. Conceitos de saldo e período diferem entre dashboard e relatório

### Evidência

`src/metrics.py` calcula `saldo_final = entradas - saídas - investimentos` usando somente transações confirmadas. `src/relatorios.py` calcula `saldo = entradas - saídas`, não restringe status e retorna separadamente `total_investido`. Além disso, o intervalo do relatório filtra as transações, mas `obter_resumo_investimentos()` recebe apenas `usuario_id` e representa a carteira atual completa.

### Aprendizado

Dashboard e relatório possuem semânticas distintas no código atual. A interface e a documentação precisam nomear essas diferenças para que valores corretos segundo fórmulas diferentes não pareçam inconsistentes por acaso.

## Ligações

- [[01-requisitos]]
- [[03-modelo-de-dados]]
- [[04-pipeline-etl]]
- [[05-decisoes-tecnicas]]
