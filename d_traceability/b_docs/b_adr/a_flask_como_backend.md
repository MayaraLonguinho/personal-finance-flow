# ADR 001: Flask como Backend

## Status

✅ Aceito

## Contexto

Precisávamos de um framework web para a aplicação de finanças pessoais.

## Decisão

Utilizar **Flask 3.1.3** como backend web.

## Justificativa

- Simples e leve, adequado para o escopo do projeto
- Ecossistema maduro (Flask-Login, Flask-SQLAlchemy, python-dotenv)
- Integração nativa com Jinja2 para templates server-side
- Fácil de aprender e manter
- Já havia sido iniciado no projeto

## Consequências

### Positivas
- Desenvolvimento rápido
- Baixa curva de aprendizado
- Arquitetura simples (monólito)
- Templates Jinja2 funcionam bem para o frontend multipágina

### Negativas
- Não é um framework full-stack como Django (menos baterias inclusas)
- Escalabilidade horizontal mais complexa que arquiteturas de microserviços
- Monólito pode ficar grande se o projeto crescer muito

## Alternativas Consideradas
- Django (mais pesado, overkill para o MVP)
- FastAPI (moderno, mas menos foco em templates server-side)
- Node.js/Express (requeria mudar stack de Python para JS)
