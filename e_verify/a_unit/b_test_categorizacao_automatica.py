import unittest
from unittest.mock import patch

import pandas as pd

from c_generate_rpa.c_categorization import (
    categorizar_transacao,
    normalizar_texto,
)
from c_generate_rpa.d_load import carregar_transacoes_mysql
from c_generate_rpa.b_transform import tratar_transacoes


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

    @patch("c_generate_rpa.b_transform.obter_regras_categorizacao_do_banco")
    @patch("c_generate_rpa.b_transform.inicializar_categorias_padrao")
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



if __name__ == "__main__":
    unittest.main()
