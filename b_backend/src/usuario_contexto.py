from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional

_USUARIO_ID_ATUAL: ContextVar[Optional[int]] = ContextVar("usuario_id_atual", default=None)


def definir_usuario_id(usuario_id: Optional[int]) -> None:
    """Define o usuário ativo para o contexto atual da requisição."""
    _USUARIO_ID_ATUAL.set(usuario_id)


def limpar_usuario_id() -> None:
    """Remove o usuário ativo do contexto atual."""
    _USUARIO_ID_ATUAL.set(None)


def obter_usuario_id() -> Optional[int]:
    """Retorna o usuário ativo para o contexto atual."""
    return _USUARIO_ID_ATUAL.get()


@contextmanager
def contexto_usuario(usuario_id: Optional[int]) -> Iterator[None]:
    """Context manager que aplica o usuário da sessão durante a execução."""
    token = _USUARIO_ID_ATUAL.set(usuario_id)
    try:
        yield
    finally:
        _USUARIO_ID_ATUAL.reset(token)
