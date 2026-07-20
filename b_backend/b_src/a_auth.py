# Módulo de autenticação
# Responsável por gerenciar usuários e autenticação

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from c_generate_rpa.d_load import obter_engine


def criar_usuario(nome, email, telefone, senha):
    """
    Cria um novo usuário no banco de dados.
    
    Args:
        nome (str): Nome do usuário
        email (str): Email do usuário (deve ser único)
        telefone (str): Telefone do usuário (opcional)
        senha (str): Senha do usuário (será hasheada)
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        from b_backend.b_src.d_categorias import inicializar_categorias_padrao
        
        engine = obter_engine()
        
        # Verifica se o email já existe
        query_check = text("SELECT id FROM usuarios WHERE email = :email")
        with engine.connect() as conn:
            result = conn.execute(query_check, {'email': email}).fetchone()
            if result:
                return {'sucesso': False, 'erro': 'Email já cadastrado'}
        
        # Gera hash da senha usando pbkdf2:sha256 (mais compatível)
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        # Insere o novo usuário
        query_insert = text("""
            INSERT INTO usuarios (nome, email, telefone, senha_hash)
            VALUES (:nome, :email, :telefone, :senha_hash)
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query_insert, {
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'senha_hash': senha_hash
            })
            conn.commit()
        
        usuario_id = result.lastrowid
        
        # Inicializa categorias padrão para o novo usuário
        resultado_categorias = inicializar_categorias_padrao(usuario_id=usuario_id)
        if not resultado_categorias['sucesso']:
            return {'sucesso': False, 'erro': f'Usuário criado, mas erro ao inicializar categorias: {resultado_categorias["erro"]}'}
        
        return {'sucesso': True, 'mensagem': 'Usuário criado com sucesso', 'id': usuario_id}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def buscar_usuario_por_email(email):
    """
    Busca um usuário pelo email.
    
    Args:
        email (str): Email do usuário
        
    Returns:
        dict: Dicionário com os dados do usuário ou None se não encontrado
    """
    try:
        engine = obter_engine()
        
        query = text("""
            SELECT id, nome, email, telefone, senha_hash, criado_em
            FROM usuarios
            WHERE email = :email
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'email': email}).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'nome': result[1],
                    'email': result[2],
                    'telefone': result[3],
                    'senha_hash': result[4],
                    'criado_em': result[5].isoformat() if result[5] else None
                }
        
        return None
        
    except Exception as e:
        return None


def verificar_senha(senha_hash, senha):
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    
    Args:
        senha_hash (str): Hash da senha armazenada
        senha (str): Senha a ser verificada
        
    Returns:
        bool: True se a senha estiver correta, False caso contrário
    """
    return check_password_hash(senha_hash, senha)


def obter_usuario_por_id(usuario_id):
    """
    Busca um usuário pelo ID.
    
    Args:
        usuario_id (int): ID do usuário
        
    Returns:
        dict: Dicionário com os dados do usuário ou None se não encontrado
    """
    try:
        engine = obter_engine()
        
        query = text("""
            SELECT id, nome, email, telefone, criado_em
            FROM usuarios
            WHERE id = :usuario_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'usuario_id': usuario_id}).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'nome': result[1],
                    'email': result[2],
                    'telefone': result[3],
                    'criado_em': result[4].isoformat() if result[4] else None
                }
        
        return None
        
    except Exception as e:
        return None
