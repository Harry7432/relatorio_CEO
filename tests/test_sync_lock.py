from types import SimpleNamespace
import pytest
from src import sync_lock


class FakeCursor:
    def __init__(self, lock_result: bool = True):
        self.lock_result = lock_result
        self.executed_queries: list[tuple[str, tuple]] = []

    def execute(self, query: str, params: tuple = ()) -> None:
        self.executed_queries.append((query, params))

    def fetchone(self) -> tuple[bool]:
        return (self.lock_result,)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeConnection:
    def __init__(self, lock_result: bool = True):
        self.cursor_obj = FakeCursor(lock_result)
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def close(self):
        self.closed = True


def test_tentar_adquirir_lock_executes_pg_try_advisory_lock() -> None:
    conn = FakeConnection(lock_result=True)
    acquired = sync_lock.tentar_adquirir_lock(conn, lock_id=12345)

    assert acquired is True
    assert len(conn.cursor_obj.executed_queries) == 1
    assert "pg_try_advisory_lock" in conn.cursor_obj.executed_queries[0][0]
    assert conn.cursor_obj.executed_queries[0][1] == (12345,)


def test_tentar_adquirir_lock_returns_false_when_lock_held() -> None:
    conn = FakeConnection(lock_result=False)
    acquired = sync_lock.tentar_adquirir_lock(conn, lock_id=12345)

    assert acquired is False


def test_liberar_lock_executes_pg_advisory_unlock() -> None:
    conn = FakeConnection(lock_result=True)
    released = sync_lock.liberar_lock(conn, lock_id=12345)

    assert released is True
    assert len(conn.cursor_obj.executed_queries) == 1
    assert "pg_advisory_unlock" in conn.cursor_obj.executed_queries[0][0]
    assert conn.cursor_obj.executed_queries[0][1] == (12345,)


def test_obter_lock_sincronizacao_context_manager_releases_lock_on_exit() -> None:
    conn = FakeConnection(lock_result=True)

    with sync_lock.obter_lock_sincronizacao(conexao_custom=conn, lock_id=12345) as acquired:
        assert acquired is True
        assert len(conn.cursor_obj.executed_queries) == 1
        assert "pg_try_advisory_lock" in conn.cursor_obj.executed_queries[0][0]

    assert len(conn.cursor_obj.executed_queries) == 2
    assert "pg_advisory_unlock" in conn.cursor_obj.executed_queries[1][0]


def test_obter_lock_sincronizacao_releases_lock_even_on_exception() -> None:
    conn = FakeConnection(lock_result=True)

    with pytest.raises(ValueError, match="Erro simulado"):
        with sync_lock.obter_lock_sincronizacao(conexao_custom=conn, lock_id=12345) as acquired:
            assert acquired is True
            raise ValueError("Erro simulado")

    assert len(conn.cursor_obj.executed_queries) == 2
    assert "pg_advisory_unlock" in conn.cursor_obj.executed_queries[1][0]


def test_obter_lock_sincronizacao_does_not_unlock_if_not_acquired() -> None:
    conn = FakeConnection(lock_result=False)

    with sync_lock.obter_lock_sincronizacao(conexao_custom=conn, lock_id=12345) as acquired:
        assert acquired is False

    # Advisory unlock should NOT be called if lock was not acquired
    assert len(conn.cursor_obj.executed_queries) == 1
    assert "pg_try_advisory_lock" in conn.cursor_obj.executed_queries[0][0]
