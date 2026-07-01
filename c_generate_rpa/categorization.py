"""Módulo de categorização automática."""

import unicodedata

import pandas as pd


REGRAS_CATEGORIZACAO_PADRAO = {
    "Salário": [
        "salario",
        "salário",
        "folha",
        "holerite",
        "pagamento",
        "proventos",
        "remuneracao",
        "remuneração",
    ],
    "Alimentação": [
        "mercado",
        "supermercado",
        "restaurante",
        "ifood",
        "padaria",
        "lanchonete",
        "delivery",
    ],
    "Casa": [
        "aluguel",
        "agua",
        "água",
        "energia",
        "luz",
        "condominio",
        "condomínio",
        "internet",
        "gas",
        "gás",
    ],
    "Transportes": [
        "uber",
        "99",
        "combustivel",
        "combustível",
        "gasolina",
        "onibus",
        "ônibus",
        "metro",
        "metrô",
        "taxi",
        "transporte",
    ],
    "Lazer": [
        "cinema",
        "streaming",
        "netflix",
        "spotify",
        "show",
        "teatro",
        "parque",
        "viagem",
    ],
    "Saúde": [
        "farmacia",
        "farmácia",
        "hospital",
        "consulta",
        "medico",
        "médico",
        "dentista",
        "remedio",
        "remédio",
    ],
    "Educação": [
        "curso",
        "faculdade",
        "universidade",
        "escola",
        "mensalidade",
        "livro",
        "material",
        "bootcamp",
    ],
    "Investimentos": [
        "tesouro",
        "cdb",
        "fundo",
        "acoes",
        "ações",
        "bolsa",
        "aplicacao",
        "aplicação",
    ],
    "Outros": [],
}

TIPOS_NORMALIZADOS = {
    "receita": "entrada",
    "entrada": "entrada",
    "despesa": "saida",
    "saída": "saida",
    "saida": "saida",
    "investimento": "investimento",
}


def normalizar_texto(valor):
    """Normaliza texto removendo acentos, caixa e espaços excedentes."""
    if valor is None:
        return None

    if not isinstance(valor, str):
        valor = str(valor)

    valor = " ".join(valor.split()).strip()
    if not valor:
        return None

    valor = valor.lower()
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(
        caractere
        for caractere in valor
        if not unicodedata.combining(caractere)
    )
    return valor


def normalizar_descricao(descricao):
    """Compatibilidade para código legado."""
    return normalizar_texto(descricao)


def obter_regras_categorizacao():
    """
    Retorna as regras de categorização padrão.
    
    Esta função é usada como fallback quando não há categorias no banco.
    
    Returns:
        dict: Dicionário com categorias e palavras-chave
    """
    return {
        nome: list(palavras_chave)
        for nome, palavras_chave in REGRAS_CATEGORIZACAO_PADRAO.items()
    }


def _iterar_fontes_regras(fonte):
    if not fonte:
        return []

    if isinstance(fonte, dict):
        return list(fonte.items())

    if isinstance(fonte, list):
        itens = []
        for item in fonte:
            if isinstance(item, dict) and item.get("nome"):
                itens.append(
                    (
                        item["nome"],
                        item.get("palavras_chave", []),
                    )
                )
        return itens

    return []


def _construir_catalogo_categorias(regras_categorizacao=None, categorias_usuario=None):
    catalogo = {}

    def registrar(nome, palavras_chave, prioridade):
        chave = normalizar_texto(nome)
        if not chave:
            return

        keywords_normalizadas = [
            keyword
            for keyword in (
                normalizar_texto(palavra)
                for palavra in (palavras_chave or [])
            )
            if keyword
        ]

        if chave not in catalogo:
            catalogo[chave] = {
                "nome": nome,
                "palavras_chave": [],
                "prioridade": prioridade,
            }
        elif prioridade >= catalogo[chave]["prioridade"]:
            catalogo[chave]["nome"] = nome
            catalogo[chave]["prioridade"] = prioridade

        existentes = catalogo[chave]["palavras_chave"]
        for palavra in keywords_normalizadas:
            if palavra not in existentes:
                existentes.append(palavra)

    for nome, palavras_chave in REGRAS_CATEGORIZACAO_PADRAO.items():
        registrar(nome, palavras_chave, prioridade=0)

    for nome, palavras_chave in _iterar_fontes_regras(regras_categorizacao):
        registrar(nome, palavras_chave, prioridade=1)

    for nome, palavras_chave in _iterar_fontes_regras(categorias_usuario):
        registrar(nome, palavras_chave, prioridade=2)

    return catalogo


def _obter_nome_categoria(catalogo, nome_padrao):
    chave = normalizar_texto(nome_padrao)
    if chave in catalogo:
        return catalogo[chave]["nome"]
    return nome_padrao


def _resolver_categoria_informada(categoria_informada, catalogo):
    chave = normalizar_texto(categoria_informada)
    if not chave:
        return None
    categoria = catalogo.get(chave)
    return categoria["nome"] if categoria else None


def _nomes_prioritarios_por_tipo(tipo_transacao):
    tipo_normalizado = TIPOS_NORMALIZADOS.get(
        normalizar_texto(tipo_transacao),
        normalizar_texto(tipo_transacao),
    )

    if tipo_normalizado == "entrada":
        return ["Salário"]

    if tipo_normalizado == "saida":
        return [
            "Alimentação",
            "Casa",
            "Transportes",
            "Lazer",
            "Saúde",
            "Educação",
        ]

    return []


def _categorias_bloqueadas_por_tipo(tipo_transacao):
    tipo_normalizado = TIPOS_NORMALIZADOS.get(
        normalizar_texto(tipo_transacao),
        normalizar_texto(tipo_transacao),
    )

    if tipo_normalizado == "entrada":
        return {
            "Alimentação",
            "Casa",
            "Transportes",
            "Lazer",
            "Saúde",
            "Educação",
        }

    if tipo_normalizado == "saida":
        return {"Salário"}

    return set()


def _buscar_categoria_por_palavra_chave(descricao_normalizada, catalogo, ordem_categorias):
    for nome_categoria in ordem_categorias:
        chave_categoria = normalizar_texto(nome_categoria)
        categoria = catalogo.get(chave_categoria)
        if not categoria:
            continue
        for palavra_chave in categoria["palavras_chave"]:
            if palavra_chave and palavra_chave in descricao_normalizada:
                return categoria["nome"]
    return None


def categorizar_transacao(
    descricao,
    categoria_atual=None,
    regras_categorizacao=None,
    tipo_transacao=None,
    categorias_usuario=None,
):
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
    catalogo = _construir_catalogo_categorias(
        regras_categorizacao=regras_categorizacao,
        categorias_usuario=categorias_usuario,
    )

    categoria_informada = _resolver_categoria_informada(
        categoria_atual,
        catalogo,
    )
    nome_outros = _obter_nome_categoria(catalogo, "Outros")

    if categoria_informada and normalizar_texto(categoria_informada) != normalizar_texto("Outros"):
        return categoria_informada, False

    descricao_normalizada = normalizar_texto(descricao)
    if not descricao_normalizada:
        return nome_outros, categoria_informada != nome_outros

    ordem_prioritaria = _nomes_prioritarios_por_tipo(tipo_transacao)
    categoria_por_regra = _buscar_categoria_por_palavra_chave(
        descricao_normalizada,
        catalogo,
        ordem_prioritaria,
    )
    if categoria_por_regra:
        return categoria_por_regra, True

    categorias_bloqueadas = {
        normalizar_texto(nome)
        for nome in _categorias_bloqueadas_por_tipo(tipo_transacao)
    }
    demais_categorias = [
        dados["nome"]
        for chave, dados in catalogo.items()
        if (
            dados["nome"] not in ordem_prioritaria
            and chave != normalizar_texto("Outros")
            and chave not in categorias_bloqueadas
        )
    ]
    categoria_por_regra = _buscar_categoria_por_palavra_chave(
        descricao_normalizada,
        catalogo,
        demais_categorias,
    )
    if categoria_por_regra:
        return categoria_por_regra, True

    return nome_outros, categoria_informada != nome_outros


def categorizar_dataframe(df, regras_categorizacao=None, categorias_usuario=None):
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

    if 'descricao' not in df.columns or 'categoria' not in df.columns:
        return df, 0

    if regras_categorizacao is None and categorias_usuario is None:
        regras_categorizacao = obter_regras_categorizacao()

    df = df.copy()
    for index, row in df.iterrows():
        descricao = row['descricao']
        categoria_atual = row['categoria']
        tipo_transacao = row['tipo'] if 'tipo' in df.columns else None

        if pd.isna(categoria_atual):
            categoria_atual = None

        categoria_sugerida, foi_categorizada = categorizar_transacao(
            descricao,
            categoria_atual,
            regras_categorizacao=regras_categorizacao,
            tipo_transacao=tipo_transacao,
            categorias_usuario=categorias_usuario,
        )

        if categoria_sugerida != categoria_atual:
            df.at[index, 'categoria'] = categoria_sugerida

        if foi_categorizada:
            contador += 1

    return df, contador
