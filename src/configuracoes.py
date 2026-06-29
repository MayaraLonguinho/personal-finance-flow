import json
from sqlalchemy import text

from src.auth import obter_usuario_por_id
from src.load import obter_engine


DEFAULTS = {
    "nome": "",
    "tema": "theme-blue",
    "moeda": "BRL",
    "formato_data": "DD/MM/YYYY",
    "qtd_transacoes_recentes": 5,
    "confirmar_exclusao": True,
    "cards_visiveis": [
        "resumo_financeiro",
        "investimentos",
        "transacoes_recentes",
        "meta_economia",
    ],
}

TEMAS_PERMITIDOS = {"theme-blue", "theme-pink", "theme-green", "theme-red", "theme-dark"}
MOEDAS_PERMITIDAS = {"BRL", "USD", "EUR"}
FORMATOS_DATA_PERMITIDOS = {"DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"}
CARDS_PERMITIDOS = set(DEFAULTS["cards_visiveis"])


def garantir_tabela_configuracoes():
    engine = obter_engine()

    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS configuracoes_usuario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL UNIQUE,
                    nome VARCHAR(150) NULL,
                    tema VARCHAR(50) NOT NULL DEFAULT 'theme-blue',
                    moeda VARCHAR(10) NOT NULL DEFAULT 'BRL',
                    formato_data VARCHAR(20) NOT NULL DEFAULT 'DD/MM/YYYY',
                    qtd_transacoes_recentes INT NOT NULL DEFAULT 5,
                    confirmar_exclusao TINYINT(1) NOT NULL DEFAULT 1,
                    cards_visiveis TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )
        )


def _normalizar_cards_visiveis(cards_visiveis):
    if isinstance(cards_visiveis, list):
        return [
            str(item) for item in cards_visiveis
            if str(item) in CARDS_PERMITIDOS
        ]

    if isinstance(cards_visiveis, str):
        try:
            dados = json.loads(cards_visiveis)
            if isinstance(dados, list):
                return [
                    str(item) for item in dados
                    if str(item) in CARDS_PERMITIDOS
                ]
        except (TypeError, ValueError):
            pass

    return list(DEFAULTS["cards_visiveis"])


def _obter_defaults(usuario_id):
    usuario = obter_usuario_por_id(usuario_id) or {}
    defaults = dict(DEFAULTS)
    defaults["nome"] = usuario.get("nome") or ""
    return defaults


def obter_configuracoes_usuario(usuario_id):
    garantir_tabela_configuracoes()
    defaults = _obter_defaults(usuario_id)

    engine = obter_engine()
    with engine.connect() as conexao:
        resultado = conexao.execute(
            text(
                """
                SELECT nome, tema, moeda, formato_data, qtd_transacoes_recentes,
                       confirmar_exclusao, cards_visiveis
                FROM configuracoes_usuario
                WHERE usuario_id = :usuario_id
                """
            ),
            {"usuario_id": usuario_id},
        ).fetchone()

    if resultado is None:
        return defaults

    return {
        "nome": resultado[0] or defaults["nome"],
        "tema": resultado[1] or defaults["tema"],
        "moeda": resultado[2] or defaults["moeda"],
        "formato_data": resultado[3] or defaults["formato_data"],
        "qtd_transacoes_recentes": int(resultado[4] or defaults["qtd_transacoes_recentes"]),
        "confirmar_exclusao": bool(resultado[5]) if resultado[5] is not None else defaults["confirmar_exclusao"],
        "cards_visiveis": _normalizar_cards_visiveis(resultado[6] or defaults["cards_visiveis"]),
    }


def salvar_configuracoes_usuario(usuario_id, dados=None):
    if usuario_id is None:
        raise PermissionError("Usuário não autenticado")

    garantir_tabela_configuracoes()
    atuais = obter_configuracoes_usuario(usuario_id)
    dados = dados or {}

    nome = str(dados.get("nome", atuais["nome"] or "")).strip()[:150]
    tema = str(dados.get("tema") or atuais["tema"])
    moeda = str(dados.get("moeda") or atuais["moeda"])
    formato_data = str(dados.get("formato_data") or atuais["formato_data"])

    if tema not in TEMAS_PERMITIDOS:
        raise ValueError("Tema inválido")
    if moeda not in MOEDAS_PERMITIDAS:
        raise ValueError("Moeda inválida")
    if formato_data not in FORMATOS_DATA_PERMITIDOS:
        raise ValueError("Formato de data inválido")

    try:
        qtd_transacoes_recentes = int(
            dados.get("qtd_transacoes_recentes", atuais["qtd_transacoes_recentes"])
        )
    except (TypeError, ValueError):
        raise ValueError("Quantidade de transações recentes inválida")
    qtd_transacoes_recentes = max(3, min(20, qtd_transacoes_recentes))

    confirmar_exclusao = dados.get("confirmar_exclusao", atuais["confirmar_exclusao"])
    if isinstance(confirmar_exclusao, str):
        confirmar_exclusao = confirmar_exclusao.lower() in {"1", "true", "sim", "yes", "on"}
    confirmar_exclusao = bool(confirmar_exclusao)

    cards_visiveis = _normalizar_cards_visiveis(
        dados.get("cards_visiveis", atuais["cards_visiveis"])
    )

    engine = obter_engine()
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                INSERT INTO configuracoes_usuario (
                    usuario_id, nome, tema, moeda, formato_data,
                    qtd_transacoes_recentes, confirmar_exclusao, cards_visiveis
                )
                VALUES (
                    :usuario_id, :nome, :tema, :moeda, :formato_data,
                    :qtd_transacoes_recentes, :confirmar_exclusao, :cards_visiveis
                )
                ON DUPLICATE KEY UPDATE
                    nome = VALUES(nome),
                    tema = VALUES(tema),
                    moeda = VALUES(moeda),
                    formato_data = VALUES(formato_data),
                    qtd_transacoes_recentes = VALUES(qtd_transacoes_recentes),
                    confirmar_exclusao = VALUES(confirmar_exclusao),
                    cards_visiveis = VALUES(cards_visiveis)
                """
            ),
            {
                "usuario_id": usuario_id,
                "nome": nome,
                "tema": tema,
                "moeda": moeda,
                "formato_data": formato_data,
                "qtd_transacoes_recentes": qtd_transacoes_recentes,
                "confirmar_exclusao": confirmar_exclusao,
                "cards_visiveis": json.dumps(cards_visiveis),
            },
        )

    return {
        "nome": nome,
        "tema": tema,
        "moeda": moeda,
        "formato_data": formato_data,
        "qtd_transacoes_recentes": qtd_transacoes_recentes,
        "confirmar_exclusao": confirmar_exclusao,
        "cards_visiveis": cards_visiveis,
    }


def restaurar_configuracoes_padrao(usuario_id):
    defaults = _obter_defaults(usuario_id)
    return salvar_configuracoes_usuario(usuario_id, defaults)
