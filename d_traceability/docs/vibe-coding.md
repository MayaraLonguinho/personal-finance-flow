# Vibe coding no Personal Finance Flow

## Escopo e fontes

Este documento registra como o Windsurf e agentes de IA participaram das etapas de desenvolvimento que podem ser confirmadas no estado atual do projeto.

As fontes usadas são:

- histórico Git e alterações presentes no repositório;
- arquivos de `brain/`, `docs/`, `skills/`, `mcp/` e `tests/`;
- solicitações registradas na sequência de trabalho que produziu esses artefatos;
- resultados de comandos de validação executados durante a implementação do MCP.

O repositório não contém exportação das conversas do Cascade, telemetria do Windsurf nem o histórico completo dos prompts usados desde o início do projeto. Por isso, não é possível atribuir à IA a autoria de todo o sistema, medir quanto código foi gerado automaticamente ou afirmar quais recursos específicos do editor foram usados além do contexto de arquivos e da configuração MCP documentada.

## Papel do Windsurf

O Windsurf foi o ambiente de desenvolvimento apresentado durante o trabalho. O contexto compartilhado pelo editor indicou o arquivo ativo e as abas relevantes, o que ajudou o agente a localizar rapidamente rotas, templates, módulos de configuração, agentes financeiros e documentação.

Também foi preparado um servidor MCP local para uso no Windsurf. A entrada versionada em `mcp/configuracao-exemplo.json` inicia `mcp/server.py` por `stdio` e referencia um arquivo local de ambiente. A instalação e a ativação são descritas em `mcp/README.md`.

Não há evidência versionada de que o MCP já tenha sido habilitado no Windsurf ou consultado pelo Cascade com dados reais. O que foi confirmado é a implementação do servidor, sua configuração de exemplo e o teste do protocolo por um cliente MCP local.

## Papel dos agentes de IA

Os agentes foram usados como colaboradores de análise, documentação, implementação e validação. As atividades confirmadas nesta sequência foram:

1. analisar as configurações por usuário e seu isolamento por `usuario_id`;
2. aplicar preferências de tema, moeda, data, transações recentes, cards e confirmação de exclusão na interface;
3. revisar o projeto e preencher o vault técnico em `brain/`;
4. formalizar a skill `financial-csv-analyzer` sem duplicar o pipeline;
5. documentar o assistente OpenAI e o fallback local;
6. propor uma integração MCP somente leitura;
7. implementar apenas o MCP aprovado, com SQL fixo e resources controlados;
8. executar testes e revisar a superfície de segurança do MCP.

O assistente financeiro existente na aplicação é outro uso de IA, distinto do agente de desenvolvimento. `src/ai_financial_agent.py` usa a OpenAI com function calling; `src/financial_agent.py` oferece fallback local determinístico, sem LLM.

## Planejamento

O trabalho foi dividido por escopo e por risco, em vez de solicitar uma reescrita ampla da aplicação.

### Configurações

Primeiro foi solicitado verificar se nome, tema, moeda, formato de data, limite de transações, confirmação de exclusão, cards e restauração já existiam e se eram persistidos por usuário. Depois da análise, uma segunda etapa autorizou aplicar as preferências globalmente, com a restrição explícita de não alterar conteúdo financeiro nem regras do banco.

O histórico Git confirma essa separação:

- `8cedc52` — criação das configurações por usuário;
- `2cbe74f` — aplicação global das configurações nos templates e scripts.

### Documentação e revisão

A revisão documental foi solicitada sem alteração de código. Ela produziu o commit `b5f1e06`, que preencheu oito notas do vault `brain/` com visão geral, requisitos, arquitetura, modelo de dados, ETL, decisões, erros e prompts confirmados.

Na sequência, tarefas independentes formalizaram a skill do CSV e a documentação do assistente. Essa divisão preservou os módulos existentes e evitou misturar documentação com mudanças de comportamento.

### MCP

O MCP foi planejado antes da implementação. A decisão humana foi priorizar um servidor local somente leitura, voltado a consultas financeiras predefinidas e arquivos controlados. A implementação só foi autorizada depois, com três restrições explícitas:

- não expor credenciais;
- não aceitar consultas arbitrárias;
- não oferecer operações de escrita.

## Geração inicial

A geração assistida ocorreu em incrementos verificáveis, não como criação integral do projeto em uma única etapa.

Na área de configurações, foram criados o módulo `src/configuracoes.py`, a página, o CSS e o JavaScript próprios. Em um incremento posterior, preferências passaram a ser injetadas nos templates e consumidas pelos scripts das páginas.

Na documentação, os arquivos que antes continham apenas títulos foram preenchidos por inspeção do código existente. O vault não apresenta requisitos imaginados como fatos: `brain/01-requisitos.md`, por exemplo, declara que os requisitos foram derivados de rotas, validações, templates e funções.

A skill `skills/financial-csv-analyzer/SKILL.md` referencia `extract.py`, `transform.py`, `categorization.py` e `load.py` como fontes de verdade. Ela orienta reutilizar o pipeline e alerta para não executar `src/main.py` como caminho confiável, sem copiar a implementação para dentro da skill.

O MCP foi gerado como uma fachada separada em `mcp/`, sem importar `app.py` nem os módulos que executam migração ou escrita. Sua superfície possui seis tools financeiras e cinco resources fixos.

## Revisão

A revisão assistida combinou leitura de código, comparação entre camadas e checagem do histórico Git.

Na revisão funcional foram conferidos:

- uso de `session["usuario_id"]` nas rotas;
- propagação da identidade por `ContextVar`;
- filtros `usuario_id` nas consultas financeiras;
- persistência das preferências em `configuracoes_usuario`;
- diferença entre formatação monetária e conversão de moeda;
- contratos do pipeline CSV;
- tools, fontes de dados e fallback do assistente;
- divergências entre schema, documentação e implementação.

Na revisão do MCP, a lista de tools foi comparada com o plano aprovado. Também foram inspecionados os schemas de entrada para confirmar que nenhum deles publica `usuario_id`, SQL, query ou caminho de arquivo.

## Depuração

Os seguintes eventos de depuração foram observados durante a implementação do MCP:

### Versão do Python

O ambiente principal usa Python 3.9, enquanto o SDK MCP instalado exige Python 3.10 ou superior. A correção foi criar `.venv-mcp` com Python 3.14, mantendo o ambiente da aplicação separado e sem alterar suas dependências.

### Cache de bytecode

A primeira compilação sintática tentou escrever no cache global do Python e recebeu `PermissionError`. A validação foi repetida com `PYTHONPYCACHEPREFIX` apontando para `/tmp`, e a compilação concluiu sem erro.

### Instalação de dependências

A primeira instalação de `requirements-mcp.txt` falhou por resolução de nome bloqueada no ambiente restrito. Depois da autorização para acesso externo, a instalação foi repetida e concluiu com `mcp 1.28.1` e as dependências declaradas.

### Precedência do usuário fixo

Durante a revisão, foi identificado que a função interna `_fetch_all` montava primeiro `usuario_id` e depois aplicava parâmetros adicionais. Embora nenhuma tool permitisse enviar essa identidade, um futuro chamador interno poderia sobrescrevê-la. A ordem foi corrigida para que o usuário fixado no processo sempre prevaleça, e um teste de regressão foi incluído.

## Testes

Antes do MCP, `brain/06-erros-e-aprendizados.md` registrava a ausência de testes versionados. A implementação do MCP adicionou `tests/test_mcp_readonly.py`.

Foram executados 11 testes unitários, todos aprovados. Eles cobrem:

- consultas iniciadas por `SELECT` e sem verbos mutáveis;
- filtro obrigatório por `usuario_id`;
- impossibilidade de sobrescrever o usuário fixo;
- limites entre 1 e 20;
- fórmula do saldo financeiro;
- cálculo de progresso da meta;
- conjunto exato de tools aprovadas;
- ausência de argumentos perigosos nas tools;
- ausência de imports dos módulos da aplicação com efeitos de escrita;
- allowlist de resources;
- rejeição de caminho não autorizado.

Também foram confirmados:

- compilação sintática dos novos módulos;
- validade de `mcp/configuracao-exemplo.json`;
- ausência de erros em `git diff --check`;
- inicialização do servidor MCP;
- handshake real por `stdio`, negociando o protocolo `2025-11-25`;
- publicação das seis tools e dos cinco resources previstos.

O banco real não foi consultado durante esses testes, pois não foram fornecidas credenciais da conta MySQL dedicada somente leitura. Portanto, não há resultado confirmado de teste de integração com dados financeiros reais nem teste confirmado da interface pelo navegador.

## Decisões humanas

As decisões que permaneceram sob controle explícito da pessoa responsável pelo projeto foram:

- priorizar isolamento entre usuários;
- manter conteúdo financeiro e regras do banco fora do escopo dos ajustes visuais;
- usar moeda apenas para formatação, sem conversão de valores;
- exigir confirmação antes de implementar o MCP proposto;
- limitar o MCP a leitura;
- não permitir SQL ou caminhos de arquivo fornecidos pelo modelo;
- manter credenciais fora do repositório;
- preservar os módulos existentes ao documentar a skill e o assistente;
- separar análise/documentação de etapas autorizadas de implementação.

Essas decisões funcionaram como critérios de aceitação. O agente propôs, inspecionou e executou, mas não ampliou sozinho o escopo para migrações, correções financeiras ou alterações do banco.

## Erros encontrados e correções realizadas

### Corrigidos no desenvolvimento registrado

| Problema confirmado | Correção confirmada |
|---|---|
| Consultas e áreas financeiras precisavam de isolamento por conta | Commits de autenticação e isolamento passaram `usuario_id` da sessão às consultas e operações de domínio |
| Preferências existiam, mas precisavam ser aplicadas globalmente | `2cbe74f` centralizou preferências nos templates e scripts das páginas |
| Tema dependia de comportamento local da interface | A configuração persistida por usuário passou a ser a fonte usada pela interface |
| Risco interno de sobrescrever o usuário fixo do MCP | A precedência dos parâmetros foi invertida e protegida por teste |
| Python principal incompatível com o SDK MCP | Foi criado um ambiente virtual separado para o servidor |
| Compilação bloqueada pelo cache global | O cache de bytecode foi redirecionado para `/tmp` durante a validação |

### Identificados, mas não corrigidos nesta sequência

O vault registra problemas que permaneceram apenas documentados porque corrigi-los não fazia parte das solicitações:

- `src/main.py` está incompatível com o retorno atual de `tratar_transacoes` e com o `usuario_id` obrigatório da carga;
- `categorias.nome` possui unicidade global, apesar do escopo por usuário;
- o schema não define chaves estrangeiras para `usuario_id`;
- alguns métodos internos ainda admitem execução sem proprietário;
- exclusão de categoria divide uma operação lógica entre conexões;
- uploads preservam o nome original e não são removidos após processamento;
- algumas exceções são convertidas silenciosamente em valores vazios;
- `SECRET_KEY` possui fallback conhecido de desenvolvimento;
- README, porta de execução e roadmap estão desatualizados;
- dashboard e relatório usam semânticas diferentes de saldo e status.

Não há evidência de correção desses itens no estado analisado, portanto eles não devem ser apresentados como concluídos.

## Boas práticas adotadas

- inspeção do código antes de propor mudanças;
- implementação incremental e revisão entre etapas;
- consultas SQL parametrizadas;
- identidade derivada da sessão ou fixada fora dos argumentos das tools;
- allowlist para tools, functions e resources;
- limites explícitos para texto e quantidade de resultados;
- separação entre formatação e valores financeiros;
- fallback local quando a OpenAI não está disponível;
- ambiente MCP isolado do ambiente Flask;
- credenciais em arquivo local ignorado pelo Git;
- usuário MySQL dedicado com apenas `SELECT`;
- documentação de limitações e divergências, não apenas do caminho ideal;
- testes negativos para segurança e isolamento;
- preservação de alterações existentes e de módulos fora do escopo;
- distinção entre problemas diagnosticados e problemas efetivamente corrigidos.

## Limites desta documentação

Este registro não comprova:

- que todo o código foi criado por agentes de IA;
- quais sugestões do Windsurf foram aceitas ou rejeitadas antes dos commits;
- duração, custo ou quantidade total de interações com modelos;
- execução de testes de interface completos;
- validação do MCP contra um banco real;
- uso do MCP dentro do Cascade após sua configuração.

Esses dados exigiriam logs do editor, histórico exportado de conversas ou evidências adicionais que não estão no repositório.
