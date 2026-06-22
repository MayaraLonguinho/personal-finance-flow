# Personal Finance Flow

Dashboard financeira pessoal end-to-end para controle de transações financeiras.

## Objetivo do Projeto

Desenvolver uma dashboard financeira pessoal onde o usuário poderá:
- Importar transações financeiras de um arquivo CSV
- Tratar os dados com Pandas
- Salvar no banco de dados MySQL
- Visualizar indicadores financeiros em uma dashboard web

## Tecnologias Utilizadas

- **Backend**: Python com Flask
- **Frontend**: HTML, CSS e JavaScript
- **Processamento de Dados**: Pandas
- **Banco de Dados**: MySQL
- **ORM**: SQLAlchemy
- **Variáveis de Ambiente**: python-dotenv

## Estrutura de Pastas

```
personal-finance-flow/
├── app.py                      # Aplicação Flask principal
├── requirements.txt            # Dependências do projeto
├── .env.example               # Exemplo de variáveis de ambiente
├── README.md                  # Documentação do projeto
├── data/                      # Diretório de dados
│   ├── raw/                   # Dados brutos (CSV)
│   │   └── transacoes_exemplo.csv
│   └── processed/             # Dados processados
├── database/                  # Scripts do banco de dados
│   └── schema.sql            # Schema do banco MySQL
├── src/                       # Módulos de processamento
│   ├── extract.py            # Extração de dados
│   ├── transform.py          # Transformação de dados
│   ├── load.py               # Carregamento no banco
│   └── metrics.py            # Cálculo de métricas
├── templates/                 # Templates HTML
│   ├── index.html            # Página inicial
│   └── dashboard.html        # Dashboard
└── static/                    # Arquivos estáticos
    ├── css/
    │   └── style.css         # Estilos CSS
    └── js/
        └── dashboard.js       # JavaScript do dashboard
```

## Como Executar o Projeto

### 1. Configurar o Banco de Dados

#### Criar o banco de dados no MySQL

Conecte-se ao MySQL e execute o seguinte comando para criar o banco de dados:

```sql
CREATE DATABASE personal_finance_flow;
```

#### Executar o script schema.sql

Após criar o banco, execute o script para criar a tabela de transações:

```bash
mysql -u root -p personal_finance_flow < database/schema.sql
```

Ou execute diretamente no cliente MySQL:

```sql
USE personal_finance_flow;
SOURCE database/schema.sql;
```

#### Configurar o arquivo .env

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais do MySQL:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=personal_finance_flow
```

#### Testar a conexão (futuramente)

Para testar a conexão com o banco de dados, você pode usar o módulo `src/database.py`:

```python
from src.database import get_connection

engine = get_connection()
print("Conexão estabelecida com sucesso!")
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## Próximos Passos

- Implementar upload de arquivos CSV
- Conectar com o banco de dados MySQL
- Desenvolver a lógica de processamento ETL
- Implementar visualização de métricas no dashboard
- Adicionar gráficos e relatórios
