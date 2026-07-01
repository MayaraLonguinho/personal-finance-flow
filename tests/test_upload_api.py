import io
import unittest
from unittest.mock import patch

from app import app


class UploadApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["WTF_CSRF_CHECK_DEFAULT"] = False

    def setUp(self):
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 99
            sess["usuario_nome"] = "Usuário de Teste"

    @patch("src.transform.obter_regras_categorizacao_do_banco")
    @patch("src.transform.inicializar_categorias_padrao")
    @patch("app.carregar_transacoes_mysql")
    def test_upload_csv_valido(self, mock_carregar, _mock_inicializar, mock_regras):
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
        mock_carregar.return_value = {
            "recebidos": 1,
            "importados": 1,
            "ignorados": 0,
            "linhas_ignoradas_duplicadas": [],
        }

        conteudo = (
            "data,descricao,categoria,tipo,valor,status\n"
            "2026-01-10,Restaurante do centro,,despesa,54.90,confirmado\n"
        )

        response = self.client.post(
            "/api/upload",
            data={
                "arquivo": (io.BytesIO(conteudo.encode("utf-8")), "transacoes.csv"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["importados"], 1)
        self.assertEqual(payload["relatorio"]["linhas_aceitas"], 1)
        self.assertEqual(payload["relatorio"]["linhas_rejeitadas"], 0)

    @patch("src.transform.obter_regras_categorizacao_do_banco")
    @patch("src.transform.inicializar_categorias_padrao")
    def test_upload_csv_invalido(self, _mock_inicializar, mock_regras):
        mock_regras.return_value = {
            "Outros": [],
        }

        conteudo = (
            "data,descricao,categoria,tipo,valor,status\n"
            "data-invalida,Compra livre,,despesa,abc,confirmado\n"
        )

        response = self.client.post(
            "/api/upload",
            data={
                "arquivo": (io.BytesIO(conteudo.encode("utf-8")), "invalido.csv"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["erro"], "Nenhuma linha válida foi encontrada no CSV.")
        self.assertEqual(payload["relatorio"]["linhas_aceitas"], 0)
        self.assertEqual(payload["relatorio"]["linhas_rejeitadas"], 1)

    def test_upload_csv_vazio(self):
        response = self.client.post(
            "/api/upload",
            data={
                "arquivo": (io.BytesIO(b""), "vazio.csv"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["erro"], "O arquivo CSV está vazio.")

    @patch("src.transform.obter_regras_categorizacao_do_banco")
    @patch("src.transform.inicializar_categorias_padrao")
    @patch("app.carregar_transacoes_mysql")
    def test_upload_csv_duplicado(self, mock_carregar, _mock_inicializar, mock_regras):
        mock_regras.return_value = {
            "Transportes": ["uber", "combustivel"],
            "Outros": [],
        }
        mock_carregar.return_value = {
            "recebidos": 1,
            "importados": 1,
            "ignorados": 0,
            "linhas_ignoradas_duplicadas": [],
        }

        conteudo = (
            "data,descricao,categoria,tipo,valor,status\n"
            "2026-01-10,Uber viagem,,despesa,30,confirmado\n"
            "2026-01-10,Uber viagem,,despesa,30,confirmado\n"
        )

        response = self.client.post(
            "/api/upload",
            data={
                "arquivo": (io.BytesIO(conteudo.encode("utf-8")), "duplicado.csv"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["importados"], 1)
        self.assertEqual(payload["relatorio"]["linhas_aceitas"], 1)
        self.assertEqual(payload["relatorio"]["linhas_rejeitadas"], 1)
        self.assertEqual(
            payload["relatorio"]["rejeicoes"][0]["motivo"],
            "linha duplicada no arquivo",
        )

    def test_upload_extensao_invalida(self):
        response = self.client.post(
            "/api/upload",
            data={
                "arquivo": (io.BytesIO(b"conteudo qualquer"), "arquivo.txt"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["erro"], "Envie apenas arquivos CSV.")


if __name__ == "__main__":
    unittest.main()
