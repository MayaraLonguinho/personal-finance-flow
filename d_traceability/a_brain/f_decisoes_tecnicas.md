---
title: Decisões técnicas
tags:
  - personal-finance-flow
  - decisões
  - arquitetura
---

# Decisões técnicas

> [!info]
> Não há ADRs formais no repositório. As decisões abaixo são evidenciadas diretamente pela implementação e pelas dependências fixadas.

## DT-01 — Monólito Flask com páginas e APIs no mesmo processo

`app.py` serve templates e endpoints JSON. Isso mantém autenticação, sessão e regras de acesso na mesma aplicação. O frontend multipágina consome as APIs com `fetch()`.

## DT-02 — Frontend sem framework

Cada área possui HTML, CSS e JavaScript próprios. Não há React, Vue, Angular ou bundler nas dependências. Chart.js é carregado por CDN no dashboard.

## DT-03 — SQLAlchemy Core e Pandas em vez de ORM declarativo

O projeto usa SQL textual parametrizado, conexões explícitas e mapeamentos de resultados. Pandas é usado para consultas analíticas e carga em lote. Não existem classes de modelo ORM.

## DT-04 — MySQL configurado por ambiente

`src/load.py` constrói uma `URL` `mysql+pymysql` a partir de `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`. `python-dotenv` carrega o `.env`.

## DT-05 — Sessão como fonte da identidade

O login armazena `usuario_id` na sessão Flask. As rotas passam esse valor às consultas. Um `ContextVar` permite que funções internas resolvam o usuário mesmo quando ele não é fornecido explicitamente, e é limpo no teardown da requisição.

## DT-06 — Senhas com PBKDF2-SHA256

`src/auth.py` usa `generate_password_hash(..., method='pbkdf2:sha256')` e `check_password_hash`. A senha original não é persistida.

## DT-07 — Categorização determinística e configurável

A categorização não usa modelo de IA. Ela normaliza texto e compara palavras-chave. Regras padrão inicializam as categorias, mas as regras operacionais podem vir do banco por usuário.

## DT-08 — Duplicidade tratada na carga

A importação compara a linha normalizada com todas as transações existentes do usuário e grava apenas as novas. A decisão está implementada em Pandas, não em índice único do banco.

## DT-09 — Métricas calculadas sob demanda

Resumo, gastos por categoria, evolução, insights, progresso de meta e resumo de investimentos são calculados na consulta. O schema armazena os dados básicos, não tabelas agregadas.

## DT-10 — Assistente híbrido

A API tenta OpenAI primeiro e recorre ao agente local em qualquer exceção. O agente OpenAI usa function calling para obter números do domínio; o agente local usa regras de intenção. Assim, a interface mantém uma resposta mesmo sem cliente OpenAI funcional.

## DT-11 — Ferramentas como fronteira dos dados da IA

O prompt exige que números financeiros venham das ferramentas. O modelo não recebe acesso direto ao SQL nem aos arquivos. As funções de ferramenta consultam os módulos financeiros no contexto do usuário.

## DT-12 — Preferências como dados por usuário

As preferências ficam em `configuracoes_usuario`, com uma linha por `usuario_id`. O backend injeta o objeto serializado nos templates e os scripts reutilizam `window.PFF` para formatar e controlar a apresentação.

O tema deixou de depender de armazenamento local do navegador: a fonte implementada é a configuração persistida. Moeda muda a formatação, mas não converte montantes.

## DT-13 — Atualização parcial de configurações

Antes de salvar, `salvar_configuracoes_usuario` lê o estado atual, aplica somente os campos recebidos, valida valores permitidos e executa um upsert. Isso permite, por exemplo, mudar apenas o tema no dashboard sem restaurar as outras opções.

## DT-14 — Compatibilidade de schema em tempo de execução

Na importação de `app.py`, `garantir_colunas_usuario()` consulta `information_schema` e adiciona `usuario_id` a metas, categorias e investimentos quando ausente. O módulo de configurações também cria sua tabela sob demanda com `CREATE TABLE IF NOT EXISTS`.

## DT-15 — Formatação na borda

Datas e moedas permanecem como valores básicos no banco e nas respostas. `static/js/temas.js` formata a interface; `src/utils.py` formata textos gerados no backend e no agente local. Essa separação preserva os cálculos.

## Consequências observáveis

- O código permanece simples de executar como uma única aplicação.
- Há repetição entre JavaScripts, CSS e funções de conexão.
- Integridade multiusuário depende principalmente das consultas, pois o schema não possui FKs.
- A criação de engine e algumas verificações de schema ocorrem em tempo de execução.
- O fallback local reduz a dependência operacional da OpenAI, mas mantém duas implementações de interpretação de perguntas.

## Relações

- [[02-arquitetura]]
- [[03-modelo-de-dados]]
- [[06-erros-e-aprendizados]]
- [[07-prompts]]
