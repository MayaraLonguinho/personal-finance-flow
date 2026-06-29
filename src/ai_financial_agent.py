# Módulo de Agent Financeiro com OpenAI
# Responsável por processar perguntas usando OpenAI Responses API com function calling

import os
import unicodedata
from typing import Dict, List, Any, Optional
from openai import OpenAI

from src.metrics import (
    calcular_resumo_financeiro,
    calcular_gastos_por_categoria,
    buscar_ultimas_transacoes
)
from src.metas import buscar_meta_ativa
from src.categorias import buscar_todas_categorias, obter_estatisticas_categoria
from src.usuario_contexto import obter_usuario_id
from src.configuracoes import obter_configuracoes_usuario


# Configuração do cliente OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"[AI Agent] Erro ao inicializar cliente OpenAI: {e}")
        client = None


# ==========================
# FUNÇÕES DE CONSULTA (FERRAMENTAS)
# ==========================

def _obter_usuario_id_da_sessao() -> Optional[int]:
    usuario_id = obter_usuario_id()
    if usuario_id is None:
        raise PermissionError("Usuário não autenticado para consultar dados financeiros")
    return usuario_id


def consultar_saldo() -> Dict[str, Any]:
    """
    Consulta o saldo atual (entradas - saídas - investimentos).
    
    Returns:
        dict: Dicionário com saldo e detalhes
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        return {
            "saldo": float(resumo['saldo_final']),
            "entradas": float(resumo['total_entradas']),
            "saidas": float(resumo['total_saidas']),
            "investimentos": float(resumo['total_investido'])
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar saldo: {e}")
        return {"erro": "Erro ao consultar saldo"}


def consultar_total_entradas() -> Dict[str, Any]:
    """
    Consulta o total de entradas registradas.
    
    Returns:
        dict: Dicionário com total de entradas
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        return {
            "total_entradas": float(resumo['total_entradas'])
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar entradas: {e}")
        return {"erro": "Erro ao consultar entradas"}


def consultar_total_saidas() -> Dict[str, Any]:
    """
    Consulta o total de saídas registradas.
    
    Returns:
        dict: Dicionário com total de saídas
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        return {
            "total_saidas": float(resumo['total_saidas'])
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar saídas: {e}")
        return {"erro": "Erro ao consultar saídas"}


def consultar_gastos_categoria(categoria: str) -> Dict[str, Any]:
    """
    Consulta o valor total gasto em uma categoria específica.
    
    Args:
        categoria (str): Nome da categoria
        
    Returns:
        dict: Dicionário com categoria e valor total
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        estatisticas = obter_estatisticas_categoria(categoria, usuario_id=usuario_id)
        
        if estatisticas['quantidade'] == 0:
            return {
                "categoria": categoria,
                "valor": 0.0,
                "quantidade": 0,
                "mensagem": f"Não há gastos registrados com {categoria}"
            }
        
        return {
            "categoria": categoria,
            "valor": float(estatisticas['valor_total']),
            "quantidade": estatisticas['quantidade']
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar gastos da categoria {categoria}: {e}")
        return {"erro": f"Erro ao consultar gastos da categoria {categoria}"}


def consultar_maior_categoria() -> Dict[str, Any]:
    """
    Consulta a categoria com maior gasto.
    
    Returns:
        dict: Dicionário com categoria de maior gasto e valor
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        gastos_categoria = calcular_gastos_por_categoria(usuario_id=usuario_id)
        
        if gastos_categoria.empty:
            return {
                "categoria": None,
                "valor": 0.0,
                "mensagem": "Não há gastos registrados por categoria"
            }
        
        maior_gasto = gastos_categoria.loc[gastos_categoria['valor'].idxmax()]
        return {
            "categoria": str(maior_gasto['categoria']),
            "valor": float(maior_gasto['valor'])
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar maior categoria: {e}")
        return {"erro": "Erro ao consultar maior categoria"}


def consultar_total_investido() -> Dict[str, Any]:
    """
    Consulta o total de investimentos registrados.
    
    Returns:
        dict: Dicionário com total de investimentos
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        return {
            "total_investido": float(resumo['total_investido'])
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar investimentos: {e}")
        return {"erro": "Erro ao consultar investimentos"}


def consultar_meta_ativa() -> Dict[str, Any]:
    """
    Consulta a meta financeira ativa.
    
    Returns:
        dict: Dicionário com dados da meta ativa
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        meta = buscar_meta_ativa(usuario_id=usuario_id)
        
        if not meta:
            return {
                "meta": None,
                "mensagem": "Não há meta financeira ativa"
            }
        
        valor_meta = float(meta['valor_meta'])
        valor_atual = float(meta['valor_atual'])
        
        if valor_meta > 0:
            percentual = (valor_atual / valor_meta) * 100
            falta = valor_meta - valor_atual
        else:
            percentual = 0
            falta = 0
        
        return {
            "titulo": meta['titulo'],
            "valor_meta": valor_meta,
            "valor_atual": valor_atual,
            "percentual": percentual,
            "falta": falta
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar meta: {e}")
        return {"erro": "Erro ao consultar meta"}


def consultar_quantidade_transacoes() -> Dict[str, Any]:
    """
    Consulta a quantidade total de transações registradas.
    
    Returns:
        dict: Dicionário com quantidade de transações
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        return {
            "quantidade": resumo['qtd_transacoes']
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar quantidade de transações: {e}")
        return {"erro": "Erro ao consultar quantidade de transações"}


def consultar_ultimas_transacoes(limite: Optional[int] = None) -> Dict[str, Any]:
    """
    Consulta as últimas transações registradas.
    
    Args:
        limite (int): Quantidade máxima de transações (máximo 10)
        
    Returns:
        dict: Dicionário com lista de transações
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        limite_preferido = obter_configuracoes_usuario(usuario_id)[
            "qtd_transacoes_recentes"
        ]
        limite = min(int(limite or limite_preferido), limite_preferido, 20)
        transacoes = buscar_ultimas_transacoes(limite=limite, usuario_id=usuario_id)
        
        # Converte valores para float e strings para serialização
        transacoes_serializadas = []
        for t in transacoes:
            transacoes_serializadas.append({
                "data_transacao": str(t['data_transacao']),
                "descricao": str(t['descricao']),
                "categoria": str(t['categoria']),
                "tipo": str(t['tipo']),
                "valor": float(t['valor'])
            })
        
        return {
            "transacoes": transacoes_serializadas,
            "quantidade": len(transacoes_serializadas)
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar últimas transações: {e}")
        return {"erro": "Erro ao consultar últimas transações"}


def consultar_resumo_financeiro() -> Dict[str, Any]:
    """
    Consulta um resumo financeiro geral combinando várias métricas.
    
    Returns:
        dict: Dicionário com resumo financeiro completo
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        gastos_categoria = calcular_gastos_por_categoria(usuario_id=usuario_id)
        meta = buscar_meta_ativa(usuario_id=usuario_id)
        
        # Processa gastos por categoria
        gastos_lista = []
        if not gastos_categoria.empty:
            for _, row in gastos_categoria.iterrows():
                gastos_lista.append({
                    "categoria": str(row['categoria']),
                    "valor": float(row['valor'])
                })
        
        # Processa meta
        meta_dados = None
        if meta:
            valor_meta = float(meta['valor_meta'])
            valor_atual = float(meta['valor_atual'])
            meta_dados = {
                "titulo": meta['titulo'],
                "valor_meta": valor_meta,
                "valor_atual": valor_atual,
                "percentual": (valor_atual / valor_meta * 100) if valor_meta > 0 else 0
            }
        
        return {
            "saldo": float(resumo['saldo_final']),
            "entradas": float(resumo['total_entradas']),
            "saidas": float(resumo['total_saidas']),
            "investimentos": float(resumo['total_investido']),
            "quantidade_transacoes": resumo['qtd_transacoes'],
            "gastos_por_categoria": gastos_lista,
            "meta": meta_dados
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao consultar resumo financeiro: {e}")
        return {"erro": "Erro ao consultar resumo financeiro"}


def listar_categorias_disponiveis() -> Dict[str, Any]:
    """
    Lista todas as categorias cadastradas no sistema.
    
    Returns:
        dict: Dicionário com lista de categorias
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        categorias = buscar_todas_categorias(usuario_id=usuario_id)
        
        categorias_lista = []
        for cat in categorias:
            categorias_lista.append({
                "nome": cat['nome'],
                "palavras_chave": cat['palavras_chave']
            })
        
        return {
            "categorias": categorias_lista,
            "quantidade": len(categorias_lista)
        }
    except Exception as e:
        print(f"[AI Agent] Erro ao listar categorias: {e}")
        return {"erro": "Erro ao listar categorias"}


# ==========================
# RESOLUÇÃO DE CATEGORIAS
# ==========================

def normalizar_texto(texto: str) -> str:
    """
    Normaliza o texto para comparação: minúsculas e sem acentos.
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto


def normalizar_texto_sem_pontuacao(texto: str) -> str:
    """
    Normaliza o texto e remove pontuação para comparação de palavras.
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado sem pontuação
    """
    import string
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto


def resolver_categoria(pergunta: str) -> Optional[str]:
    """
    Tenta identificar uma categoria mencionada na pergunta.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        str: Nome da categoria ou None
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        categorias = buscar_todas_categorias(usuario_id=usuario_id)
        pergunta_normalizada = normalizar_texto_sem_pontuacao(pergunta)
        
        # Divide a pergunta em palavras para correspondência mais precisa
        palavras_pergunta = pergunta_normalizada.split()
        
        # Primeiro, tenta correspondência exata com o nome
        for categoria in categorias:
            nome_normalizado = normalizar_texto(categoria['nome'])
            if nome_normalizado in palavras_pergunta:
                return categoria['nome']
        
        # Segundo, tenta correspondência com palavras-chave
        for categoria in categorias:
            palavras_chave = categoria.get('palavras_chave', [])
            for palavra in palavras_chave:
                palavra_normalizada = normalizar_texto(palavra)
                if palavra_normalizado in palavras_pergunta:
                    return categoria['nome']
        
        return None
    except Exception as e:
        print(f"[AI Agent] Erro ao resolver categoria: {e}")
        return None


# ==========================
# DEFINIÇÃO DE TOOLS
# ==========================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_saldo",
            "description": "Consulta o saldo atual (entradas - saídas - investimentos). Use quando o usuário perguntar sobre saldo, quanto tem, situação financeira geral.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_total_entradas",
            "description": "Consulta o total de entradas registradas. Use quando o usuário perguntar sobre quanto recebeu, entradas, rendimentos.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_total_saidas",
            "description": "Consulta o total de saídas registradas. Use quando o usuário perguntar sobre quanto gastou no total, despesas gerais, sem especificar uma categoria.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_gastos_categoria",
            "description": "Consulta o valor total gasto em uma categoria específica. Use quando o usuário mencionar uma categoria específica (alimentação, transporte, casa, etc). Priorize esta função em vez de consultar_total_saidas quando uma categoria for mencionada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Nome da categoria financeira (ex: alimentação, transporte, casa, lazer)"
                    }
                },
                "required": ["categoria"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_maior_categoria",
            "description": "Consulta a categoria com maior gasto. Use quando o usuário perguntar sobre maior gasto, categoria que mais gastou, onde mais gastou.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_total_investido",
            "description": "Consulta o total de investimentos registrados. Use quando o usuário perguntar sobre investimentos, aplicações.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_meta_ativa",
            "description": "Consulta a meta financeira ativa. Use quando o usuário perguntar sobre meta, objetivo, quanto falta para atingir, percentual da meta.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_quantidade_transacoes",
            "description": "Consulta a quantidade total de transações registradas. Use quando o usuário perguntar quantas transações tem.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_ultimas_transacoes",
            "description": "Consulta as últimas transações registradas. Use quando o usuário perguntar sobre última transação, últimas movimentações, transações recentes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {
                        "type": "integer",
                        "description": "Quantidade de transações a retornar, respeitando o limite configurado pelo usuário (máximo 20)"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_resumo_financeiro",
            "description": "Consulta um resumo financeiro geral combinando várias métricas. Use quando o usuário pedir um resumo, análise geral, panorama das finanças.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_categorias_disponiveis",
            "description": "Lista todas as categorias cadastradas no sistema. Use quando o usuário perguntar sobre categorias disponíveis ou quando não encontrar uma categoria mencionada.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    }
]


# Mapeamento de nome da função para a função Python
FUNCTION_MAP = {
    "consultar_saldo": consultar_saldo,
    "consultar_total_entradas": consultar_total_entradas,
    "consultar_total_saidas": consultar_total_saidas,
    "consultar_gastos_categoria": consultar_gastos_categoria,
    "consultar_maior_categoria": consultar_maior_categoria,
    "consultar_total_investido": consultar_total_investido,
    "consultar_meta_ativa": consultar_meta_ativa,
    "consultar_quantidade_transacoes": consultar_quantidade_transacoes,
    "consultar_ultimas_transacoes": consultar_ultimas_transacoes,
    "consultar_resumo_financeiro": consultar_resumo_financeiro,
    "listar_categorias_disponiveis": listar_categorias_disponiveis
}


# ==========================
# INSTRUÇÃO DO SISTEMA
# ==========================

SYSTEM_INSTRUCTION = """Você é um assistente financeiro do Personal Finance Flow. Responda em português do Brasil.

Regras importantes:
1. Utilize exclusivamente as ferramentas fornecidas para obter números financeiros.
2. Nunca invente valores, categorias, metas ou transações.
3. Quando faltarem dados, informe claramente ao usuário.
4. Não forneça recomendações de investimento personalizadas ou aconselhamento financeiro.
5. Diferencie consultas de uma categoria específica do total geral de saídas.
6. Se o usuário mencionar uma categoria específica (alimentação, transporte, casa, etc), use a função consultar_gastos_categoria em vez de consultar_total_saidas.
7. Se não encontrar uma categoria mencionada, use listar_categorias_disponiveis para informar as opções.
8. Seja conciso e direto nas respostas.
9. Formate valores monetários conforme a moeda indicada nas preferências abaixo, sem converter os valores.
10. Não execute código, não acesse arquivos, não execute SQL."""


def _instrucao_preferencias_usuario():
    usuario_id = _obter_usuario_id_da_sessao()
    configuracoes = obter_configuracoes_usuario(usuario_id)
    return (
        f"\nPreferências do usuário: moeda {configuracoes['moeda']}; "
        f"formato de data {configuracoes['formato_data']}."
    )


# ==========================
# FUNÇÃO PRINCIPAL
# ==========================

def responder_pergunta_openai(pergunta: str) -> Dict[str, Any]:
    """
    Processa uma pergunta usando OpenAI com function calling.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        dict: Resposta com campos 'resposta', 'origem', 'ferramenta', 'dados'
    """
    # Verifica se o cliente OpenAI está disponível
    if not client:
        raise Exception("Cliente OpenAI não disponível")
    
    print(f"[AI Agent] Processando pergunta com OpenAI: {pergunta}")
    
    # Validação básica
    if not pergunta or not pergunta.strip():
        return {
            "resposta": "Por favor, digite uma pergunta.",
            "origem": "local",
            "ferramenta": None,
            "dados": {}
        }
    
    if len(pergunta) > 500:
        return {
            "resposta": "A pergunta é muito longa. Por favor, seja mais conciso.",
            "origem": "local",
            "ferramenta": None,
            "dados": {}
        }
    
    # Verifica se há uma categoria mencionada
    categoria_mencionada = resolver_categoria(pergunta)
    
    # Se houver categoria mencionada, adiciona contexto à pergunta
    if categoria_mencionada:
        pergunta_contextualizada = f"{pergunta} (categoria: {categoria_mencionada})"
    else:
        pergunta_contextualizada = pergunta
    
    # Limite de iterações para evitar loop infinito
    max_iterations = 4
    iteration = 0
    
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION + _instrucao_preferencias_usuario()},
        {"role": "user", "content": pergunta_contextualizada}
    ]
    
    ferramenta_usada = None
    dados_ferramenta = {}
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            # Faz a chamada à API
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Verifica se o modelo quer chamar uma função
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                # Processa cada chamada de função
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = tool_call.function.arguments
                    
                    print(f"[AI Agent] Chamando função: {function_name} com args: {function_args}")
                    
                    # Valida se a função é permitida
                    if function_name not in FUNCTION_MAP:
                        print(f"[AI Agent] Função não permitida: {function_name}")
                        continue
                    
                    # Executa a função
                    try:
                        import json
                        args_dict = json.loads(function_args) if function_args else {}
                        function_result = FUNCTION_MAP[function_name](**args_dict)
                        
                        # Registra a ferramenta usada
                        ferramenta_usada = function_name
                        dados_ferramenta = function_result
                        
                        # Adiciona o resultado à conversa
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_result, ensure_ascii=False)
                        })
                        
                    except Exception as e:
                        print(f"[AI Agent] Erro ao executar função {function_name}: {e}")
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps({"erro": str(e)}, ensure_ascii=False)
                        })
                
                # Continua o loop para obter a resposta final
                continue
            else:
                # Resposta final do modelo
                resposta = response_message.content
                
                if not resposta:
                    resposta = "Não consegui gerar uma resposta. Tente reformular sua pergunta."
                
                return {
                    "resposta": resposta,
                    "origem": "openai",
                    "ferramenta": ferramenta_usada,
                    "dados": dados_ferramenta
                }
                
        except Exception as e:
            print(f"[AI Agent] Erro na chamada OpenAI (iteração {iteration}): {e}")
            raise e
    
    # Se atingiu o limite de iterações
    return {
        "resposta": "Não consegui processar sua pergunta. Tente ser mais específico.",
        "origem": "local",
        "ferramenta": None,
        "dados": {}
    }
