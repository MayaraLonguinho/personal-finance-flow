# Personal Finance Flow MCP — somente leitura

Servidor MCP local para consultar dados financeiros de uma única conta e ler documentação explicitamente autorizada do projeto.

## Garantias de escopo

- Seis tools financeiras, todas de leitura.
- Cinco resources mapeados por URI fixa.
- Nenhuma tool aceita `usuario_id`, SQL ou caminho de arquivo.
- Consultas SQL estáticas, parametrizadas e filtradas por usuário.
- Validação de todas as queries contra verbos de escrita.
- Conta MySQL dedicada com permissão somente `SELECT`.
- Servidor `stdio`, sem porta de rede aberta.

O servidor não importa `app.py` nem chama funções que criam ou alteram tabelas.

## Requisitos

- Python 3.10 ou superior. O ambiente principal atual usa Python 3.9, portanto use um ambiente separado.
- MySQL acessível localmente.
- Schema do Personal Finance Flow aplicado.
- Usuário MySQL exclusivo para o MCP.

## 1. Criar o usuário MySQL somente leitura

Execute como administrador do MySQL, substituindo a senha pelo segredo local:

```sql
CREATE USER 'pff_mcp_reader'@'localhost' IDENTIFIED BY '<senha-forte-local>';

GRANT SELECT ON personal_finance_flow.transacoes
TO 'pff_mcp_reader'@'localhost';

GRANT SELECT ON personal_finance_flow.metas
TO 'pff_mcp_reader'@'localhost';

GRANT SELECT ON personal_finance_flow.categorias
TO 'pff_mcp_reader'@'localhost';

GRANT SELECT ON personal_finance_flow.investimentos
TO 'pff_mcp_reader'@'localhost';

GRANT SELECT ON personal_finance_flow.configuracoes_usuario
TO 'pff_mcp_reader'@'localhost';
```

Não conceda acesso à tabela `usuarios` e não use a conta administrativa da aplicação.

Para conferir as permissões:

```sql
SHOW GRANTS FOR 'pff_mcp_reader'@'localhost';
```

## 2. Criar o ambiente MCP

No diretório raiz do projeto:

```bash
python3.14 -m venv .venv-mcp
.venv-mcp/bin/python -m pip install --upgrade pip
.venv-mcp/bin/python -m pip install -r requirements-mcp.txt
```

Qualquer Python 3.10+ compatível pode substituir `python3.14`.

## 3. Configurar credenciais locais

```bash
cp .env.mcp.example .env.mcp
```

Preencha `.env.mcp` localmente:

```dotenv
PFF_MCP_USER_ID=1
PFF_MCP_DB_HOST=localhost
PFF_MCP_DB_PORT=3306
PFF_MCP_DB_USER=pff_mcp_reader
PFF_MCP_DB_PASSWORD=<senha-forte-local>
PFF_MCP_DB_NAME=personal_finance_flow
```

O arquivo `.env.mcp` está ignorado pelo Git. Não reutilize `DB_USER` ou `DB_PASSWORD` da aplicação.

`PFF_MCP_USER_ID` fixa a identidade durante toda a vida do processo. O modelo não consegue substituí-lo em uma chamada de tool.

## 4. Configurar o Windsurf

O Windsurf Editor mantém a configuração em:

```text
~/.codeium/windsurf/mcp_config.json
```

Também é possível abrir `Windsurf Settings → Cascade → MCP Servers → View Raw Config`.

Copie a entrada de `mcp/configuracao-exemplo.json` para `mcpServers`. Ajuste apenas os caminhos absolutos se o projeto estiver em outro local. A configuração referencia `.env.mcp`; não contém as credenciais.

Depois de salvar, atualize a lista de MCPs no Windsurf e habilite `personal-finance-flow-readonly`.

## Tools

| Tool | Entradas | Saída |
|---|---|---|
| `get_financial_summary` | nenhuma | Entradas, saídas, investimentos, saldo, quantidade e moeda |
| `get_recent_transactions` | `limit` entre 1 e 20 | Transações confirmadas recentes |
| `get_spending_by_category` | `category?`, `limit` entre 1 e 20 | Saídas confirmadas agrupadas |
| `get_active_goal` | nenhuma | Meta ativa, percentual e restante |
| `get_investment_summary` | nenhuma | Resumo e distribuição da carteira ativa |
| `list_categories` | nenhuma | Nomes das categorias da conta |

## Resources permitidos

```text
pff://project/overview
pff://project/architecture
pff://project/data-model
pff://project/etl
pff://project/schema
```

Não existe resource dinâmico por caminho. `.env`, `g_uploads/`, CSVs, `.git/` e demais arquivos não são acessíveis.

## Testes locais

Os testes unitários não precisam de banco nem do SDK MCP:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_mcp_readonly.py' -v
```

Eles validam:

- queries exclusivamente `SELECT`;
- presença obrigatória de `usuario_id`;
- identidade injetada pelo servidor;
- limites de resultados;
- fórmula financeira;
- tools aprovadas sem parâmetros perigosos;
- imports sem efeitos de escrita;
- allowlist de resources.

Após instalar o ambiente MCP, valide os imports:

```bash
PFF_MCP_ENV_FILE="$PWD/.env.mcp" \
  .venv-mcp/bin/python -c "import sys; sys.path.insert(0, 'mcp'); import server; print('MCP carregado')"
```

O comando abre conexão somente quando uma tool é executada.

## Teste com MCP Inspector

Opcionalmente:

```bash
npx -y @modelcontextprotocol/inspector \
  "$PWD/.venv-mcp/bin/python" \
  "$PWD/mcp/server.py"
```

Defina `PFF_MCP_ENV_FILE` no ambiente antes de iniciar o Inspector.

## Demonstração no Windsurf

Perguntas sugeridas:

- “Use o MCP para mostrar meu resumo financeiro.”
- “Liste minhas cinco transações confirmadas mais recentes.”
- “Em qual categoria eu mais gastei?”
- “Como está minha meta ativa?”
- “Qual é o resultado atual da minha carteira?”
- “Leia `pff://project/data-model` e explique a origem dos totais.”

Testes negativos:

- solicitar 500 transações deve falhar na validação;
- solicitar dados de outro `usuario_id` não é possível, pois o argumento não existe;
- solicitar leitura de `.env` não encontra resource correspondente;
- solicitar SQL arbitrário não encontra tool correspondente.

## Solução de problemas

### O servidor não aparece

- Confira os caminhos absolutos em `mcp_config.json`.
- Confirme que `.venv-mcp/bin/python` existe.
- Atualize a lista de MCPs no Windsurf.

### Variável obrigatória ausente

Confira `PFF_MCP_ENV_FILE` e as seis variáveis de `.env.mcp`. O erro não imprime os valores configurados.

### Acesso negado no MySQL

Confira `SHOW GRANTS`. A conta precisa somente de `SELECT` nas cinco tabelas listadas.

### Dados de usuário incorreto

Pare o servidor, corrija `PFF_MCP_USER_ID` e reinicie o MCP. Não exponha esse identificador como argumento de tool.

## Arquivos da integração

```text
mcp/server.py
mcp/readonly_service.py
mcp/schemas.py
mcp/allowed_resources.py
mcp/configuracao-exemplo.json
mcp/README.md
requirements-mcp.txt
.env.mcp.example
tests/test_mcp_readonly.py
```
