# Módulo de metas
# Responsável por gerenciar metas de economia no MySQL

from sqlalchemy import text
from c_generate_rpa.load import obter_engine
from b_backend.src.usuario_contexto import obter_usuario_id


def _resolver_usuario_id(usuario_id=None):
    if usuario_id is not None:
        return usuario_id

    contexto_usuario_id = obter_usuario_id()
    if contexto_usuario_id is not None:
        return contexto_usuario_id

    raise PermissionError("Usuário não autenticado para consultar dados financeiros")


def buscar_meta_ativa(usuario_id=None):
    """
    Busca a meta ativa no banco de dados.
    
    Returns:
        dict: Dicionário com os dados da meta ativa ou None se não existir
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    engine = obter_engine()
    
    query = """
        SELECT id, titulo, valor_meta, valor_atual, data_limite, status, criado_em, atualizado_em
        FROM metas
        WHERE status = 'ativa' AND usuario_id = :usuario_id
        ORDER BY id DESC
        LIMIT 1
    """
    params = {'usuario_id': usuario_id}

    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchone()
        
        if result:
            return {
                'id': result[0],
                'titulo': result[1],
                'valor_meta': float(result[2]),
                'valor_atual': float(result[3]),
                'data_limite': result[4].isoformat() if result[4] else None,
                'status': result[5],
                'criado_em': result[6].isoformat() if result[6] else None,
                'atualizado_em': result[7].isoformat() if result[7] else None
            }
        return None


def criar_meta(titulo, valor_meta, valor_atual=0.0, data_limite=None, status='ativa', usuario_id=None):
    """
    Cria uma nova meta no banco de dados.
    
    Args:
        titulo (str): Título da meta
        valor_meta (float): Valor da meta
        valor_atual (float): Valor atual (padrão: 0.0)
        data_limite (str): Data limite no formato YYYY-MM-DD (opcional)
        status (str): Status da meta (padrão: 'ativa')
    
    Returns:
        int: ID da meta criada
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    engine = obter_engine()
    
    query = """
        INSERT INTO metas (usuario_id, titulo, valor_meta, valor_atual, data_limite, status)
        VALUES (:usuario_id, :titulo, :valor_meta, :valor_atual, :data_limite, :status)
    """
    params = {
        'usuario_id': usuario_id,
        'titulo': titulo,
        'valor_meta': valor_meta,
        'valor_atual': valor_atual,
        'data_limite': data_limite,
        'status': status
    }

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        conn.commit()
        return result.lastrowid


def atualizar_meta(id_meta, titulo=None, valor_meta=None, valor_atual=None, data_limite=None, status=None, usuario_id=None):
    """
    Atualiza uma meta existente no banco de dados.
    
    Args:
        id_meta (int): ID da meta a ser atualizada
        titulo (str): Novo título (opcional)
        valor_meta (float): Novo valor da meta (opcional)
        valor_atual (float): Novo valor atual (opcional)
        data_limite (str): Nova data limite no formato YYYY-MM-DD (opcional)
        status (str): Novo status (opcional)
    
    Returns:
        bool: True se atualizou com sucesso, False se não encontrou
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    engine = obter_engine()
    
    # Constrói a query dinamicamente apenas com os campos fornecidos
    campos = []
    params = {'id_meta': id_meta}
    
    if titulo is not None:
        campos.append("titulo = :titulo")
        params['titulo'] = titulo
    
    if valor_meta is not None:
        campos.append("valor_meta = :valor_meta")
        params['valor_meta'] = valor_meta
    
    if valor_atual is not None:
        campos.append("valor_atual = :valor_atual")
        params['valor_atual'] = valor_atual
    
    if data_limite is not None:
        campos.append("data_limite = :data_limite")
        params['data_limite'] = data_limite
    
    if status is not None:
        campos.append("status = :status")
        params['status'] = status
    
    if not campos:
        return False
    
    query = f"""
        UPDATE metas
        SET {', '.join(campos)}
        WHERE id = :id_meta AND usuario_id = :usuario_id
    """
    params['usuario_id'] = usuario_id

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        conn.commit()
        return result.rowcount > 0


def excluir_meta(id_meta, usuario_id=None):
    """
    Exclui uma meta do banco de dados.
    
    Args:
        id_meta (int): ID da meta a ser excluída
    
    Returns:
        bool: True se excluiu com sucesso, False se não encontrou
    """
    usuario_id = _resolver_usuario_id(usuario_id)
    engine = obter_engine()
    
    query = """
        DELETE FROM metas
        WHERE id = :id_meta AND usuario_id = :usuario_id
    """
    params = {'id_meta': id_meta, 'usuario_id': usuario_id}

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        conn.commit()
        return result.rowcount > 0
