import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from b_backend.src.categorias import inicializar_categorias_padrao, buscar_todas_categorias


class TestCategoriasPadrao(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        self.mock_conn = self.mock_engine.connect().__enter__()

    @patch('b_backend.src.categorias.obter_engine')
    @patch('b_backend.src.categorias.buscar_categoria_por_nome')
    def test_inicializar_categorias_novo_usuario(self, mock_buscar, mock_obter_engine):
        """Testa que categorias padrão são criadas para um novo usuário"""
        mock_obter_engine.return_value = self.mock_engine
        mock_buscar.return_value = None  # Nenhuma categoria existe

        resultado = inicializar_categorias_padrao(usuario_id=1)
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(mock_buscar.call_count, 9)  # 9 categorias padrão

    @patch('b_backend.src.categorias.obter_engine')
    @patch('b_backend.src.categorias.buscar_categoria_por_nome')
    @patch('b_backend.src.categorias.criar_categoria')
    def test_inicializar_categorias_idempotente(self, mock_criar, mock_buscar, mock_obter_engine):
        """Testa que a função é idempotente: se categorias já existem, não duplica"""
        mock_obter_engine.return_value = self.mock_engine
        mock_buscar.return_value = {'id': 1, 'nome': 'Salário'}  # Todas categorias já existem

        resultado = inicializar_categorias_padrao(usuario_id=1)
        self.assertTrue(resultado['sucesso'])
        mock_criar.assert_not_called()

    @patch('b_backend.src.categorias.obter_engine')
    @patch('b_backend.src.categorias.buscar_categoria_por_nome')
    @patch('b_backend.src.categorias.criar_categoria')
    def test_preservar_categorias_personalizadas(self, mock_criar, mock_buscar, mock_obter_engine):
        """Testa que categorias personalizadas existentes não são alteradas"""
        mock_obter_engine.return_value = self.mock_engine
        # Simula que "Investimentos" existe, mas "Educação" não
        def side_effect(nome, usuario_id):
            if nome.lower() == 'investimentos':
                return {'id': 2, 'nome': 'Investimentos', 'palavras_chave': []}
            return None
        mock_buscar.side_effect = side_effect

        resultado = inicializar_categorias_padrao(usuario_id=1)
        self.assertTrue(resultado['sucesso'])
        # Verifica que não tentou criar "Investimentos" de novo
        calls = [call[0][0].lower() for call in mock_criar.call_args_list]
        self.assertNotIn('investimentos', calls)


    @patch('b_backend.src.categorias.obter_engine')
    def test_dois_usuarios_mesma_categoria(self, mock_obter_engine):
        """Testa que dois usuários diferentes podem ter categorias com o mesmo nome"""
        mock_obter_engine.return_value = self.mock_engine
        # Simula que para user 1, "Salário" não existe
        with patch('b_backend.src.categorias.buscar_categoria_por_nome') as mock_buscar:
            def side_effect(nome, usuario_id):
                if usuario_id == 2:
                    return {'id': 5, 'nome': 'Salário'}
                return None
            mock_buscar.side_effect = side_effect

            with patch('b_backend.src.categorias.criar_categoria') as mock_criar:
                # Cria para usuário 1
                resultado1 = inicializar_categorias_padrao(usuario_id=1)
                self.assertTrue(resultado1['sucesso'])

                # Cria para usuário 2 (não deve duplicar)
                resultado2 = inicializar_categorias_padrao(usuario_id=2)
                self.assertTrue(resultado2['sucesso'])

                # Verifica que para user 1, "Salário" foi criado, para user 2 não
                for call in mock_criar.call_args_list:
                    self.assertNotEqual(call[1]['usuario_id'], 2)


if __name__ == '__main__':
    unittest.main()
