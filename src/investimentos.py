from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from src.load import obter_engine


STATUS_PERMITIDOS = {
    "ativo",
    "resgatado",
    "cancelado",
}


def converter_valor(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, (date, datetime)):
        return valor.isoformat()

    return valor


def converter_registro(registro: Any) -> Dict[str, Any]:
    return {
        chave: converter_valor(valor)
        for chave, valor in registro.items()
    }


def normalizar_texto(valor: Any) -> Optional[str]:
    if valor is None:
        return None

    texto_normalizado = str(valor).strip()

    if not texto_normalizado:
        return None

    return texto_normalizado


def converter_decimal(
    valor: Any,
    campo: str,
    obrigatorio: bool = True,
) -> Optional[Decimal]:
    if valor is None or valor == "":
        if obrigatorio:
            raise ValueError(
                f"O campo {campo} é obrigatório."
            )

        return None

    try:
        valor_convertido = Decimal(str(valor))
    except (ValueError, TypeError, ArithmeticError) as erro:
        raise ValueError(
            f"O campo {campo} deve ser um número válido."
        ) from erro

    return valor_convertido


def validar_data(
    valor: Any,
    campo: str,
    obrigatorio: bool = True,
) -> Optional[str]:
    if valor is None or valor == "":
        if obrigatorio:
            raise ValueError(
                f"O campo {campo} é obrigatório."
            )

        return None

    try:
        data_validada = datetime.strptime(
            str(valor),
            "%Y-%m-%d",
        )

        return data_validada.strftime("%Y-%m-%d")

    except ValueError as erro:
        raise ValueError(
            f"O campo {campo} deve estar no formato YYYY-MM-DD."
        ) from erro


def validar_dados_investimento(
    dados: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(dados, dict):
        raise ValueError(
            "Os dados do investimento são inválidos."
        )

    nome = normalizar_texto(dados.get("nome"))
    tipo = normalizar_texto(dados.get("tipo"))
    instituicao = normalizar_texto(
        dados.get("instituicao")
    )

    if not nome:
        raise ValueError(
            "O campo nome é obrigatório."
        )

    if len(nome) > 150:
        raise ValueError(
            "O nome deve possuir no máximo 150 caracteres."
        )

    if not tipo:
        raise ValueError(
            "O campo tipo é obrigatório."
        )

    if len(tipo) > 80:
        raise ValueError(
            "O tipo deve possuir no máximo 80 caracteres."
        )

    if instituicao and len(instituicao) > 120:
        raise ValueError(
            "A instituição deve possuir no máximo 120 caracteres."
        )

    valor_aplicado = converter_decimal(
        dados.get("valor_aplicado"),
        "valor_aplicado",
    )

    valor_atual = converter_decimal(
        dados.get("valor_atual"),
        "valor_atual",
    )

    rentabilidade_percentual = converter_decimal(
        dados.get("rentabilidade_percentual", 0),
        "rentabilidade_percentual",
        obrigatorio=False,
    )

    if rentabilidade_percentual is None:
        rentabilidade_percentual = Decimal("0")

    if valor_aplicado <= 0:
        raise ValueError(
            "O valor aplicado deve ser maior que zero."
        )

    if valor_atual < 0:
        raise ValueError(
            "O valor atual não pode ser negativo."
        )

    data_aplicacao = validar_data(
        dados.get("data_aplicacao"),
        "data_aplicacao",
    )

    data_vencimento = validar_data(
        dados.get("data_vencimento"),
        "data_vencimento",
        obrigatorio=False,
    )

    if (
        data_vencimento
        and data_vencimento < data_aplicacao
    ):
        raise ValueError(
            "A data de vencimento não pode ser anterior "
            "à data de aplicação."
        )

    status = normalizar_texto(
        dados.get("status", "ativo")
    )

    status = (
        status.lower()
        if status
        else "ativo"
    )

    if status not in STATUS_PERMITIDOS:
        raise ValueError(
            "O status deve ser ativo, resgatado ou cancelado."
        )

    return {
        "nome": nome,
        "tipo": tipo,
        "instituicao": instituicao,
        "valor_aplicado": valor_aplicado,
        "valor_atual": valor_atual,
        "rentabilidade_percentual": (
            rentabilidade_percentual
        ),
        "data_aplicacao": data_aplicacao,
        "data_vencimento": data_vencimento,
        "status": status,
    }


def listar_investimentos(
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    parametros: Dict[str, Any] = {}

    consulta = """
        SELECT
            id,
            nome,
            tipo,
            instituicao,
            valor_aplicado,
            valor_atual,
            rentabilidade_percentual,
            data_aplicacao,
            data_vencimento,
            status,
            criado_em,
            atualizado_em
        FROM investimentos
    """

    if status:
        status_normalizado = status.strip().lower()

        if status_normalizado not in STATUS_PERMITIDOS:
            raise ValueError(
                "O status informado é inválido."
            )

        consulta += " WHERE status = :status"
        parametros["status"] = status_normalizado

    consulta += " ORDER BY data_aplicacao DESC, id DESC"

    engine = obter_engine()

    with engine.connect() as conexao:
        registros = conexao.execute(
            text(consulta),
            parametros,
        ).mappings().all()

    return [
        converter_registro(registro)
        for registro in registros
    ]


def buscar_investimento_por_id(
    investimento_id: int,
) -> Optional[Dict[str, Any]]:
    consulta = text(
        """
        SELECT
            id,
            nome,
            tipo,
            instituicao,
            valor_aplicado,
            valor_atual,
            rentabilidade_percentual,
            data_aplicacao,
            data_vencimento,
            status,
            criado_em,
            atualizado_em
        FROM investimentos
        WHERE id = :id
        LIMIT 1
        """
    )

    engine = obter_engine()

    with engine.connect() as conexao:
        registro = conexao.execute(
            consulta,
            {
                "id": investimento_id,
            },
        ).mappings().first()

    if not registro:
        return None

    return converter_registro(registro)


def criar_investimento(
    dados: Dict[str, Any],
) -> Dict[str, Any]:
    investimento = validar_dados_investimento(
        dados
    )

    consulta = text(
        """
        INSERT INTO investimentos (
            nome,
            tipo,
            instituicao,
            valor_aplicado,
            valor_atual,
            rentabilidade_percentual,
            data_aplicacao,
            data_vencimento,
            status
        )
        VALUES (
            :nome,
            :tipo,
            :instituicao,
            :valor_aplicado,
            :valor_atual,
            :rentabilidade_percentual,
            :data_aplicacao,
            :data_vencimento,
            :status
        )
        """
    )

    engine = obter_engine()

    with engine.begin() as conexao:
        resultado = conexao.execute(
            consulta,
            investimento,
        )

        investimento_id = resultado.lastrowid

    investimento_criado = buscar_investimento_por_id(
        investimento_id
    )

    if not investimento_criado:
        raise RuntimeError(
            "O investimento foi criado, mas não pôde ser consultado."
        )

    return investimento_criado


def atualizar_investimento(
    investimento_id: int,
    dados: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    investimento_existente = buscar_investimento_por_id(
        investimento_id
    )

    if not investimento_existente:
        return None

    investimento = validar_dados_investimento(
        dados
    )

    consulta = text(
        """
        UPDATE investimentos
        SET
            nome = :nome,
            tipo = :tipo,
            instituicao = :instituicao,
            valor_aplicado = :valor_aplicado,
            valor_atual = :valor_atual,
            rentabilidade_percentual = :rentabilidade_percentual,
            data_aplicacao = :data_aplicacao,
            data_vencimento = :data_vencimento,
            status = :status
        WHERE id = :id
        """
    )

    parametros = {
        **investimento,
        "id": investimento_id,
    }

    engine = obter_engine()

    with engine.begin() as conexao:
        conexao.execute(
            consulta,
            parametros,
        )

    return buscar_investimento_por_id(
        investimento_id
    )


def excluir_investimento(
    investimento_id: int,
) -> bool:
    consulta = text(
        """
        DELETE FROM investimentos
        WHERE id = :id
        """
    )

    engine = obter_engine()

    with engine.begin() as conexao:
        resultado = conexao.execute(
            consulta,
            {
                "id": investimento_id,
            },
        )

    return resultado.rowcount > 0


def obter_resumo_investimentos() -> Dict[str, Any]:
    consulta_resumo = text(
        """
        SELECT
            COUNT(*) AS quantidade_total,

            COALESCE(
                SUM(
                    CASE
                        WHEN status = 'ativo'
                        THEN valor_aplicado
                        ELSE 0
                    END
                ),
                0
            ) AS total_aplicado,

            COALESCE(
                SUM(
                    CASE
                        WHEN status = 'ativo'
                        THEN valor_atual
                        ELSE 0
                    END
                ),
                0
            ) AS valor_atual_total,

            COALESCE(
                SUM(
                    CASE
                        WHEN status = 'ativo'
                        THEN valor_atual - valor_aplicado
                        ELSE 0
                    END
                ),
                0
            ) AS lucro_prejuizo,

            SUM(
                CASE
                    WHEN status = 'ativo'
                    THEN 1
                    ELSE 0
                END
            ) AS quantidade_ativos
        FROM investimentos
        """
    )

    consulta_tipos = text(
        """
        SELECT
            tipo,
            COUNT(*) AS quantidade,
            COALESCE(SUM(valor_atual), 0) AS valor_atual
        FROM investimentos
        WHERE status = 'ativo'
        GROUP BY tipo
        ORDER BY valor_atual DESC
        """
    )

    engine = obter_engine()

    with engine.connect() as conexao:
        resumo = conexao.execute(
            consulta_resumo
        ).mappings().first()

        tipos = conexao.execute(
            consulta_tipos
        ).mappings().all()

    total_aplicado = float(
        resumo["total_aplicado"] or 0
    )

    valor_atual_total = float(
        resumo["valor_atual_total"] or 0
    )

    lucro_prejuizo = float(
        resumo["lucro_prejuizo"] or 0
    )

    rentabilidade_total = (
        (lucro_prejuizo / total_aplicado) * 100
        if total_aplicado > 0
        else 0
    )

    distribuicao = [
        {
            "tipo": registro["tipo"],
            "quantidade": int(
                registro["quantidade"] or 0
            ),
            "valor_atual": float(
                registro["valor_atual"] or 0
            ),
        }
        for registro in tipos
    ]

    return {
        "quantidade_total": int(
            resumo["quantidade_total"] or 0
        ),
        "quantidade_ativos": int(
            resumo["quantidade_ativos"] or 0
        ),
        "total_aplicado": total_aplicado,
        "valor_atual_total": valor_atual_total,
        "lucro_prejuizo": lucro_prejuizo,
        "rentabilidade_total": rentabilidade_total,
        "distribuicao_por_tipo": distribuicao,
    }