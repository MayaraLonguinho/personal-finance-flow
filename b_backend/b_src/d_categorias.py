# Módulo de categorias
# Responsável por CRUD de categorias no MySQL

import json
from c_generate_rpa.d_load import obter_engine
from sqlalchemy import text
from b_backend.b_src.b_usuario_contexto import obter_usuario_id


def _resolver_usuario_id(usuario_id=None):
    if usuario_id is not None:
        return usuario_id

    contexto_usuario_id = obter_usuario_id()
    if contexto_usuario_id is not None:
        return contexto_usuario_id

    raise PermissionError("Usuário não autenticado para consultar dados financeiros")


def buscar_todas_categorias(usuario_id=None):
    """
    Busca todas as categorias da tabela categorias no MySQL.
    
    Returns:
        list: Lista de dicionários com as categorias
    """
    try:
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        query = text("SELECT * FROM categorias WHERE usuario_id = :usuario_id ORDER BY nome")
        params = {'usuario_id': usuario_id}
        
        with engine.connect() as conn:
            result = conn.execute(query, params) if 'params' in locals() else conn.execute(query)
            categorias = []
            for row in result:
                categoria = {
                    'id': row.id,
                    'nome': row.nome,
                    'palavras_chave': json.loads(row.palavras_chave) if row.palavras_chave else [],
                    'cor': row.cor,
                    'criado_em': row.criado_em.isoformat() if row.criado_em else None,
                    'atualizado_em': row.atualizado_em.isoformat() if row.atualizado_em else None
                }
                categorias.append(categoria)
        
        return categorias
        
    except Exception as e:
        return []


def buscar_categoria_por_nome(nome, usuario_id=None):
    """
    Busca uma categoria pelo nome.
    
    Args:
        nome (str): Nome da categoria
        
    Returns:
        dict: Dicionário com a categoria ou None se não encontrada
    """
    try:
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        query = text("SELECT * FROM categorias WHERE nome = :nome AND usuario_id = :usuario_id")
        params = {'nome': nome, 'usuario_id': usuario_id}

        with engine.connect() as conn:
            result = conn.execute(query, params)
            row = result.fetchone()
            
            if row:
                return {
                    'id': row.id,
                    'nome': row.nome,
                    'palavras_chave': json.loads(row.palavras_chave) if row.palavras_chave else [],
                    'cor': row.cor,
                    'criado_em': row.criado_em.isoformat() if row.criado_em else None,
                    'atualizado_em': row.atualizado_em.isoformat() if row.atualizado_em else None
                }
        
        return None
        
    except Exception as e:
        return None


def criar_categoria(nome, palavras_chave=None, cor=None, usuario_id=None):
    """
    Cria uma nova categoria na tabela categorias do MySQL.
    
    Args:
        nome (str): Nome da categoria
        palavras_chave (list): Lista de palavras-chave
        cor (str): Cor da categoria (opcional)
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        # Converte lista de palavras-chave para JSON
        palavras_chave_json = json.dumps(palavras_chave) if palavras_chave else None
        
        query = text("""
            INSERT INTO categorias (usuario_id, nome, palavras_chave, cor)
            VALUES (:usuario_id, :nome, :palavras_chave, :cor)
        """)
        params = {
            'usuario_id': usuario_id,
            'nome': nome,
            'palavras_chave': palavras_chave_json,
            'cor': cor
        }
        
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        
        return {'sucesso': True, 'mensagem': 'Categoria criada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def atualizar_categoria(nome_atual, novo_nome=None, palavras_chave=None, cor=None, usuario_id=None):
    """
    Atualiza uma categoria existente na tabela categorias do MySQL.
    
    Args:
        nome_atual (str): Nome atual da categoria
        novo_nome (str): Novo nome da categoria (opcional)
        palavras_chave (list): Nova lista de palavras-chave (opcional)
        cor (str): Nova cor da categoria (opcional)
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        # Constrói a query dinamicamente
        set_clauses = []
        params = {'nome_atual': nome_atual}
        
        if novo_nome:
            set_clauses.append("nome = :novo_nome")
            params['novo_nome'] = novo_nome
        
        if palavras_chave is not None:
            set_clauses.append("palavras_chave = :palavras_chave")
            params['palavras_chave'] = json.dumps(palavras_chave)
        
        if cor is not None:
            set_clauses.append("cor = :cor")
            params['cor'] = cor
        
        if not set_clauses:
            return {'sucesso': False, 'erro': 'Nenhum campo para atualizar'}
        
        query = f"""
            UPDATE categorias 
            SET {', '.join(set_clauses)}
            WHERE nome = :nome_atual AND usuario_id = :usuario_id
        """
        params['usuario_id'] = usuario_id
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            conn.commit()
        
        if result.rowcount == 0:
            return {'sucesso': False, 'erro': 'Categoria não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Categoria atualizada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def excluir_categoria(nome, usuario_id=None):
    """
    Exclui uma categoria da tabela categorias do MySQL.
    Move transações dessa categoria para 'outros'.
    Não permite excluir a categoria 'outros'.
    
    Args:
        nome (str): Nome da categoria
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        # Não permitir excluir 'outros'
        if nome.lower() == 'outros':
            return {'sucesso': False, 'erro': 'Não é permitido excluir a categoria "outros"'}
        
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        # Primeiro, move transações dessa categoria para 'outros'
        query_update = text("""
            UPDATE transacoes 
            SET categoria = 'outros'
            WHERE categoria = :nome AND usuario_id = :usuario_id
        """)
        params_update = {'nome': nome, 'usuario_id': usuario_id}
        
        with engine.connect() as conn:
            conn.execute(query_update, params_update)
        
        # Depois, exclui a categoria
        query_delete = text("DELETE FROM categorias WHERE nome = :nome AND usuario_id = :usuario_id")
        params_delete = {'nome': nome, 'usuario_id': usuario_id}

        with engine.connect() as conn:
            result = conn.execute(query_delete, params_delete)
            conn.commit()
        
        if result.rowcount == 0:
            return {'sucesso': False, 'erro': 'Categoria não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Categoria excluída com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def obter_regras_categorizacao_do_banco(usuario_id=None):
    """
    Obtém as regras de categorização do banco de dados.
    
    Returns:
        dict: Dicionário com categorias e palavras-chave
    """
    try:
        categorias = buscar_todas_categorias(usuario_id=usuario_id)
        
        regras = {}
        for categoria in categorias:
            regras[categoria['nome']] = categoria['palavras_chave']
        
        return regras
        
    except Exception as e:
        return {}


def inicializar_categorias_padrao(usuario_id=None):
    """
    Inicializa as categorias padrão se ainda não existirem no banco.
    
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        from c_generate_rpa.c_categorization import obter_regras_categorizacao
        
        regras_padrao = obter_regras_categorizacao()
        
        for nome, palavras_chave in regras_padrao.items():
            # Verifica se a categoria já existe
            categoria_existente = buscar_categoria_por_nome(nome, usuario_id=usuario_id)
            
            if not categoria_existente:
                # Cria a categoria
                resultado = criar_categoria(nome, palavras_chave, usuario_id=usuario_id)
                if not resultado['sucesso']:
                    return resultado
        
        return {'sucesso': True, 'mensagem': 'Categorias padrão inicializadas com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def obter_estatisticas_categoria(nome, usuario_id=None):
    """
    Obtém estatísticas de uma categoria (quantidade de transações e valor total).
    
    Args:
        nome (str): Nome da categoria
        
    Returns:
        dict: Dicionário com quantidade e valor total
    """
    try:
        usuario_id = _resolver_usuario_id(usuario_id)
        engine = obter_engine()
        
        query = text("""
            SELECT 
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM transacoes
            WHERE categoria = :nome AND usuario_id = :usuario_id
        """)
        params = {'nome': nome, 'usuario_id': usuario_id}

        with engine.connect() as conn:
            result = conn.execute(query, params)
            row = result.fetchone()
            
            return {
                'quantidade': row.quantidade if row.quantidade else 0,
                'valor_total': float(row.valor_total) if row.valor_total else 0.0
            }
        
    except Exception as e:
        return {'quantidade': 0, 'valor_total': 0.0}
