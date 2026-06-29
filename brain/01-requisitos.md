---
title: Requisitos
tags:
  - personal-finance-flow
  - requisitos
---

# Requisitos

> [!note]
> Estes requisitos foram derivados exclusivamente de validações, rotas, templates e funções presentes no projeto. Não representam uma especificação externa.

## Atores

### Visitante

- Visualiza a página inicial.
- Acessa as páginas de login e cadastro.
- Cria uma conta com nome, e-mail, senha, confirmação de senha e telefone opcional.
- Realiza login com e-mail e senha.

### Usuário autenticado

- Acessa dashboard, transações, categorias, relatórios, metas, investimentos, assistente e configurações.
- Opera somente os dados associados ao `usuario_id` da sessão nas rotas da aplicação.

## Requisitos funcionais

### RF-01 — Autenticação

- O nome deve possuir pelo menos três caracteres no cadastro.
- O e-mail deve conter `@` e `.` e é normalizado para minúsculas.
- A senha deve possuir pelo menos seis caracteres e coincidir com a confirmação.
- O e-mail deve ser único.
- A senha é persistida como hash PBKDF2-SHA256.
- O login cria as chaves `usuario_id`, `usuario_nome` e `usuario_email` na sessão.
- APIs protegidas retornam HTTP 401 sem sessão; páginas protegidas redirecionam ao login.

### RF-02 — Dashboard

- Exibe total de entradas, saídas, investimentos, saldo e quantidade de transações confirmadas.
- Calcula saldo como `entradas - saídas - investimentos`.
- Exibe gastos por categoria, movimento por tipo, evolução mensal e até quatro insights.
- Lista transações recentes confirmadas, ordenadas por data e ID decrescentes.
- Exibe resumo da meta ativa e da carteira de investimentos.
- Permite importar CSV, limpar transações do usuário e trocar o tema.

### RF-03 — Transações

- Lista transações com filtros por descrição, categoria, tipo e status.
- Cria, atualiza e exclui transações.
- Tipos aceitos pela API: `entrada`, `saida` e `investimento`.
- Status aceitos pela API: `confirmado`, `pendente` e `cancelado`.
- Data, descrição, tipo, valor e status são obrigatórios na criação e edição.
- O valor deve ser numérico e maior que zero.
- Operações de alteração e exclusão verificam simultaneamente ID da transação e `usuario_id`.
- Uma categoria vazia ou igual a `outros` pode ser substituída pela categorização automática.

### RF-04 — Importação CSV

- Aceita arquivo cujo nome termine em `.csv`.
- Rejeita ausência de arquivo, nome vazio e extensão diferente.
- Salva o arquivo recebido em `uploads/`.
- Processa o CSV com Pandas, transforma os dados, categoriza e carrega somente registros ainda não existentes para o usuário.
- Retorna quantidades recebidas, importadas, ignoradas e categorizadas automaticamente.

### RF-05 — Categorias

- Inicializa categorias padrão: transporte, alimentação, lazer, saúde, casa, salário, investimentos e outros.
- Cada categoria pode possuir palavras-chave em JSON e uma cor.
- Permite criar, editar e excluir categorias.
- A categoria `outros` não pode ser excluída.
- Ao excluir outra categoria, o código tenta mover as transações associadas para `outros` antes da exclusão.
- Exibe quantidade e valor total das transações por categoria.

### RF-06 — Metas

- Consulta a meta ativa mais recente do usuário.
- Permite criar, atualizar e excluir metas.
- O valor da meta deve ser maior que zero.
- O valor atual não pode ser negativo.
- Status permitidos: `ativa`, `concluida` e `cancelada`.
- Calcula percentual com teto de 100% e valor restante com piso zero.

### RF-07 — Investimentos

- Permite listar todos ou filtrar por status.
- Permite consultar, criar, atualizar e excluir por ID.
- Status permitidos: `ativo`, `resgatado` e `cancelado`.
- Nome, tipo, valor aplicado, valor atual e data de aplicação são obrigatórios.
- Valor aplicado deve ser positivo; valor atual não pode ser negativo.
- Data de vencimento, quando fornecida, não pode anteceder a aplicação.
- Calcula resumo da carteira, incluindo totais, resultado, rentabilidade e quantidades.

### RF-08 — Relatórios

- Aceita filtros opcionais `data_inicio` e `data_fim` no formato `YYYY-MM-DD`.
- Rejeita intervalo em que a data inicial seja posterior à final.
- Retorna resumo financeiro, categorias e transações do intervalo, junto ao resumo atual da carteira de investimentos.
- O filtro de datas é aplicado às transações; o resumo da carteira chamado pelo relatório não recebe o intervalo.
- Permite impressão pelo frontend.

### RF-09 — Assistente financeiro

- Recebe perguntas não vazias com até 500 caracteres.
- Tenta primeiro o agente OpenAI.
- Usa ferramentas para consultar saldo, entradas, saídas, categorias, investimentos, meta, quantidade e transações recentes.
- Em falha da OpenAI, usa o agente local baseado em normalização de texto e detecção de intenções.
- Não deve inventar números nem fornecer aconselhamento financeiro personalizado, conforme o prompt de sistema.

### RF-10 — Configurações do usuário

- Permite configurar nome de exibição, tema, moeda, formato de data, quantidade de transações recentes, confirmação de exclusão e cards visíveis.
- Temas permitidos: azul, rosa, verde, vermelho e escuro.
- Moedas permitidas: BRL, USD e EUR.
- Formatos permitidos: `DD/MM/YYYY`, `MM/DD/YYYY` e `YYYY-MM-DD`.
- O limite de transações recentes é restringido ao intervalo de 3 a 20.
- Cards configuráveis: resumo financeiro, investimentos, transações recentes e meta de economia.
- Permite restaurar os valores padrão.
- As preferências são injetadas nas páginas e utilizadas pelos formatadores JavaScript e Python.
- A mudança de moeda altera a apresentação, não converte os valores financeiros.

## Requisitos de isolamento e segurança observados

- O decorator `login_obrigatorio` protege páginas internas e APIs de negócio.
- `before_request` copia o `usuario_id` da sessão para um `ContextVar`; `teardown_request` limpa o contexto.
- Consultas principais de métricas, metas e categorias exigem usuário explícito ou disponível no contexto.
- As rotas passam o identificador da sessão para transações, metas, categorias, relatórios, investimentos e configurações.
- SQL com dados externos usa parâmetros nomeados, exceto trechos estruturais controlados pelo código, como filtros e `LIMIT`.

## Restrições e lacunas confirmadas

- O schema não declara chaves estrangeiras entre `usuario_id` e `usuarios.id`.
- `usuario_id` é anulável em metas, categorias e investimentos no schema.
- A restrição `UNIQUE` de `categorias.nome` é global, embora o código trate categorias por usuário.
- Alguns métodos de repositório permitem omitir `usuario_id`; as rotas atuais o fornecem.
- O segredo Flask possui um valor padrão de desenvolvimento se `SECRET_KEY` não estiver definido.
- Não há suíte de testes versionada no projeto.

## Relações

- Visão do produto: [[00-visao-geral]]
- Implementação dos requisitos: [[02-arquitetura]]
- Persistência: [[03-modelo-de-dados]]
- Limitações: [[06-erros-e-aprendizados]]
