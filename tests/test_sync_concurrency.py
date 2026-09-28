import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

from src import sync_lock, sync_service
from tests.test_sync_lock import FakeConnection

ROOT = Path(__file__).resolve().parent.parent

_real_obter_lock = sync_lock.obter_lock_sincronizacao


def test_concurrency_lock_acquired_runs_sync(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_conn = FakeConnection(lock_result=True)
    monkeypatch.setattr(
        sync_lock,
        "obter_lock_sincronizacao",
        lambda conexao_custom=None, lock_id=None: _real_obter_lock(
            conexao_custom=fake_conn, lock_id=lock_id
        ),
    )
    monkeypatch.setattr(
        sync_service, "executar_modulo", lambda modulo: "Etapa mock concluida"
    )

    logs = sync_service.executar_sincronizacao_completa()

    captured = capsys.readouterr().out
    assert "status=started" in captured
    assert "status=success" in captured
    assert "run_id=" in captured
    assert len(logs) == 3


def test_concurrency_lock_held_skips_execution_cleanly(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_conn = FakeConnection(lock_result=False)
    monkeypatch.setattr(
        sync_lock,
        "obter_lock_sincronizacao",
        lambda conexao_custom=None, lock_id=None: _real_obter_lock(
            conexao_custom=fake_conn, lock_id=lock_id
        ),
    )

    executed_modules: list[str] = []
    monkeypatch.setattr(
        sync_service,
        "executar_modulo",
        lambda modulo: (executed_modules.append(modulo) or "Etapa mock"),
    )

    logs = sync_service.executar_sincronizacao_completa()

    captured = capsys.readouterr().out
    assert "status=skipped_concurrency" in captured
    assert len(executed_modules) == 0
    assert logs == []


def test_main_exits_with_nonzero_on_stage_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_conn = FakeConnection(lock_result=True)
    monkeypatch.setattr(
        sync_lock,
        "obter_lock_sincronizacao",
        lambda conexao_custom=None, lock_id=None: _real_obter_lock(
            conexao_custom=fake_conn, lock_id=lock_id
        ),
    )

    def failing_execute(modulo: str) -> str:
        raise RuntimeError("Falha simulada na etapa")

    monkeypatch.setattr(sync_service, "executar_modulo", failing_execute)

    with pytest.raises(SystemExit) as exc_info:
        sync_service.main()

    assert exc_info.value.code != 0


def test_main_exits_with_zero_on_skipped_concurrency(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_conn = FakeConnection(lock_result=False)
    monkeypatch.setattr(
        sync_lock,
        "obter_lock_sincronizacao",
        lambda conexao_custom=None, lock_id=None: _real_obter_lock(
            conexao_custom=fake_conn, lock_id=lock_id
        ),
    )

    sync_service.main()
    captured = capsys.readouterr().out
    assert "status=skipped_concurrency" in captured


def test_logs_are_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_conn = FakeConnection(lock_result=True)
    monkeypatch.setattr(
        sync_lock,
        "obter_lock_sincronizacao",
        lambda conexao_custom=None, lock_id=None: _real_obter_lock(
            conexao_custom=fake_conn, lock_id=lock_id
        ),
    )

    def execute_with_secret(modulo: str) -> str:
        return "Concluido postgresql://user:secretpass@localhost:5432/db 5511999999999"

    monkeypatch.setattr(sync_service, "executar_modulo", execute_with_secret)

    sync_service.main()
    captured = capsys.readouterr().out

    assert "secretpass" not in captured
    assert "5511999999999" not in captured
    assert "status=success" in captured
