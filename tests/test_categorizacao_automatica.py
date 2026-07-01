import unittest
from unittest.mock import patch

import pandas as pd

from src.categorization import (
    categorizar_transacao,
    normalizar_texto,
)
from src.load import carregar_transacoes_mysql
from src.transform import tratar_transacoes


class TestCategorizacaoAutomatica(unittest.TestCase):
    def test_normaliza_texto_com_acentos_maiusculas_e_espacos(self):
        self.assertEqual(
            normalizar_texto("  ÁGUA   Mineral "),
            "agua mineral",
        )

    def test_preserva_categoria_do_csv_quando_valida_para_o_usuario(self):
        categoria, foi_categorizada = categorizar_transacao(
            descricao="Compra no mercado do bairro",
            categoria_atual="  alimentacao ",
            tipo_transacao="saida",
            categorias_usuario={
                "Alimentação": ["mercado", "restaurante"],
                "Outros": [],
            },
        )

        self.assertEqual(categoria, "Alimentação")
        self.assertFalse(foi_categorizada)

    def test_aplica_regra_por_descricao_tipo_e_palavra_chave(self):
        categoria, foi_categorizada = categorizar_transacao(
            descricao="  FOLHA   de pagamento empresa x ",
            categoria_atual=None,
            tipo_transacao="entrada",
        )

        self.assertEqual(categoria, "Salário")
        self.assertTrue(foi_categorizada)

    def test_categoria_nao_reconhecida_vira_outros(self):
        categoria, foi_categorizada = categorizar_transacao(
            descricao="Compra aleatória sem padrão",
            categoria_atual="Sem categoria",
            tipo_transacao="saida",
        )

        self.assertEqual(categoria, "Outros")
        self.assertTrue(foi_categorizada)

    @patch("src.transform.obter_regras_categorizacao_do_banco")
    @patch("src.transform.inicializar_categorias_padrao")
    def test_tratar_transacoes_considera_categoria_do_usuario(self, mock_inicializar, mock_regras):
        mock_regras.return_value = {
            "Salário": ["salario", "folha"],
            "Alimentação": ["mercado", "restaurante"],
            "Casa": ["aluguel", "agua", "energia"],
            "Transportes": ["uber", "combustivel"],
            "Lazer": ["cinema", "streaming"],
            "Saúde": ["farmacia", "hospital"],
            "Educação": ["curso", "faculdade"],
            "Outros": [],
        }

        df = pd.DataFrame(
            [
                {
                    "Data": "2026-01-05",
                    "Descricao": " Uber   viagem ",
                    "Categoria": "invalida",
                    "Tipo": "Despesa",
                    "Valor": "35.50",
                    "Status": "Concluído",
                },
                {
                    "Data": "2026-01-06",
                    "Descricao": "Restaurante da esquina",
                    "Categoria": " ALIMENTACAO ",
                    "Tipo": "Saída",
                    "Valor": "52.00",
                    "Status": "confirmado",
                },
            ]
        )

        df_tratado, contador = tratar_transacoes(df, usuario_id=42)

        mock_inicializar.assert_called_once_with(usuario_id=42)
        mock_regras.assert_called_once_with(usuario_id=42)
        self.assertEqual(df_tratado.iloc[0]["categoria"], "Transportes")
        self.assertEqual(df_tratado.iloc[1]["categoria"], "Alimentação")
        self.assertEqual(contador, 1)

    @patch("pandas.DataFrame.to_sql")
    @patch("pandas.read_sql")
    @patch("src.load.obter_engine")
    def test_carregar_transacoes_preserva_categoria_formatada(self, mock_engine, mock_read_sql, mock_to_sql):
        mock_engine.return_value = object()
        mock_read_sql.return_value = pd.DataFrame(
            columns=[
                "usuario_id",
                "data_transacao",
                "descricao",
                "categoria",
                "tipo",
                "valor",
                "conta",
                "instituicao",
                "status",
            ]
        )

        df = pd.DataFrame(
            [
                {
                    "data": "2026-01-10",
                    "descricao": "  Conta de água  ",
                    "categoria": "Casa",
                    "tipo": "saida",
                    "valor": 120,
                    "conta": "Conta Corrente",
                    "instituicao": "Banco X",
                    "status": "confirmado",
                }
            ]
        )

        carregar_transacoes_mysql(df, usuario_id=77)

        dataframe_enviado = mock_to_sql.call_args[0][0]
        self.assertEqual(dataframe_enviado.iloc[0]["categoria"], "Casa")
        self.assertEqual(dataframe_enviado.iloc[0]["descricao"], "Conta de água")


if __name__ == "__main__":
    unittest.main()
