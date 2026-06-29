# Arquitetura Geral

## Estilo geral

A aplicação é um monólito Flask organizado em camadas informais. `app.py` concentra composição, rotas, autenticação e tradução HTTP; os módulos em `src/` concentram domínio, consultas SQL, ETL, métricas e assistentes. O frontend é multipágina, renderizado no servidor, e usa JavaScript para consumir APIs JSON.

## Camada web — `app.py`

Responsabilidades:

- Configurar Flask, JSON e chave de sessão.
- Proteger rotas com `login_obrigatorio`.
- Renderizar páginas Jinja.
- Delegar operações aos módulos em `src/`.

## Camada de domínio e dados — `src/`

| Módulo | Papel |
|---|---|
| `auth.py` | Usuários, hashes e consulta de credenciais |
| `transacoes.py` | Consulta e CRUD de transações |
| `categorias.py` | CRUD, regras e estatísticas de categorias |
| `metas.py` | Consulta e CRUD de metas |
| `investimentos.py` | Validação, CRUD e resumo de investimentos |
| `metrics.py` | Métricas, insights e transações recentes |
| `extract.py`, `transform.py`, `load.py` | Pipeline ETL de CSV |
| `financial_agent.py`, `ai_financial_agent.py` | Assistentes financeiros |

## Persistência

- Banco: MySQL via PyMySQL + SQLAlchemy Core (sem ORM)
- Pandas para consultas analíticas e carga em lote
- SQL parametrizado para segurança

## Isolamento por usuário

Todas as consultas incluem `WHERE usuario_id = :usuario_id`, garantindo que cada usuário só veja seus próprios dados.
