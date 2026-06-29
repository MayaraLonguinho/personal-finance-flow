# Módulo de transações
# Responsável por buscar e inserir transações do MySQL

import pandas as pd
from sqlalchemy import text
from src.load import obter_engine
from src.categorization import categorizar_transacao
from src.categorias import obter_regras_categorizacao_do_banco, inicializar_categorias_padrao


def buscar_todas_transacoes(filtros=None, usuario_id=None):
    """
    Busca todas as transações da tabela transacoes no MySQL.
    Retorna ordenadas pelas transações mais recentes.
    
    Args:
        filtros (dict): Dicionário com filtros opcionais (descricao, categoria, tipo, status)
        
    Returns:
        pd.DataFrame: DataFrame com todas as transações ordenadas
    """
    # Obtém o engine de conexão
    engine = obter_engine()
    
    # Query base
    query = "SELECT * FROM transacoes WHERE 1=1"
    params = {}
    
    # Adiciona filtros se fornecidos
    if filtros:
        if filtros.get('descricao'):
            query += " AND descricao LIKE :descricao"
            params['descricao'] = f"%{filtros['descricao']}%"
        if filtros.get('categoria'):
            query += " AND categoria = :categoria"
            params['categoria'] = filtros['categoria']
        if filtros.get('tipo'):
            query += " AND tipo = :tipo"
            params['tipo'] = filtros['tipo']
        if filtros.get('status'):
            query += " AND status = :status"
            params['status'] = filtros['status']
    # Filtra pelo usuário se informado
    if usuario_id is not None:
        query += " AND usuario_id = :usuario_id"
        params['usuario_id'] = usuario_id
    
    # Ordena por data_transacao de forma decrescente
    query += " ORDER BY data_transacao DESC"
    
    df = pd.read_sql(text(query), engine, params=params)
    
    return df


def criar_transacao(data_transacao, descricao, categoria, tipo, valor, conta, instituicao, status, usuario_id=None):
    """
    Insere uma nova transação na tabela transacoes do MySQL.
    
    Aplica categorização automática se a categoria estiver vazia ou for "outros".
    
    Args:
        data_transacao (str): Data da transação
        descricao (str): Descrição da transação
        categoria (str): Categoria da transação
        tipo (str): Tipo da transação (entrada, saida, investimento)
        valor (float): Valor da transação
        conta (str): Conta da transação
        instituicao (str): Instituição da transação
        status (str): Status da transação (confirmado, pendente, cancelado)
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        # Inicializa categorias padrão se necessário
        inicializar_categorias_padrao()
        
        # Aplica categorização automática se categoria estiver vazia ou for "outros"
        if not categoria or categoria.lower() == 'outros':
            # Obtém regras de categorização do banco
            regras_categorizacao = obter_regras_categorizacao_do_banco()
            categoria_sugerida, _ = categorizar_transacao(descricao, categoria, regras_categorizacao)
            categoria = categoria_sugerida
        
        # Obtém o engine de conexão
        engine = obter_engine()
        
        # Query SQL parametrizada para inserir transação (usuario_id será fornecido pelo chamador)
        query = text("""
            INSERT INTO transacoes 
            (usuario_id, data_transacao, descricao, categoria, tipo, valor, conta, instituicao, status)
            VALUES (:usuario_id, :data_transacao, :descricao, :categoria, :tipo, :valor, :conta, :instituicao, :status)
        """)
        
        # Executa a query com parâmetros
        if usuario_id is None:
            raise Exception('usuario_id não fornecido para criar_transacao')

        with engine.connect() as conn:
            conn.execute(query, {
                'usuario_id': usuario_id,
                'data_transacao': data_transacao,
                'descricao': descricao,
                'categoria': categoria,
                'tipo': tipo,
                'valor': valor,
                'conta': conta,
                'instituicao': instituicao,
                'status': status
            })
            conn.commit()
        
        return {'sucesso': True, 'mensagem': 'Transação criada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def editar_transacao(id_transacao, data_transacao, descricao, categoria, tipo, valor, conta, instituicao, status, usuario_id=None):
    """
    Edita uma transação existente na tabela transacoes do MySQL.
    
    Args:
        id_transacao (int): ID da transação
        data_transacao (str): Data da transação
        descricao (str): Descrição da transação
        categoria (str): Categoria da transação
        tipo (str): Tipo da transação (entrada, saida, investimento)
        valor (float): Valor da transação
        conta (str): Conta da transação
        instituicao (str): Instituição da transação
        status (str): Status da transação (confirmado, pendente, cancelado)
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        # Obtém o engine de conexão
        engine = obter_engine()
        
        # Query SQL parametrizada para atualizar transação (valida usuário)
        query = text("""
            UPDATE transacoes 
            SET data_transacao = :data_transacao,
                descricao = :descricao,
                categoria = :categoria,
                tipo = :tipo,
                valor = :valor,
                conta = :conta,
                instituicao = :instituicao,
                status = :status
            WHERE id = :id AND usuario_id = :usuario_id
        """)
        
        # Executa a query com parâmetros
        if usuario_id is None:
            raise Exception('usuario_id não fornecido para editar_transacao')

        with engine.connect() as conn:
            resultado = conn.execute(query, {
                'id': id_transacao,
                'usuario_id': usuario_id,
                'data_transacao': data_transacao,
                'descricao': descricao,
                'categoria': categoria,
                'tipo': tipo,
                'valor': valor,
                'conta': conta,
                'instituicao': instituicao,
                'status': status
            })
            conn.commit()
        
        # Verifica se a transação foi encontrada e atualizada
        if resultado.rowcount == 0:
            return {'sucesso': False, 'erro': 'Transação não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Transação atualizada com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}


def excluir_transacao(id_transacao, usuario_id=None):
    """
    Exclui uma transação da tabela transacoes do MySQL.
    
    Args:
        id_transacao (int): ID da transação
        
    Returns:
        dict: Dicionário com sucesso ou erro
    """
    try:
        # Obtém o engine de conexão
        engine = obter_engine()
        
        # Query SQL parametrizada para excluir transação (valida usuário)
        query = text("DELETE FROM transacoes WHERE id = :id AND usuario_id = :usuario_id")

        if usuario_id is None:
            raise Exception('usuario_id não fornecido para excluir_transacao')

        # Executa a query com parâmetros
        with engine.connect() as conn:
            resultado = conn.execute(query, {'id': id_transacao, 'usuario_id': usuario_id})
            conn.commit()
        
        # Verifica se a transação foi encontrada e excluída
        if resultado.rowcount == 0:
            return {'sucesso': False, 'erro': 'Transação não encontrada'}
        
        return {'sucesso': True, 'mensagem': 'Transação excluída com sucesso'}
        
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}
