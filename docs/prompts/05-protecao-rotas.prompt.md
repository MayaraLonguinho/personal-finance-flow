# Prompt 05: Proteção de Rotas

Implemente proteção de rotas e isolamento por usuário:

1. Crie decorator `login_obrigatorio` que verifica sessão
2. Se não logado, redireciona para login (páginas) ou retorna 401 (APIs)
3. Use ContextVar para propagar usuario_id:
   - before_request copia session["usuario_id"] para ContextVar
   - teardown_request limpa o ContextVar
4. Todas as consultas SQL devem incluir WHERE usuario_id = :usuario_id
5. Garanta que nenhum usuário veja dados de outro
