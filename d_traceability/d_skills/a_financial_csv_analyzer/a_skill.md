---
name: financial-csv-analyzer
description: Analisar, validar, transformar, categorizar e importar arquivos CSV de transações financeiras usando o pipeline Pandas e MySQL já existente no Personal Finance Flow. Usar quando for necessário inspecionar um CSV financeiro, explicar incompatibilidades de colunas ou valores, preparar dados no formato aceito, executar uma importação isolada por usuário, identificar duplicatas ou interpretar os contadores retornados pelo ETL do projeto.
---

# Financial CSV Analyzer

## Objetivo

Usar o pipeline existente para processar transações financeiras sem reimplementar suas regras. Preservar os módulos atuais e escolher um dos modos:

1. **Análise sem carga**: extrair, validar e transformar o CSV; não persistir dados.
2. **Importação**: executar extração, transformação, categorização e carga no MySQL para um usuário autenticado.

Não converter moedas, recalcular valores nem alterar regras financeiras. Não editar `src/`, `app.py`, schema ou arquivos de frontend para executar esta skill.

## Fontes de verdade

Consultar diretamente, conforme necessário:

- `src/extract.py`: leitura de arquivo por caminho.
- `src/transform.py`: transformação e contrato de retorno.
- `src/categorization.py`: normalização e regras padrão.
- `src/categorias.py`: regras persistidas por usuário.
- `src/load.py`: normalização final, deduplicação e carga.
- `src/usuario_contexto.py`: contexto necessário fora de uma requisição Flask.
- `app.py`, rota `POST /api/upload`: fluxo web integrado.
- `h_database/a_schema.sql`: tipos e restrições da tabela `transacoes`.
- `data/raw/transacoes_exemplo.csv`: exemplo de entrada.
- `data/processed/transacoes_tratadas.csv`: exemplo transformado.

Não copiar essas implementações para a resposta ou para novos scripts. Invocar ou descrever os componentes existentes.

## Entradas

Receber:

- um arquivo CSV acessível por caminho; ou
- um arquivo enviado como campo multipart `arquivo` para `POST /api/upload`;
- um `usuario_id` válido para qualquer carga no banco;
- credenciais MySQL configuradas por `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME` quando houver persistência.

Para o fluxo web, exigir uma sessão autenticada. Para uso direto dos módulos, estabelecer o usuário com `contexto_usuario(usuario_id)` durante transformação e categorização e passar o mesmo `usuario_id` explicitamente à carga.

## Colunas esperadas

Esperar o cabeçalho lógico abaixo:

| Coluna | Finalidade | Observação |
|---|---|---|
| `data` | Data da transação | Convertida por Pandas e renomeada para `data_transacao` na carga |
| `descricao` | Texto da movimentação | Base da categorização automática |
| `categoria` | Categoria informada | Valor ausente vira `outros`; categoria válida existente é preservada |
| `tipo` | Natureza da movimentação | Normaliza `receita` para `entrada` e `despesa` para `saida` |
| `valor` | Montante | Convertido para número e arredondado a duas casas na carga |
| `conta` | Conta associada | Pode terminar como `NULL` quando vazia |
| `instituicao` | Instituição associada | Pode terminar como `NULL` quando vazia |
| `status` | Estado da transação | Normaliza `concluído` e `concluido` para `confirmado` |

Tratar nomes de colunas sem distinção entre maiúsculas e minúsculas, pois a transformação os converte para minúsculas. Não assumir remoção de espaços no cabeçalho.

Considerar `data`, `valor`, `tipo`, `status` e `categoria` necessárias para `tratar_transacoes`, pois são acessadas diretamente. Exigir `descricao` para categorização útil. Manter `conta` e `instituicao` como campos esperados, embora a carga consiga criar colunas ausentes.

## Validações

### Antes de processar

1. Confirmar que o arquivo existe e é legível.
2. No fluxo web, confirmar nome não vazio e extensão exatamente `.csv`.
3. Ler o cabeçalho e comparar com as colunas esperadas.
4. Reportar colunas obrigatórias ausentes antes de transformar.
5. Confirmar que existe usuário autenticado ou `usuario_id` explícito antes de carregar.
6. Confirmar configuração do MySQL e existência da tabela `transacoes` antes da persistência.

### Durante a transformação

- Tratar falha de conversão de `data` como erro do arquivo.
- Tratar falha de conversão de `valor` como erro do arquivo.
- Verificar se os valores finais de `tipo` são compatíveis com `entrada`, `saida` ou `investimento`.
- Verificar se os valores finais de `status` são compatíveis com `confirmado`, `pendente` ou `cancelado`.
- Não aceitar silenciosamente um tipo ou status incompatível com os `ENUM` do banco.
- Preservar valores financeiros; realizar somente conversão numérica e arredondamento já previstos.

### Antes da carga

- Usar o mesmo `usuario_id` para contexto, consulta de duplicatas e inserção.
- Não chamar `limpar_transacoes_mysql` como parte da análise ou importação.
- Não gravar quando o pedido for apenas analisar, validar ou pré-visualizar.

## Etapas do pipeline

### 1. Extração

Para arquivo por caminho, usar `ler_csv(caminho_arquivo)`. Para upload web, usar a rota existente, que salva o arquivo em `g_uploads/` e lê com `pandas.read_csv`.

Registrar ao menos:

- caminho ou nome lógico do arquivo;
- quantidade bruta de linhas;
- cabeçalho encontrado.

Não criar um leitor CSV alternativo.

### 2. Transformação

Usar `tratar_transacoes(df)`. Desempacotar obrigatoriamente o retorno como:

- DataFrame tratado;
- quantidade de transações categorizadas automaticamente.

A função existente:

1. remove linhas duplicadas completas;
2. normaliza nomes das colunas para minúsculas;
3. converte data e valor;
4. normaliza tipo e status pelos mapeamentos existentes;
5. preenche categoria vazia com `outros`;
6. inicializa e consulta regras de categorias do usuário;
7. aplica categorização automática;
8. remove linhas sem valor ou data;
9. retorna `(df_tratado, contador_categorizadas)`.

Não repetir essas operações manualmente antes ou depois, salvo para validar e relatar o resultado.

### 3. Carga

Somente quando houver autorização para importar, usar `carregar_transacoes_mysql(df_tratado, usuario_id)`.

A carga existente:

- renomeia `data` para `data_transacao`;
- associa o proprietário;
- normaliza datas, valores e textos;
- remove linhas inválidas em data ou valor;
- remove duplicatas internas;
- consulta registros existentes somente do usuário;
- compara todas as colunas de carga;
- insere somente linhas novas com `DataFrame.to_sql`.

Considerar uma duplicata lógica quando coincidirem:

`usuario_id`, `data_transacao`, `descricao`, `categoria`, `tipo`, `valor`, `conta`, `instituicao` e `status`.

## Categorização

Respeitar a seguinte precedência:

1. Preservar categoria preenchida e diferente de `outros`.
2. Para categoria ausente ou `outros`, normalizar a descrição para minúsculas, espaços simples e sem acentos.
3. Usar as palavras-chave das categorias persistidas para o usuário.
4. Usar as regras padrão de `obter_regras_categorizacao()` quando nenhuma regra for fornecida ao categorizador.
5. Selecionar a primeira categoria cuja palavra-chave apareça como substring da descrição.
6. Usar `outros` quando não houver correspondência.

As regras padrão existentes abrangem transporte, alimentação, lazer, saúde, casa, salário, investimentos e outros. Não inventar novas regras nem reclassificar categorias já informadas.

## Tratamento de erros

### Extração

- Propagar `FileNotFoundError` de `ler_csv` com o caminho informado.
- Relatar erros de parsing ou codificação produzidos pelo Pandas sem fingir que a importação ocorreu.

### Transformação

- Interromper diante de colunas necessárias ausentes.
- Interromper diante de data ou valor não conversível pela transformação atual.
- Informar a coluna e, quando disponível, exemplos de valores problemáticos.
- Não corrigir automaticamente formatos ambíguos sem confirmação do usuário.

### Categorização

- Se categorias do banco não puderem ser obtidas, informar que as regras persistidas não foram confirmadas.
- Não apresentar `outros` como correspondência de palavra-chave; ele também é o fallback do categorizador.

### Carga

- Propagar falhas de conexão, consulta ou inserção; `carregar_transacoes_mysql` já registra e relança a exceção.
- Não repetir automaticamente uma carga após erro sem determinar se houve inserção parcial.
- Distinguir registros ignorados por duplicidade de registros inválidos removidos antes do contador `recebidos`.

### Rota web

Interpretar:

- HTTP 400 como arquivo ausente, nome vazio ou extensão rejeitada;
- HTTP 401 como ausência de autenticação;
- HTTP 500 como falha de leitura, transformação, categorização ou carga, usando o campo `detalhe` para diagnóstico.

## Saída

### Análise sem carga

Entregar um resumo contendo:

- arquivo analisado;
- colunas encontradas, ausentes e adicionais;
- quantidade bruta de linhas;
- quantidade após transformação;
- quantidade categorizada automaticamente;
- distribuição de tipo, status e categoria, quando solicitada;
- amostra transformada, quando solicitada;
- erros ou alertas;
- confirmação explícita de que nada foi persistido.

Não salvar o CSV processado sem solicitação explícita.

### Importação direta

Combinar o contador de categorização com o retorno da carga:

```yaml
recebidos: <linhas válidas consideradas pela carga>
importados: <linhas novas inseridas>
ignorados: <recebidos menos importados>
categorizadas_automaticamente: <contador da transformação>
```

### Importação web

Esperar os mesmos quatro contadores e a mensagem `Planilha processada com sucesso.`.

Explicar que `ignorados` representa principalmente duplicatas após normalização e comparação. Linhas descartadas por data ou valor inválido na etapa interna de carga não entram em `recebidos`; no fluxo padrão, conversões inválidas costumam falhar antes, durante a transformação.

## Caminhos de execução

### Preferir o fluxo web

Usar `POST /api/upload` quando a aplicação estiver em execução e houver sessão autenticada. Esse é o caminho já integrado ao contexto do usuário e à resposta HTTP.

### Usar funções diretamente

Usar `ler_csv`, `tratar_transacoes` e, somente se autorizado, `carregar_transacoes_mysql`, mantendo o contexto do usuário e respeitando os contratos de retorno.

### Não usar o pipeline standalone atual

Não executar `src/main.py` como caminho confiável desta skill. No estado atual, ele trata a tupla retornada por `tratar_transacoes` como DataFrame e chama a carga sem `usuario_id`. Não corrigir o arquivo durante o uso desta skill; escolher o fluxo web ou as funções existentes com os argumentos corretos.

## Exemplos de uso

### Exemplo 1 — Validar sem importar

Solicitação:

> Analise `data/raw/transacoes_exemplo.csv`, mostre inconsistências e uma prévia tratada, mas não grave no banco.

Proceder com extração e transformação, apresentar o resumo de análise e declarar que a carga não foi executada.

### Exemplo 2 — Importar para o usuário autenticado

Solicitação:

> Importe este CSV financeiro para minha conta e informe quantos registros foram novos ou duplicados.

Preferir `/api/upload`, verificar autenticação e relatar `recebidos`, `importados`, `ignorados` e `categorizadas_automaticamente`.

### Exemplo 3 — Diagnosticar cabeçalho

Solicitação:

> Por que meu CSV com as colunas `date`, `description` e `amount` não entra no pipeline?

Comparar o cabeçalho com o contrato esperado, apontar `data`, `descricao`, `categoria`, `tipo`, `valor`, `conta`, `instituicao` e `status`, e não alterar módulos para aceitar aliases sem pedido explícito de desenvolvimento.

### Exemplo 4 — Explicar categorização

Solicitação:

> Mostre quais transações seriam categorizadas automaticamente antes de importar.

Executar até a transformação no contexto do usuário, comparar categoria original e final quando os dados permitirem e não chamar a carga.

### Exemplo 5 — Reimportação

Solicitação:

> Já importei este arquivo. Verifique o que aconteceria se eu enviar novamente.

Explicar e, se autorizado a executar a importação, usar a deduplicação existente por usuário. Não presumir que todas as linhas serão ignoradas antes de comparar os campos normalizados.
