# Módulo de categorias
# Responsável por CRUD de categorias no MySQL

import json
from src.load import obter_engine
from sqlalchemy import text


def buscar_todas_categorias():
    """
    Busca todas as categorias da tabela categorias no MySQL.
    
    Returns:
        list: Lista de dicionários com as categorias
    """
    try:
        engine = obter_engine()
        
        query = text("SELECT * FROM categorias ORDER BY nome")
        
        with engine.connect() as conn:
            result = conn.execute(query)
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


def buscar_categoria_por_nome(nome):
    """
    Busca uma categoria pelo nome.
    
    Args:
        nome (str): Nome da categoria
        
    Returns:
        dict: Dicionário com a categoria ou None se não encontrada
    """
    try:
        engine = obter_engine()
        
        query = text("SELECT * FROM categorias WHERE nome = :nome")
        
        with engine.connect() as conn:
            result = conn.execute(query, {'nome': nome})
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


def criar_categoria(nome, palavras_chave=None, cor=None):
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
        engine = obter_engine()
        
        # Converte lista de palavras-chave para JSON
        palavras_chave_json = json.dumps(palavras_chave) if palavras_chave else None
        
        query = text("""
            INSERT INTO categorias (nome, palavras_chave, cor)
            VALUES (:nome, :palavras_chave, :cor)
        """)
        
        with engine.connect() as conn:
            conn.execute(query, {
                'nome': nome,
                'palavras_chave': palavras_chave_json,
                'cor': cor
            })
            conn.commit()
        
        return {'sucesso': True, 'mensagem': 'Categoria criada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def atualizar_categoria(nome_atual, novo_nome=None, palavras_chave=None, cor=None):
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
            WHERE nome = :nome_atual
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            conn.commit()
        
        if result.rowcount == 0:
            return {'sucesso': False, 'erro': 'Categoria não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Categoria atualizada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def excluir_categoria(nome):
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
        
        engine = obter_engine()
        
        # Primeiro, move transações dessa categoria para 'outros'
        query_update = text("""
            UPDATE transacoes 
            SET categoria = 'outros'
            WHERE categoria = :nome
        """)
        
        with engine.connect() as conn:
            conn.execute(query_update, {'nome': nome})
        
        # Depois, exclui a categoria
        query_delete = text("DELETE FROM categorias WHERE nome = :nome")
        
        with engine.connect() as conn:
            result = conn.execute(query_delete, {'nome': nome})
            conn.commit()
        
        if result.rowcount == 0:
            return {'sucesso': False, 'erro': 'Categoria não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Categoria excluída com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def obter_regras_categorizacao_do_banco():
    """
    Obtém as regras de categorização do banco de dados.
    
    Returns:
        dict: Dicionário com categorias e palavras-chave
    """
    try:
        categorias = buscar_todas_categorias()
        
        regras = {}
        for categoria in categorias:
            regras[categoria['nome']] = categoria['palavras_chave']
        
        return regras
        
    except Exception as e:
        return {}


def inicializar_categorias_padrao():
    """
    Inicializa as categorias padrão se ainda não existirem no banco.
    
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        from src.categorization import obter_regras_categorizacao
        
        regras_padrao = obter_regras_categorizacao()
        
        for nome, palavras_chave in regras_padrao.items():
            # Verifica se a categoria já existe
            categoria_existente = buscar_categoria_por_nome(nome)
            
            if not categoria_existente:
                # Cria a categoria
                resultado = criar_categoria(nome, palavras_chave)
                if not resultado['sucesso']:
                    return resultado
        
        return {'sucesso': True, 'mensagem': 'Categorias padrão inicializadas com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def obter_estatisticas_categoria(nome):
    """
    Obtém estatísticas de uma categoria (quantidade de transações e valor total).
    
    Args:
        nome (str): Nome da categoria
        
    Returns:
        dict: Dicionário com quantidade e valor total
    """
    try:
        engine = obter_engine()
        
        query = text("""
            SELECT 
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM transacoes
            WHERE categoria = :nome
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'nome': nome})
            row = result.fetchone()
            
            return {
                'quantidade': row.quantidade if row.quantidade else 0,
                'valor_total': float(row.valor_total) if row.valor_total else 0.0
            }
        
    except Exception as e:
        return {'quantidade': 0, 'valor_total': 0.0}
