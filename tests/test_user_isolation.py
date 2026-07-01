import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app


class FakeEngine:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def connect(self):
        return FakeConnection(self)

    def begin(self):
        return FakeConnection(self)


class FakeConnection:
    def __init__(self, engine):
        self._engine = engine

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, parameters=None):
        parameters = parameters or {}
        sql = " ".join(str(statement).split())
        self._engine.calls.append((sql, dict(parameters)))
        for marker, rows in self._engine.responses.items():
            if marker in sql:
                return FakeResult(rows)
        return FakeResult([])

    def commit(self):
        pass


class FakeResult:
    def __init__(self, rows):
        self._rows = rows
        self.rowcount = len(rows)

    def mappings(self):
        return FakeMappings(self._rows)

    def fetchone(self):
        if self._rows:
            return self._rows[0]
        return None

    def fetchall(self):
        return self._rows

    def __iter__(self):
        for row in self._rows:
            yield row


class FakeMappings:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class TestUserIsolation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_transacoes_isoladas(self):
        """Test that user B can't access user A's transactions"""
        with patch('app.obter_engine') as mock_engine:
            # Create a mock engine
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # First, log in as user A (simulate session)
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
                sess['usuario_nome'] = 'Usuário A'

            # Try to access transactions (should only see user 1's)
            response = self.app.get('/api/transacoes/todas')
            self.assertEqual(response.status_code, 200)

            # Now check that the query uses usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found, "Query should use usuario_id=1 for user A")

            # Now log in as user B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
                sess['usuario_nome'] = 'Usuário B'

            # Try to access transactions (should only see user 2's)
            response = self.app.get('/api/transacoes/todas')
            self.assertEqual(response.status_code, 200)

            # Check that the query uses usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found, "Query should use usuario_id=2 for user B")

    def test_categorias_isoladas(self):
        """Test that user B can't access user A's categories"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/categorias')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/categorias')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)

    def test_metas_isoladas(self):
        """Test that user B can't access user A's goals"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/meta')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/meta')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)

    def test_investimentos_isolados(self):
        """Test that user B can't access user A's investments"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/investimentos')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/investimentos')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)

    def test_configuracoes_isoladas(self):
        """Test that user B can't access user A's settings"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/configuracoes')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/configuracoes')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)

    def test_relatorios_isolados(self):
        """Test that user B can't access user A's reports"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/relatorios')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/relatorios')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)

    def test_dashboard_isolado(self):
        """Test that user B can't access user A's dashboard data"""
        with patch('app.obter_engine') as mock_engine:
            fake_engine = FakeEngine()
            mock_engine.return_value = fake_engine

            # User A
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 1
            response = self.app.get('/api/metricas')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=1
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 1:
                    found = True
            self.assertTrue(found)

            # User B
            fake_engine.calls.clear()
            with self.app.session_transaction() as sess:
                sess['usuario_id'] = 2
            response = self.app.get('/api/metricas')
            self.assertEqual(response.status_code, 200)

            # Check usuario_id=2
            found = False
            for sql, params in fake_engine.calls:
                if 'usuario_id' in params and params['usuario_id'] == 2:
                    found = True
            self.assertTrue(found)


if __name__ == '__main__':
    unittest.main()
