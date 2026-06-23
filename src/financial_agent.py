# Módulo de Agent Financeiro
# Responsável por responder perguntas sobre finanças pessoais

import unicodedata
from src.metrics import (
    calcular_resumo_financeiro,
    calcular_gastos_por_categoria,
    buscar_ultimas_transacoes,
    gerar_insights
)
from src.metas import buscar_meta_ativa
from src.categorias import buscar_todas_categorias
from src.utils import formatar_moeda


# Palavras-chave para reconhecimento de intenções
INTENCOES = {
    "saldo": [
        "saldo", "sobrou", "restou", "positivo", "negativo", "zerado",
        "quanto tenho", "minha situação", "estou no positivo", "estou no negativo"
    ],
    "entradas": [
        "recebi", "recebido", "entrou", "entradas", "entrada", "ganhei",
        "ganho", "renda", "rendimentos", "total de entradas", "quanto recebi"
    ],
    "saidas": [
        "gastei", "gasto", "gastos", "saídas", "saida", "despesas", "despesa",
        "saiu", "sair", "gastar", "paguei", "pagamento", "total de despesas"
    ],
    "categorias": [
        "categoria", "categorias", "maior gasto", "maior despesa", "gastei com",
        "gastar com", "quanto gastei com", "qual categoria", "categoria de gasto"
    ],
    "investimentos": [
        "investi", "investido", "investimento", "investimentos", "aplicação",
        "aplicações", "tenho investimentos", "quanto investi"
    ],
    "metas": [
        "meta", "metas", "objetivo", "objetivos", "economia", "poupar",
        "falta para", "percentual da meta", "como está minha meta", "atingir minha meta"
    ],
    "transacoes": [
        "transações", "transacao", "transação", "movimentações", "movimentação",
        "quantas transações", "última transação", "últimas movimentações",
        "minhas transações", "quantidade de transações"
    ],
    "resumo": [
        "resumo", "análise", "como estão minhas finanças", "faça um resumo",
        "me dê uma análise", "situação geral", "panorama", "visão geral"
    ]
}


def normalizar_texto(texto):
    """
    Normaliza o texto para comparação: minúsculas e sem acentos.
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    # Converte para minúsculas
    texto = texto.lower()
    
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    
    return texto


def normalizar_texto_sem_pontuacao(texto):
    """
    Normaliza o texto e remove pontuação para comparação de palavras.
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado sem pontuação
    """
    import string
    # Converte para minúsculas
    texto = texto.lower()
    
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    
    # Remove pontuação
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    
    return texto


def identificar_intencao(pergunta):
    """
    Identifica a intenção da pergunta baseada em palavras-chave.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        str: Intenção identificada ou None
    """
    pergunta_normalizada = normalizar_texto(pergunta)
    
    for intencao, palavras_chave in INTENCOES.items():
        for palavra in palavras_chave:
            if palavra in pergunta_normalizada:
                return intencao
    
    return None


def extrair_categoria_mencionada(pergunta):
    """
    Extrai o nome de uma categoria mencionada na pergunta.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        str: Nome da categoria ou None
    """
    try:
        categorias = buscar_todas_categorias()
        pergunta_normalizada = normalizar_texto(pergunta)
        
        for categoria in categorias:
            nome_categoria = normalizar_texto(categoria['nome'])
            if nome_categoria in pergunta_normalizada:
                return categoria['nome']
        
        return None
    except Exception as e:
        print(f"Erro ao extrair categoria: {e}")
        return None


def extrair_grupo_categoria_mencionada(pergunta):
    """
    Extrai o nome de uma categoria mencionada na pergunta, verificando
    tanto o nome quanto as palavras-chave.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        str: Nome da categoria ou None
    """
    try:
        categorias = buscar_todas_categorias()
        pergunta_normalizada = normalizar_texto_sem_pontuacao(pergunta)
        
        # Divide a pergunta em palavras para correspondência mais precisa
        palavras_pergunta = pergunta_normalizada.split()
        
        for categoria in categorias:
            # Verifica pelo nome (correspondência exata de palavra)
            nome_categoria = normalizar_texto(categoria['nome'])
            if nome_categoria in palavras_pergunta:
                return categoria['nome']
            
            # Verifica pelas palavras-chave (correspondência exata de palavra)
            palavras_chave = categoria.get('palavras_chave', [])
            for palavra in palavras_chave:
                palavra_normalizada = normalizar_texto(palavra)
                if palavra_normalizada in palavras_pergunta:
                    return categoria['nome']
        
        return None
    except Exception as e:
        print(f"Erro ao extrair grupo de categoria: {e}")
        return None


def responder_categorias_especifica(categoria):
    """
    Responde perguntas sobre uma categoria específica.
    
    Args:
        categoria (str): Nome da categoria
        
    Returns:
        dict: Resposta formatada
    """
    try:
        from src.categorias import obter_estatisticas_categoria
        
        estatisticas = obter_estatisticas_categoria(categoria)
        
        if estatisticas['quantidade'] == 0:
            return {
                "resposta": f"Não há gastos registrados com {categoria}.",
                "tipo": "categoria_especifica",
                "dados": {"categoria": categoria, "valor": 0}
            }
        
        valor = float(estatisticas['valor_total'])
        resposta = f"Você gastou {formatar_moeda(valor)} com {categoria}."
        
        return {
            "resposta": resposta,
            "tipo": "categoria_especifica",
            "dados": {"categoria": categoria, "valor": valor}
        }
    except Exception as e:
        print(f"Erro ao consultar categoria específica: {e}")
        return {
            "resposta": f"Erro ao consultar gastos com {categoria}.",
            "tipo": "erro",
            "dados": {}
        }


def responder_saldo():
    """
    Responde perguntas sobre saldo.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        resumo = calcular_resumo_financeiro()
        saldo = resumo['saldo_final']
        
        if saldo > 0:
            resposta = f"Seu saldo atual é positivo em {formatar_moeda(saldo)}."
            tipo = "positivo"
        elif saldo < 0:
            resposta = f"Seu saldo atual é negativo em {formatar_moeda(saldo)}."
            tipo = "negativo"
        else:
            resposta = "Seu saldo está zerado."
            tipo = "neutro"
        
        return {
            "resposta": resposta,
            "tipo": tipo,
            "dados": {"saldo": saldo}
        }
    except Exception as e:
        print(f"Erro ao calcular saldo: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para calcular o saldo.",
            "tipo": "erro",
            "dados": {}
        }


def responder_entradas():
    """
    Responde perguntas sobre entradas.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        resumo = calcular_resumo_financeiro()
        total_entradas = resumo['total_entradas']
        
        if total_entradas > 0:
            resposta = f"O total de entradas é {formatar_moeda(total_entradas)}."
        else:
            resposta = "Não há entradas registradas."
        
        return {
            "resposta": resposta,
            "tipo": "entradas",
            "dados": {"total_entradas": total_entradas}
        }
    except Exception as e:
        print(f"Erro ao calcular entradas: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para calcular as entradas.",
            "tipo": "erro",
            "dados": {}
        }


def responder_saidas():
    """
    Responde perguntas sobre saídas.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        resumo = calcular_resumo_financeiro()
        total_saidas = resumo['total_saidas']
        
        if total_saidas > 0:
            resposta = f"O total de saídas é {formatar_moeda(total_saidas)}."
        else:
            resposta = "Não há saídas registradas."
        
        return {
            "resposta": resposta,
            "tipo": "saidas",
            "dados": {"total_saidas": total_saidas}
        }
    except Exception as e:
        print(f"Erro ao calcular saídas: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para calcular as saídas.",
            "tipo": "erro",
            "dados": {}
        }


def responder_categorias(pergunta):
    """
    Responde perguntas sobre categorias.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        dict: Resposta formatada
    """
    try:
        categoria_mencionada = extrair_categoria_mencionada(pergunta)
        
        if categoria_mencionada:
            # Pergunta sobre uma categoria específica
            gastos_categoria = calcular_gastos_por_categoria()
            categoria_gasto = gastos_categoria[gastos_categoria['categoria'] == categoria_mencionada]
            
            if not categoria_gasto.empty:
                valor = categoria_gasto.iloc[0]['valor']
                resposta = f"Você gastou {formatar_moeda(valor)} com {categoria_mencionada}."
                return {
                    "resposta": resposta,
                    "tipo": "categoria_especifica",
                    "dados": {"categoria": categoria_mencionada, "valor": valor}
                }
            else:
                resposta = f"Não há gastos registrados com {categoria_mencionada}."
                return {
                    "resposta": resposta,
                    "tipo": "categoria_especifica",
                    "dados": {"categoria": categoria_mencionada, "valor": 0}
                }
        else:
            # Pergunta sobre a maior categoria
            gastos_categoria = calcular_gastos_por_categoria()
            
            if gastos_categoria.empty:
                return {
                    "resposta": "Não há gastos registrados por categoria.",
                    "tipo": "categoria",
                    "dados": {}
                }
            
            maior_gasto = gastos_categoria.loc[gastos_categoria['valor'].idxmax()]
            resposta = f"Sua maior categoria de gastos foi {maior_gasto['categoria']}, com {formatar_moeda(maior_gasto['valor'])}."
            
            return {
                "resposta": resposta,
                "tipo": "categoria",
                "dados": {"categoria": maior_gasto['categoria'], "valor": maior_gasto['valor']}
            }
    except Exception as e:
        print(f"Erro ao calcular categorias: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para analisar categorias.",
            "tipo": "erro",
            "dados": {}
        }


def responder_investimentos():
    """
    Responde perguntas sobre investimentos.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        resumo = calcular_resumo_financeiro()
        total_investido = resumo['total_investido']
        
        if total_investido > 0:
            resposta = f"Você tem {formatar_moeda(total_investido)} em investimentos registrados."
        else:
            resposta = "Nenhum investimento foi registrado."
        
        return {
            "resposta": resposta,
            "tipo": "investimentos",
            "dados": {"total_investido": total_investido}
        }
    except Exception as e:
        print(f"Erro ao calcular investimentos: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para analisar investimentos.",
            "tipo": "erro",
            "dados": {}
        }


def responder_metas():
    """
    Responde perguntas sobre metas.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        meta = buscar_meta_ativa()
        
        if not meta:
            return {
                "resposta": "Você ainda não possui uma meta financeira ativa.",
                "tipo": "metas",
                "dados": {}
            }
        
        valor_meta = meta['valor_meta']
        valor_atual = meta['valor_atual']
        titulo = meta['titulo']
        
        if valor_meta > 0:
            percentual = (valor_atual / valor_meta) * 100
            falta = valor_meta - valor_atual
            
            if falta > 0:
                resposta = f"Sua meta '{titulo}' está {percentual:.0f}% concluída. Faltam {formatar_moeda(falta)} para atingir {formatar_moeda(valor_meta)}."
            else:
                resposta = f"Parabéns! Você atingiu sua meta '{titulo}' com {formatar_moeda(valor_atual)}!"
        else:
            resposta = f"Sua meta '{titulo}' tem valor atual de {formatar_moeda(valor_atual)}."
        
        return {
            "resposta": resposta,
            "tipo": "metas",
            "dados": {
                "titulo": titulo,
                "valor_meta": valor_meta,
                "valor_atual": valor_atual,
                "percentual": percentual if valor_meta > 0 else 0
            }
        }
    except Exception as e:
        print(f"Erro ao buscar metas: {e}")
        return {
            "resposta": "Erro ao buscar informações da meta.",
            "tipo": "erro",
            "dados": {}
        }


def responder_transacoes(pergunta):
    """
    Responde perguntas sobre transações.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        dict: Resposta formatada
    """
    try:
        pergunta_normalizada = normalizar_texto(pergunta)
        
        # Verifica se pergunta sobre quantidade
        if "quantas" in pergunta_normalizada or "quantidade" in pergunta_normalizada:
            resumo = calcular_resumo_financeiro()
            qtd = resumo['qtd_transacoes']
            resposta = f"Você tem {qtd} transações registradas."
            return {
                "resposta": resposta,
                "tipo": "transacoes_quantidade",
                "dados": {"quantidade": qtd}
            }
        
        # Verifica se pergunta sobre última transação
        if "última" in pergunta_normalizada or "ultima" in pergunta_normalizada:
            ultimas = buscar_ultimas_transacoes(limite=1)
            
            if ultimas:
                ultima = ultimas[0]
                resposta = f"Sua última transação foi {ultima['descricao']} de {formatar_moeda(ultima['valor'])} em {ultima['data_transacao']}."
                return {
                    "resposta": resposta,
                    "tipo": "transacao_ultima",
                    "dados": ultima
                }
            else:
                return {
                    "resposta": "Não há transações registradas.",
                    "tipo": "transacao_ultima",
                    "dados": {}
                }
        
        # Verifica se pergunta sobre últimas transações
        if "últimas" in pergunta_normalizada or "ultimas" in pergunta_normalizada:
            ultimas = buscar_ultimas_transacoes(limite=5)
            
            if ultimas:
                resposta = "Suas últimas transações foram:\n"
                for t in ultimas:
                    resposta += f"- {t['descricao']}: {formatar_moeda(t['valor'])} em {t['data_transacao']}\n"
                return {
                    "resposta": resposta.strip(),
                    "tipo": "transacoes_ultimas",
                    "dados": {"transacoes": ultimas}
                }
            else:
                return {
                    "resposta": "Não há transações registradas.",
                    "tipo": "transacoes_ultimas",
                    "dados": {}
                }
        
        # Padrão: quantidade de transações
        resumo = calcular_resumo_financeiro()
        qtd = resumo['qtd_transacoes']
        resposta = f"Você tem {qtd} transações registradas."
        return {
            "resposta": resposta,
            "tipo": "transacoes_quantidade",
            "dados": {"quantidade": qtd}
        }
    except Exception as e:
        print(f"Erro ao buscar transações: {e}")
        return {
            "resposta": "Ainda não existem transações registradas.",
            "tipo": "erro",
            "dados": {}
        }


def responder_resumo():
    """
    Responde perguntas de resumo geral.
    
    Returns:
        dict: Resposta formatada
    """
    try:
        resumo = calcular_resumo_financeiro()
        gastos_categoria = calcular_gastos_por_categoria()
        meta = buscar_meta_ativa()
        
        partes = []
        
        # Entradas
        if resumo['total_entradas'] > 0:
            partes.append(f"Você recebeu {formatar_moeda(resumo['total_entradas'])}.")
        
        # Saídas
        if resumo['total_saidas'] > 0:
            partes.append(f"Você gastou {formatar_moeda(resumo['total_saidas'])}.")
        
        # Saldo
        saldo = resumo['saldo_final']
        if saldo > 0:
            partes.append(f"Seu saldo é positivo em {formatar_moeda(saldo)}.")
        elif saldo < 0:
            partes.append(f"Seu saldo é negativo em {formatar_moeda(saldo)}.")
        
        # Maior categoria
        if not gastos_categoria.empty:
            maior_gasto = gastos_categoria.loc[gastos_categoria['valor'].idxmax()]
            partes.append(f"Sua maior categoria de gastos foi {maior_gasto['categoria']} com {formatar_moeda(maior_gasto['valor'])}.")
        
        # Investimentos
        if resumo['total_investido'] > 0:
            partes.append(f"Você tem {formatar_moeda(resumo['total_investido'])} em investimentos.")
        
        # Meta
        if meta:
            valor_meta = meta['valor_meta']
            valor_atual = meta['valor_atual']
            if valor_meta > 0:
                percentual = (valor_atual / valor_meta) * 100
                partes.append(f"Sua meta '{meta['titulo']}' está {percentual:.0f}% concluída.")
        
        if not partes:
            return {
                "resposta": "Ainda não existem transações suficientes para realizar essa análise.",
                "tipo": "resumo",
                "dados": {}
            }
        
        resposta = " ".join(partes)
        
        return {
            "resposta": resposta,
            "tipo": "resumo",
            "dados": {
                "resumo_financeiro": resumo,
                "meta": meta
            }
        }
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")
        return {
            "resposta": "Ainda não existem transações suficientes para realizar essa análise.",
            "tipo": "erro",
            "dados": {}
        }


def responder_pergunta(pergunta):
    """
    Função principal que processa a pergunta e retorna a resposta.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        dict: Resposta formatada com campos 'resposta', 'tipo' e 'dados'
    """
    print(f"[Agent] Processando pergunta: {pergunta}")
    
    # Validação básica
    if not pergunta or not pergunta.strip():
        return {
            "resposta": "Por favor, digite uma pergunta.",
            "tipo": "erro",
            "dados": {}
        }
    
    if len(pergunta) > 500:
        return {
            "resposta": "A pergunta é muito longa. Por favor, seja mais conciso.",
            "tipo": "erro",
            "dados": {}
        }
    
    # Verifica primeiro se há uma categoria mencionada (prioridade sobre saidas gerais)
    categoria_mencionada = extrair_grupo_categoria_mencionada(pergunta)
    
    if categoria_mencionada:
        print(f"[Agent] Categoria mencionada: {categoria_mencionada}")
        # Usa a função de categorias para responder
        return responder_categorias_especifica(categoria_mencionada)
    
    # Identifica a intenção
    intencao = identificar_intencao(pergunta)
    
    print(f"[Agent] Intenção identificada: {intencao}")
    
    # Processa de acordo com a intenção
    if intencao == "saldo":
        return responder_saldo()
    elif intencao == "entradas":
        return responder_entradas()
    elif intencao == "saidas":
        return responder_saidas()
    elif intencao == "categorias":
        return responder_categorias(pergunta)
    elif intencao == "investimentos":
        return responder_investimentos()
    elif intencao == "metas":
        return responder_metas()
    elif intencao == "transacoes":
        return responder_transacoes(pergunta)
    elif intencao == "resumo":
        return responder_resumo()
    else:
        # Intenção não reconhecida
        return {
            "resposta": "Não consegui identificar exatamente o que você deseja consultar. Você pode perguntar sobre saldo, entradas, saídas, categorias, investimentos, metas ou últimas transações.",
            "tipo": "desconhecido",
            "dados": {}
        }
