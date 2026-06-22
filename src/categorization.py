# Módulo de categorização automática
# Responsável por categorizar transações baseadas na descrição

import unicodedata
import json


def normalizar_descricao(descricao):
    """
    Normaliza a descrição para comparação.
    
    Converte para minúsculas, remove espaços extras e trata acentos.
    
    Args:
        descricao (str): Descrição original
        
    Returns:
        str: Descrição normalizada ou None se a descrição for None/vazia
    """
    if descricao is None:
        return None
    
    if not isinstance(descricao, str):
        descricao = str(descricao)
    
    # Converte para minúsculas
    descricao = descricao.lower()
    
    # Remove espaços extras (inclusive entre palavras)
    descricao = ' '.join(descricao.split())
    
    # Remove acentos
    descricao = unicodedata.normalize('NFKD', descricao)
    descricao = ''.join([c for c in descricao if not unicodedata.combining(c)])
    
    return descricao


def obter_regras_categorizacao():
    """
    Retorna as regras de categorização padrão.
    
    Esta função é usada como fallback quando não há categorias no banco.
    
    Returns:
        dict: Dicionário com categorias e palavras-chave
    """
    return {
        'transporte': ['uber', '99', 'ônibus', 'onibus', 'metro', 'metrô', 'combustível', 'combustivel', 'gasolina', 'postos', 'taxi'],
        'alimentação': ['ifood', 'restaurante', 'mercado', 'padaria', 'supermercado', 'lanchonete', 'café', 'cafe', 'bar', 'pizzaria'],
        'lazer': ['netflix', 'spotify', 'cinema', 'steam', 'jogos', 'teatro', 'show', 'concerto', 'parque', 'viagem'],
        'saúde': ['farmácia', 'farmacia', 'hospital', 'consulta', 'academia', 'médico', 'medico', 'dentista', 'remédio', 'remedio'],
        'casa': ['aluguel', 'condomínio', 'condominio', 'energia', 'água', 'agua', 'internet', 'gás', 'gas', 'luz', 'telefone'],
        'salário': ['salário', 'salario', 'pagamento', 'freelance', 'honorários', 'honorarios', 'proventos'],
        'investimentos': ['tesouro', 'cdb', 'fundo', 'ações', 'acoes', 'renda', 'aplicação', 'aplicacao', 'bolsa'],
        'outros': []
    }


def categorizar_transacao(descricao, categoria_atual=None, regras_categorizacao=None):
    """
    Categoriza automaticamente uma transação baseada na descrição.
    
    Preserva a categoria atual se já estiver preenchida e diferente de "outros".
    
    Args:
        descricao (str): Descrição da transação
        categoria_atual (str): Categoria atual da transação (opcional)
        regras_categorizacao (dict): Regras de categorização (opcional, usa padrão se não fornecido)
        
    Returns:
        tuple: (categoria_sugerida, foi_categorizada)
            - categoria_sugerida: Categoria sugerida ou categoria atual se preservada
            - foi_categorizada: True se a categorização automática foi aplicada
    """
    # Se a categoria atual já estiver preenchida e não for "outros", preservar
    if categoria_atual and categoria_atual.lower() != 'outros':
        return categoria_atual, False
    
    # Usa regras fornecidas ou regras padrão
    if regras_categorizacao is None:
        regras_categorizacao = obter_regras_categorizacao()
    
    # Normalizar a descrição
    descricao_normalizada = normalizar_descricao(descricao)
    
    if not descricao_normalizada:
        return 'outros', False
    
    # Verificar cada regra
    for categoria, palavras_chave in regras_categorizacao.items():
        if palavras_chave:  # Verifica se a lista não está vazia
            for palavra in palavras_chave:
                if palavra in descricao_normalizada:
                    return categoria, True
    
    # Se nenhuma regra corresponder, retornar "outros" (categorização foi aplicada)
    return 'outros', True


def categorizar_dataframe(df, regras_categorizacao=None):
    """
    Aplica a categorização automática em um DataFrame de transações.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'descricao' e 'categoria'
        regras_categorizacao (dict): Regras de categorização (opcional, usa padrão se não fornecido)
        
    Returns:
        tuple: (df_categorizado, contador)
            - df_categorizado: DataFrame com categorias aplicadas
            - contador: Número de transações categorizadas automaticamente
    """
    contador = 0
    
    # Verificar se as colunas existem
    if 'descricao' not in df.columns or 'categoria' not in df.columns:
        return df, 0
    
    # Usa regras fornecidas ou regras padrão
    if regras_categorizacao is None:
        regras_categorizacao = obter_regras_categorizacao()
    
    # Aplicar categorização em cada linha
    for index, row in df.iterrows():
        descricao = row['descricao']
        categoria_atual = row['categoria']
        
        # Se categoria atual for NaN, tratar como None
        if pd.isna(categoria_atual):
            categoria_atual = None
        
        categoria_sugerida, foi_categorizada = categorizar_transacao(
            descricao, 
            categoria_atual, 
            regras_categorizacao
        )
        
        if foi_categorizada:
            df.at[index, 'categoria'] = categoria_sugerida
            contador += 1
    
    return df, contador
