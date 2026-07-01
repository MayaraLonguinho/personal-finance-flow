# Prompt 03: Cadastro

Implemente o sistema de cadastro de usuários:

1. Página de cadastro com formulário (nome, email, senha, confirmação de senha, telefone opcional)
2. Validações:
   - Nome ≥ 3 caracteres
   - Email válido
   - Senha ≥ 6 caracteres
   - Senha e confirmação coincidem
   - Email único
3. Hash da senha usando PBKDF2-SHA256 (não armazene texto plano)
4. Salva usuário no banco
5. Redireciona para login após cadastro bem-sucedido
