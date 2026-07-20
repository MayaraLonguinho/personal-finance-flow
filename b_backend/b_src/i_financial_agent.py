
# Módulo de Agent Financeiro
# Responsável por responder perguntas sobre finanças pessoais

import string
import unicodedata

from b_backend.b_src.d_categorias import buscar_todas_categorias
from b_backend.b_src.h_investimentos import (
    listar_investimentos,
    obter_resumo_investimentos,
)
from b_backend.b_src.g_metas import buscar_meta_ativa
from b_backend.b_src.e_metrics import (
    buscar_ultimas_transacoes,
    calcular_gastos_por_categoria,
    calcular_resumo_financeiro,
)
from b_backend.b_src.l_utils import formatar_data, formatar_moeda
from b_backend.b_src.b_usuario_contexto import obter_usuario_id
from b_backend.b_src.k_configuracoes import obter_configuracoes_usuario


# Palavras-chave para reconhecimento das intenções gerais.
INTENCOES = {
    "saldo": [
        "saldo",
        "sobrou",
        "restou",
        "positivo",
        "negativo",
        "zerado",
        "quanto tenho",
        "minha situação",
        "estou no positivo",
        "estou no negativo",
    ],
    "entradas": [
        "recebi",
        "recebido",
        "entrou",
        "entradas",
        "entrada",
        "ganhei",
        "ganho",
        "renda",
        "rendimentos",
        "total de entradas",
        "quanto recebi",
    ],
    "saidas": [
        "gastei",
        "gasto",
        "gastos",
        "saídas",
        "saida",
        "despesas",
        "despesa",
        "saiu",
        "sair",
        "gastar",
        "paguei",
        "pagamento",
        "total de despesas",
    ],
    "categorias": [
        "categoria",
        "categorias",
        "maior gasto",
        "maior despesa",
        "gastei com",
        "gastar com",
        "quanto gastei com",
        "qual categoria",
        "categoria de gasto",
    ],
    "investimentos": [
        "investi",
        "investido",
        "investimento",
        "investimentos",
        "aplicação",
        "aplicações",
        "aplicacao",
        "aplicacoes",
        "carteira",
        "patrimônio investido",
        "patrimonio investido",
        "tenho investimentos",
        "quanto investi",
    ],
    "metas": [
        "meta",
        "metas",
        "objetivo",
        "objetivos",
        "economia",
        "poupar",
        "falta para",
        "percentual da meta",
        "como está minha meta",
        "atingir minha meta",
    ],
    "transacoes": [
        "transações",
        "transacao",
        "transação",
        "movimentações",
        "movimentação",
        "quantas transações",
        "última transação",
        "últimas movimentações",
        "minhas transações",
        "quantidade de transações",
    ],
    "resumo": [
        "resumo",
        "análise",
        "como estão minhas finanças",
        "faça um resumo",
        "me dê uma análise",
        "situação geral",
        "panorama",
        "visão geral",
    ],
}


TIPOS_INVESTIMENTO_CONHECIDOS = [
    "CDB",
    "LCI",
    "LCA",
    "Tesouro Direto",
    "Fundo de Investimento",
    "Ações",
    "ETF",
    "FII",
    "Criptomoeda",
    "Poupança",
    "Renda Fixa",
    "Renda Variável",
]


def _obter_usuario_id_da_sessao():
    usuario_id = obter_usuario_id()
    if usuario_id is None:
        raise PermissionError("Usuário não autenticado para consultar dados financeiros")
    return usuario_id


def _limite_transacoes_preferido(usuario_id):
    return obter_configuracoes_usuario(usuario_id)["qtd_transacoes_recentes"]


def normalizar_texto(texto):
    """
    Normaliza um texto para comparação.

    O resultado é convertido para minúsculas e fica sem acentos.

    Args:
        texto (str): Texto que será normalizado.

    Returns:
        str: Texto normalizado.
    """
    if texto is None:
        return ""

    texto = str(texto).lower()
    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )


def normalizar_texto_sem_pontuacao(texto):
    """
    Normaliza um texto e remove pontuação.

    Args:
        texto (str): Texto que será normalizado.

    Returns:
        str: Texto normalizado sem pontuação.
    """
    texto_normalizado = normalizar_texto(texto)

    return texto_normalizado.translate(
        str.maketrans("", "", string.punctuation)
    )


def contem_algum_termo(texto, termos):
    """
    Verifica se um texto contém pelo menos um termo da lista.

    Args:
        texto (str): Texto já normalizado.
        termos (list): Lista de expressões.

    Returns:
        bool: True quando algum termo estiver presente.
    """
    return any(
        normalizar_texto(termo) in texto
        for termo in termos
    )

def identificar_intencao(pergunta):
    """
    Identifica a intenção geral da pergunta.

    Perguntas sobre categorias possuem prioridade sobre a
    intenção genérica de saídas. Isso evita que expressões como
    "maior categoria de gasto" sejam classificadas apenas como
    total de gastos.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        str: Intenção identificada ou None.
    """
    pergunta_normalizada = normalizar_texto(pergunta)

    termos_prioritarios_categoria = [
        "maior categoria",
        "categoria de gasto",
        "categoria de gastos",
        "qual categoria",
        "onde mais gastei",
        "onde eu mais gastei",
        "em que mais gastei",
        "com o que mais gastei",
        "maior gasto",
        "maior despesa",
    ]

    if contem_algum_termo(
        pergunta_normalizada,
        termos_prioritarios_categoria,
    ):
        return "categorias"

    ordem_intencoes = [
        "categorias",
        "saldo",
        "entradas",
        "saidas",
        "investimentos",
        "metas",
        "transacoes",
        "resumo",
    ]

    for intencao in ordem_intencoes:
        palavras_chave = INTENCOES[intencao]

        for palavra in palavras_chave:
            if normalizar_texto(
                palavra
            ) in pergunta_normalizada:
                return intencao

    return None


def identificar_intencao_investimento(pergunta):
    """
    Identifica uma intenção específica sobre investimentos.

    A ordem das verificações evita que perguntas específicas,
    como rentabilidade, caiam na resposta genérica da carteira.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        str: Intenção específica ou None.
    """
    pergunta_normalizada = normalizar_texto(pergunta)

    termos_resultado = [
        "tive lucro",
        "tenho lucro",
        "qual meu lucro",
        "lucro dos investimentos",
        "lucro da carteira",
        "tive prejuizo",
        "tenho prejuizo",
        "qual meu prejuizo",
        "prejuizo dos investimentos",
        "prejuizo da carteira",
        "resultado da carteira",
        "resultado dos investimentos",
        "ganhei com os investimentos",
        "perdi com os investimentos",
    ]

    termos_rentabilidade = [
        "rentabilidade",
        "rendimento da carteira",
        "rendimento dos investimentos",
        "retorno da carteira",
        "retorno dos investimentos",
        "percentual de retorno",
        "quanto rendeu",
        "quanto meus investimentos renderam",
    ]

    termos_valor_atual = [
        "valor atual dos investimentos",
        "valor atual da carteira",
        "quanto vale minha carteira",
        "quanto vale a carteira",
        "quanto tenho investido hoje",
        "quanto tenho hoje em investimentos",
        "patrimonio atual investido",
        "saldo da carteira",
    ]

    termos_total_aplicado = [
        "total aplicado",
        "valor aplicado",
        "quanto apliquei",
        "quanto eu apliquei",
        "quanto investi",
        "quanto eu investi",
        "capital aplicado",
    ]

    termos_quantidade = [
        "quantos investimentos",
        "quantidade de investimentos",
        "quantos ativos",
        "quantidade de ativos",
        "investimentos ativos",
        "ativos na carteira",
    ]

    termos_resumo = [
        "resumo dos investimentos",
        "resumo da carteira",
        "resumo de investimentos",
        "análise da carteira",
        "analise da carteira",
        "como estão meus investimentos",
        "como esta minha carteira",
        "situação da carteira",
        "situacao da carteira",
        "panorama da carteira",
    ]

    termos_gerais = [
        "investimento",
        "investimentos",
        "carteira",
        "aplicação",
        "aplicações",
        "aplicacao",
        "aplicacoes",
        "patrimônio investido",
        "patrimonio investido",
    ]

    if contem_algum_termo(
        pergunta_normalizada,
        termos_resultado,
    ):
        return "investimentos_resultado"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_rentabilidade,
    ):
        return "investimentos_rentabilidade"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_valor_atual,
    ):
        return "investimentos_valor_atual"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_total_aplicado,
    ):
        return "investimentos_total_aplicado"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_quantidade,
    ):
        return "investimentos_quantidade"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_resumo,
    ):
        return "investimentos_resumo"

    tipo_investimento = extrair_tipo_investimento_mencionado(
        pergunta
    )

    if tipo_investimento:
        return "investimentos_tipo"

    if contem_algum_termo(
        pergunta_normalizada,
        termos_gerais,
    ):
        return "investimentos_resumo"

    return None


def extrair_categoria_mencionada(pergunta):
    """
    Extrai o nome de uma categoria mencionada na pergunta.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        str: Nome da categoria ou None.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        categorias = buscar_todas_categorias(usuario_id=usuario_id)
        pergunta_normalizada = normalizar_texto(pergunta)

        for categoria in categorias:
            nome_categoria = normalizar_texto(
                categoria["nome"]
            )

            if nome_categoria in pergunta_normalizada:
                return categoria["nome"]

        return None

    except Exception as erro:
        print(
            "Erro ao extrair categoria: "
            f"{erro}"
        )

        return None


def extrair_grupo_categoria_mencionada(pergunta):
    """
    Extrai uma categoria utilizando nome e palavras-chave.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        str: Nome da categoria ou None.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        categorias = buscar_todas_categorias(usuario_id=usuario_id)

        pergunta_normalizada = (
            normalizar_texto_sem_pontuacao(pergunta)
        )

        palavras_pergunta = pergunta_normalizada.split()

        for categoria in categorias:
            nome_categoria = normalizar_texto(
                categoria["nome"]
            )

            palavras_nome_categoria = (
                nome_categoria.split()
            )

            if all(
                palavra in palavras_pergunta
                for palavra in palavras_nome_categoria
            ):
                return categoria["nome"]

            palavras_chave = categoria.get(
                "palavras_chave",
                [],
            )

            for palavra in palavras_chave:
                palavra_normalizada = normalizar_texto(
                    palavra
                )

                if palavra_normalizada in palavras_pergunta:
                    return categoria["nome"]

        return None

    except Exception as erro:
        print(
            "Erro ao extrair grupo de categoria: "
            f"{erro}"
        )

        return None


def extrair_tipo_investimento_mencionado(pergunta):
    """
    Procura um tipo de investimento mencionado na pergunta.

    A função verifica tanto os tipos conhecidos pela aplicação
    quanto os tipos que já estão cadastrados no banco.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        str: Tipo encontrado ou None.
    """
    pergunta_normalizada = normalizar_texto(pergunta)

    tipos_disponiveis = list(
        TIPOS_INVESTIMENTO_CONHECIDOS
    )

    try:
        usuario_id = _obter_usuario_id_da_sessao()
        investimentos = listar_investimentos(
            usuario_id=usuario_id,
        )

        for investimento in investimentos:
            tipo = investimento.get("tipo")

            if (
                tipo
                and tipo not in tipos_disponiveis
            ):
                tipos_disponiveis.append(tipo)

    except Exception as erro:
        print(
            "Erro ao consultar tipos de investimento: "
            f"{erro}"
        )

    tipos_ordenados = sorted(
        tipos_disponiveis,
        key=len,
        reverse=True,
    )

    for tipo in tipos_ordenados:
        if normalizar_texto(tipo) in pergunta_normalizada:
            return tipo

    return None


def responder_categorias_especifica(categoria):
    """
    Responde perguntas sobre uma categoria específica.

    Args:
        categoria (str): Nome da categoria.

    Returns:
        dict: Resposta formatada.
    """
    try:
        from b_backend.b_src.d_categorias import (
            obter_estatisticas_categoria,
        )

        usuario_id = _obter_usuario_id_da_sessao()
        estatisticas = obter_estatisticas_categoria(
            categoria,
            usuario_id=usuario_id,
        )

        if estatisticas["quantidade"] == 0:
            return {
                "resposta": (
                    "Não há gastos registrados com "
                    f"{categoria}."
                ),
                "tipo": "categoria_especifica",
                "dados": {
                    "categoria": categoria,
                    "valor": 0,
                },
            }

        valor = float(
            estatisticas["valor_total"]
        )

        return {
            "resposta": (
                f"Você gastou {formatar_moeda(valor)} "
                f"com {categoria}."
            ),
            "tipo": "categoria_especifica",
            "dados": {
                "categoria": categoria,
                "valor": valor,
            },
        }

    except Exception as erro:
        print(
            "Erro ao consultar categoria específica: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar os gastos "
                f"com {categoria}."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_saldo():
    """
    Responde perguntas sobre o saldo financeiro.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)
        saldo = float(resumo["saldo_final"] or 0)

        if saldo > 0:
            resposta = (
                "Seu saldo atual é positivo em "
                f"{formatar_moeda(saldo)}."
            )
            tipo = "positivo"

        elif saldo < 0:
            resposta = (
                "Seu saldo atual é negativo em "
                f"{formatar_moeda(abs(saldo))}."
            )
            tipo = "negativo"

        else:
            resposta = "Seu saldo está zerado."
            tipo = "neutro"

        return {
            "resposta": resposta,
            "tipo": tipo,
            "dados": {
                "saldo": saldo,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao calcular saldo: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem transações suficientes "
                "para calcular o saldo."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_entradas():
    """
    Responde perguntas sobre entradas financeiras.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)

        total_entradas = float(
            resumo["total_entradas"]
            or 0
        )

        if total_entradas > 0:
            resposta = (
                "O total de entradas é "
                f"{formatar_moeda(total_entradas)}."
            )
        else:
            resposta = "Não há entradas registradas."

        return {
            "resposta": resposta,
            "tipo": "entradas",
            "dados": {
                "total_entradas": total_entradas,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao calcular entradas: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem transações suficientes "
                "para calcular as entradas."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_saidas():
    """
    Responde perguntas sobre saídas financeiras.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)

        total_saidas = float(
            resumo["total_saidas"]
            or 0
        )

        if total_saidas > 0:
            resposta = (
                "O total de saídas é "
                f"{formatar_moeda(total_saidas)}."
            )
        else:
            resposta = "Não há saídas registradas."

        return {
            "resposta": resposta,
            "tipo": "saidas",
            "dados": {
                "total_saidas": total_saidas,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao calcular saídas: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem transações suficientes "
                "para calcular as saídas."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_categorias(pergunta):
    """
    Responde perguntas gerais sobre categorias.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        dict: Resposta formatada.
    """
    try:
        categoria_mencionada = (
            extrair_categoria_mencionada(pergunta)
        )

        usuario_id = _obter_usuario_id_da_sessao()
        gastos_categoria = (
            calcular_gastos_por_categoria(usuario_id=usuario_id)
        )

        if categoria_mencionada:
            categoria_gasto = gastos_categoria[
                gastos_categoria["categoria"]
                == categoria_mencionada
            ]

            if not categoria_gasto.empty:
                valor = float(
                    categoria_gasto.iloc[0]["valor"]
                )

                return {
                    "resposta": (
                        f"Você gastou {formatar_moeda(valor)} "
                        f"com {categoria_mencionada}."
                    ),
                    "tipo": "categoria_especifica",
                    "dados": {
                        "categoria": categoria_mencionada,
                        "valor": valor,
                    },
                }

            return {
                "resposta": (
                    "Não há gastos registrados com "
                    f"{categoria_mencionada}."
                ),
                "tipo": "categoria_especifica",
                "dados": {
                    "categoria": categoria_mencionada,
                    "valor": 0,
                },
            }

        if gastos_categoria.empty:
            return {
                "resposta": (
                    "Não há gastos registrados por categoria."
                ),
                "tipo": "categoria",
                "dados": {},
            }

        maior_gasto = gastos_categoria.loc[
            gastos_categoria["valor"].idxmax()
        ]

        valor_maior_gasto = float(
            maior_gasto["valor"]
        )

        return {
            "resposta": (
                "Sua maior categoria de gastos foi "
                f"{maior_gasto['categoria']}, com "
                f"{formatar_moeda(valor_maior_gasto)}."
            ),
            "tipo": "categoria",
            "dados": {
                "categoria": maior_gasto["categoria"],
                "valor": valor_maior_gasto,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao calcular categorias: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem transações suficientes "
                "para analisar as categorias."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_resumo_investimentos():
    """
    Retorna um resumo completo da carteira de investimentos.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_total = int(
            resumo["quantidade_total"]
            or 0
        )

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        if quantidade_total == 0:
            return {
                "resposta": (
                    "Você ainda não possui investimentos "
                    "cadastrados."
                ),
                "tipo": "investimentos_resumo",
                "dados": resumo,
            }

        total_aplicado = float(
            resumo["total_aplicado"]
            or 0
        )

        valor_atual = float(
            resumo["valor_atual_total"]
            or 0
        )

        resultado = float(
            resumo["lucro_prejuizo"]
            or 0
        )

        rentabilidade = float(
            resumo["rentabilidade_total"]
            or 0
        )

        if resultado > 0:
            texto_resultado = (
                "lucro acumulado de "
                f"{formatar_moeda(resultado)}"
            )

        elif resultado < 0:
            texto_resultado = (
                "prejuízo acumulado de "
                f"{formatar_moeda(abs(resultado))}"
            )

        else:
            texto_resultado = (
                "nenhuma variação acumulada"
            )

        resposta = (
            f"Você possui {quantidade_ativos} "
            "investimento(s) ativo(s), com "
            f"{formatar_moeda(total_aplicado)} aplicados. "
            "O valor atual da carteira é "
            f"{formatar_moeda(valor_atual)}, com "
            f"{texto_resultado} e rentabilidade total "
            f"de {rentabilidade:.2f}%."
        )

        return {
            "resposta": resposta,
            "tipo": "investimentos_resumo",
            "dados": resumo,
        }

    except Exception as erro:
        print(
            "Erro ao gerar resumo de investimentos: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar sua carteira "
                "de investimentos."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_total_aplicado_investimentos():
    """
    Informa o capital aplicado nos investimentos ativos.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        total_aplicado = float(
            resumo["total_aplicado"]
            or 0
        )

        if quantidade_ativos == 0:
            resposta = (
                "Você não possui investimentos ativos "
                "com valor aplicado."
            )
        else:
            resposta = (
                "O total aplicado nos investimentos ativos "
                f"é de {formatar_moeda(total_aplicado)}."
            )

        return {
            "resposta": resposta,
            "tipo": "investimentos_total_aplicado",
            "dados": resumo,
        }

    except Exception as erro:
        print(
            "Erro ao consultar total aplicado: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar o total aplicado."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_valor_atual_investimentos():
    """
    Informa o valor atual da carteira ativa.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        valor_atual = float(
            resumo["valor_atual_total"]
            or 0
        )

        if quantidade_ativos == 0:
            resposta = (
                "Você não possui investimentos ativos "
                "na carteira."
            )
        else:
            resposta = (
                "O valor atual da sua carteira de "
                "investimentos é "
                f"{formatar_moeda(valor_atual)}."
            )

        return {
            "resposta": resposta,
            "tipo": "investimentos_valor_atual",
            "dados": resumo,
        }

    except Exception as erro:
        print(
            "Erro ao consultar valor atual: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar o valor atual "
                "da carteira."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_resultado_investimentos():
    """
    Informa o lucro ou prejuízo acumulado da carteira.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        resultado = float(
            resumo["lucro_prejuizo"]
            or 0
        )

        if quantidade_ativos == 0:
            resposta = (
                "Você não possui investimentos ativos "
                "para calcular lucro ou prejuízo."
            )
            classificacao = "neutro"

        elif resultado > 0:
            resposta = (
                "Sua carteira apresenta lucro de "
                f"{formatar_moeda(resultado)}."
            )
            classificacao = "positivo"

        elif resultado < 0:
            resposta = (
                "Sua carteira apresenta prejuízo de "
                f"{formatar_moeda(abs(resultado))}."
            )
            classificacao = "negativo"

        else:
            resposta = (
                "Sua carteira não apresenta lucro "
                "nem prejuízo no momento."
            )
            classificacao = "neutro"

        return {
            "resposta": resposta,
            "tipo": "investimentos_resultado",
            "dados": {
                **resumo,
                "classificacao": classificacao,
            },
        }

    except Exception as erro:
        print(
            "Erro ao consultar resultado da carteira: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível calcular o resultado "
                "da carteira."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_rentabilidade_investimentos():
    """
    Informa a rentabilidade total da carteira ativa.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        rentabilidade = float(
            resumo["rentabilidade_total"]
            or 0
        )

        if quantidade_ativos == 0:
            resposta = (
                "Você não possui investimentos ativos "
                "para calcular a rentabilidade."
            )
        else:
            resposta = (
                "A rentabilidade total da sua carteira "
                f"é de {rentabilidade:.2f}%."
            )

        return {
            "resposta": resposta,
            "tipo": "investimentos_rentabilidade",
            "dados": resumo,
        }

    except Exception as erro:
        print(
            "Erro ao consultar rentabilidade: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível calcular a rentabilidade "
                "da carteira."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_quantidade_investimentos():
    """
    Informa a quantidade de investimentos cadastrados e ativos.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = obter_resumo_investimentos(usuario_id=usuario_id)

        quantidade_total = int(
            resumo["quantidade_total"]
            or 0
        )

        quantidade_ativos = int(
            resumo["quantidade_ativos"]
            or 0
        )

        if quantidade_total == 0:
            resposta = (
                "Você ainda não possui investimentos "
                "cadastrados."
            )
        else:
            resposta = (
                f"Você possui {quantidade_total} "
                "investimento(s) cadastrado(s), sendo "
                f"{quantidade_ativos} ativo(s)."
            )

        return {
            "resposta": resposta,
            "tipo": "investimentos_quantidade",
            "dados": resumo,
        }

    except Exception as erro:
        print(
            "Erro ao consultar quantidade de investimentos: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar a quantidade "
                "de investimentos."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_investimentos_por_tipo(tipo):
    """
    Responde sobre investimentos ativos de determinado tipo.

    Args:
        tipo (str): Tipo de investimento.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        investimentos = listar_investimentos(
            status="ativo",
            usuario_id=usuario_id,
        )

        tipo_normalizado = normalizar_texto(tipo)

        encontrados = [
            investimento
            for investimento in investimentos
            if normalizar_texto(
                investimento.get("tipo")
            ) == tipo_normalizado
        ]

        if not encontrados:
            return {
                "resposta": (
                    "Não encontrei investimentos ativos "
                    f"do tipo {tipo}."
                ),
                "tipo": "investimentos_tipo",
                "dados": {
                    "tipo": tipo,
                    "quantidade": 0,
                    "valor_atual_total": 0,
                    "investimentos": [],
                },
            }

        valor_atual_total = sum(
            float(
                investimento.get("valor_atual")
                or 0
            )
            for investimento in encontrados
        )

        nomes = [
            investimento.get("nome")
            for investimento in encontrados
            if investimento.get("nome")
        ]

        resposta = (
            f"Você possui {len(encontrados)} "
            f"investimento(s) ativo(s) do tipo {tipo}, "
            "com valor atual total de "
            f"{formatar_moeda(valor_atual_total)}."
        )

        if nomes:
            resposta += (
                " Os investimentos encontrados são: "
                + ", ".join(nomes)
                + "."
            )

        return {
            "resposta": resposta,
            "tipo": "investimentos_tipo",
            "dados": {
                "tipo": tipo,
                "quantidade": len(encontrados),
                "valor_atual_total": valor_atual_total,
                "investimentos": encontrados,
            },
        }

    except Exception as erro:
        print(
            "Erro ao consultar investimentos por tipo: "
            f"{erro}"
        )

        return {
            "resposta": (
                "Não foi possível consultar os "
                f"investimentos do tipo {tipo}."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_investimentos(pergunta=None):
    """
    Processa perguntas específicas sobre investimentos.

    Args:
        pergunta (str): Pergunta original do usuário.

    Returns:
        dict: Resposta formatada.
    """
    intencao = identificar_intencao_investimento(
        pergunta or ""
    )

    if intencao == "investimentos_resultado":
        return responder_resultado_investimentos()

    if intencao == "investimentos_rentabilidade":
        return responder_rentabilidade_investimentos()

    if intencao == "investimentos_valor_atual":
        return responder_valor_atual_investimentos()

    if intencao == "investimentos_total_aplicado":
        return responder_total_aplicado_investimentos()

    if intencao == "investimentos_quantidade":
        return responder_quantidade_investimentos()

    if intencao == "investimentos_tipo":
        tipo = extrair_tipo_investimento_mencionado(
            pergunta
        )

        if tipo:
            return responder_investimentos_por_tipo(
                tipo
            )

    return responder_resumo_investimentos()


def responder_metas():
    """
    Responde perguntas sobre metas financeiras.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        meta = buscar_meta_ativa(usuario_id=usuario_id)

        if not meta:
            return {
                "resposta": (
                    "Você ainda não possui uma meta "
                    "financeira ativa."
                ),
                "tipo": "metas",
                "dados": {},
            }

        valor_meta = float(
            meta["valor_meta"]
            or 0
        )

        valor_atual = float(
            meta["valor_atual"]
            or 0
        )

        titulo = meta["titulo"]

        percentual = 0

        if valor_meta > 0:
            percentual = (
                valor_atual / valor_meta
            ) * 100

            falta = valor_meta - valor_atual

            if falta > 0:
                resposta = (
                    f"Sua meta '{titulo}' está "
                    f"{percentual:.0f}% concluída. "
                    f"Faltam {formatar_moeda(falta)} "
                    "para atingir "
                    f"{formatar_moeda(valor_meta)}."
                )
            else:
                resposta = (
                    "Parabéns! Você atingiu sua meta "
                    f"'{titulo}' com "
                    f"{formatar_moeda(valor_atual)}!"
                )
        else:
            resposta = (
                f"Sua meta '{titulo}' tem valor atual "
                f"de {formatar_moeda(valor_atual)}."
            )

        return {
            "resposta": resposta,
            "tipo": "metas",
            "dados": {
                "titulo": titulo,
                "valor_meta": valor_meta,
                "valor_atual": valor_atual,
                "percentual": percentual,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao buscar metas: {erro}"
        )

        return {
            "resposta": (
                "Não foi possível buscar as informações "
                "da meta."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_transacoes(pergunta):
    """
    Responde perguntas sobre transações.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        dict: Resposta formatada.
    """
    try:
        pergunta_normalizada = normalizar_texto(
            pergunta
        )

        if (
            "quantas" in pergunta_normalizada
            or "quantidade" in pergunta_normalizada
        ):
            usuario_id = _obter_usuario_id_da_sessao()
            resumo = calcular_resumo_financeiro(usuario_id=usuario_id)

            quantidade = int(
                resumo["qtd_transacoes"]
                or 0
            )

            return {
                "resposta": (
                    f"Você tem {quantidade} "
                    "transações registradas."
                ),
                "tipo": "transacoes_quantidade",
                "dados": {
                    "quantidade": quantidade,
                },
            }

        if (
            "ultima" in pergunta_normalizada
            and "ultimas" not in pergunta_normalizada
        ):
            usuario_id = _obter_usuario_id_da_sessao()
            ultimas = buscar_ultimas_transacoes(
                limite=1,
                usuario_id=usuario_id,
            )

            if ultimas:
                ultima = ultimas[0]

                return {
                    "resposta": (
                        "Sua última transação foi "
                        f"{ultima['descricao']} de "
                        f"{formatar_moeda(ultima['valor'])} "
                        f"em {formatar_data(ultima['data_transacao'])}."
                    ),
                    "tipo": "transacao_ultima",
                    "dados": ultima,
                }

            return {
                "resposta": (
                    "Não há transações registradas."
                ),
                "tipo": "transacao_ultima",
                "dados": {},
            }

        if "ultimas" in pergunta_normalizada:
            usuario_id = _obter_usuario_id_da_sessao()
            ultimas = buscar_ultimas_transacoes(
                limite=_limite_transacoes_preferido(usuario_id),
                usuario_id=usuario_id,
            )

            if ultimas:
                linhas = [
                    (
                        f"- {transacao['descricao']}: "
                        f"{formatar_moeda(transacao['valor'])} "
                        f"em {formatar_data(transacao['data_transacao'])}"
                    )
                    for transacao in ultimas
                ]

                resposta = (
                    "Suas últimas transações foram:\n"
                    + "\n".join(linhas)
                )

                return {
                    "resposta": resposta,
                    "tipo": "transacoes_ultimas",
                    "dados": {
                        "transacoes": ultimas,
                    },
                }

            return {
                "resposta": (
                    "Não há transações registradas."
                ),
                "tipo": "transacoes_ultimas",
                "dados": {},
            }

        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)

        quantidade = int(
            resumo["qtd_transacoes"]
            or 0
        )

        return {
            "resposta": (
                f"Você tem {quantidade} "
                "transações registradas."
            ),
            "tipo": "transacoes_quantidade",
            "dados": {
                "quantidade": quantidade,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao buscar transações: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem transações registradas."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_resumo():
    """
    Responde perguntas sobre o panorama financeiro geral.

    Returns:
        dict: Resposta formatada.
    """
    try:
        usuario_id = _obter_usuario_id_da_sessao()
        resumo = calcular_resumo_financeiro(usuario_id=usuario_id)

        gastos_categoria = (
            calcular_gastos_por_categoria(usuario_id=usuario_id)
        )

        meta = buscar_meta_ativa(usuario_id=usuario_id)

        resumo_investimentos = (
            obter_resumo_investimentos(usuario_id=usuario_id)
        )

        partes = []

        total_entradas = float(
            resumo["total_entradas"]
            or 0
        )

        total_saidas = float(
            resumo["total_saidas"]
            or 0
        )

        saldo = float(
            resumo["saldo_final"]
            or 0
        )

        if total_entradas > 0:
            partes.append(
                "Você recebeu "
                f"{formatar_moeda(total_entradas)}."
            )

        if total_saidas > 0:
            partes.append(
                "Você gastou "
                f"{formatar_moeda(total_saidas)}."
            )

        if saldo > 0:
            partes.append(
                "Seu saldo é positivo em "
                f"{formatar_moeda(saldo)}."
            )

        elif saldo < 0:
            partes.append(
                "Seu saldo é negativo em "
                f"{formatar_moeda(abs(saldo))}."
            )

        else:
            partes.append(
                "Seu saldo atual está zerado."
            )

        if not gastos_categoria.empty:
            maior_gasto = gastos_categoria.loc[
                gastos_categoria["valor"].idxmax()
            ]

            partes.append(
                "Sua maior categoria de gastos foi "
                f"{maior_gasto['categoria']} com "
                f"{formatar_moeda(maior_gasto['valor'])}."
            )

        quantidade_ativos = int(
            resumo_investimentos["quantidade_ativos"]
            or 0
        )

        valor_atual_carteira = float(
            resumo_investimentos["valor_atual_total"]
            or 0
        )

        resultado_carteira = float(
            resumo_investimentos["lucro_prejuizo"]
            or 0
        )

        if quantidade_ativos > 0:
            texto_carteira = (
                "Sua carteira possui "
                f"{quantidade_ativos} investimento(s) "
                "ativo(s), com valor atual de "
                f"{formatar_moeda(valor_atual_carteira)}"
            )

            if resultado_carteira > 0:
                texto_carteira += (
                    " e lucro de "
                    f"{formatar_moeda(resultado_carteira)}."
                )

            elif resultado_carteira < 0:
                texto_carteira += (
                    " e prejuízo de "
                    f"{formatar_moeda(abs(resultado_carteira))}."
                )

            else:
                texto_carteira += (
                    " e sem variação acumulada."
                )

            partes.append(texto_carteira)

        if meta:
            valor_meta = float(
                meta["valor_meta"]
                or 0
            )

            valor_atual_meta = float(
                meta["valor_atual"]
                or 0
            )

            if valor_meta > 0:
                percentual = (
                    valor_atual_meta
                    / valor_meta
                ) * 100

                partes.append(
                    f"Sua meta '{meta['titulo']}' está "
                    f"{percentual:.0f}% concluída."
                )

        if not partes:
            return {
                "resposta": (
                    "Ainda não existem dados suficientes "
                    "para realizar essa análise."
                ),
                "tipo": "resumo",
                "dados": {},
            }

        return {
            "resposta": " ".join(partes),
            "tipo": "resumo",
            "dados": {
                "resumo_financeiro": resumo,
                "investimentos": resumo_investimentos,
                "meta": meta,
            },
        }

    except Exception as erro:
        print(
            f"Erro ao gerar resumo: {erro}"
        )

        return {
            "resposta": (
                "Ainda não existem dados suficientes "
                "para realizar essa análise."
            ),
            "tipo": "erro",
            "dados": {},
        }


def responder_pergunta(pergunta):
    """
    Processa uma pergunta e retorna a resposta do agente.

    Args:
        pergunta (str): Pergunta do usuário.

    Returns:
        dict: Resposta com os campos resposta, tipo e dados.
    """
    print(
        f"[Agent] Processando pergunta: {pergunta}"
    )

    if not pergunta or not pergunta.strip():
        return {
            "resposta": (
                "Por favor, digite uma pergunta."
            ),
            "tipo": "erro",
            "dados": {},
        }

    if len(pergunta) > 500:
        return {
            "resposta": (
                "A pergunta é muito longa. "
                "Por favor, seja mais conciso."
            ),
            "tipo": "erro",
            "dados": {},
        }

    # Perguntas de investimentos são verificadas primeiro,
    # pois podem conter termos que também aparecem em outras
    # intenções, como saldo, rendimento ou quantidade.
    intencao_investimento = (
        identificar_intencao_investimento(pergunta)
    )

    if intencao_investimento:
        print(
            "[Agent] Intenção de investimento: "
            f"{intencao_investimento}"
        )

        return responder_investimentos(
            pergunta
        )

    # Depois das intenções de investimentos, verificamos
    # possíveis categorias mencionadas na pergunta.
    categoria_mencionada = (
        extrair_grupo_categoria_mencionada(pergunta)
    )

    if categoria_mencionada:
        print(
            "[Agent] Categoria mencionada: "
            f"{categoria_mencionada}"
        )

        return responder_categorias_especifica(
            categoria_mencionada
        )

    intencao = identificar_intencao(
        pergunta
    )

    print(
        "[Agent] Intenção identificada: "
        f"{intencao}"
    )

    if intencao == "saldo":
        return responder_saldo()

    if intencao == "entradas":
        return responder_entradas()

    if intencao == "saidas":
        return responder_saidas()

    if intencao == "categorias":
        return responder_categorias(pergunta)

    if intencao == "investimentos":
        return responder_investimentos(pergunta)

    if intencao == "metas":
        return responder_metas()

    if intencao == "transacoes":
        return responder_transacoes(pergunta)

    if intencao == "resumo":
        return responder_resumo()

    return {
        "resposta": (
            "Não consegui identificar exatamente o que "
            "você deseja consultar. Você pode perguntar "
            "sobre saldo, entradas, saídas, categorias, "
            "investimentos, metas ou últimas transações."
        ),
        "tipo": "desconhecido",
        "dados": {},
    }
