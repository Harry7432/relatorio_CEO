import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from src import sync_service


ROOT = Path(__file__).resolve().parent.parent


def test_worker_invocation_contract_is_recorded_verbatim() -> None:
    model = (ROOT / "specs/003-production-runtime/data-model.md").read_text()
    constraints = {
        "command": "Exatamente `python -m src.sync_service`.",
        "trigger": "`manual` nesta feature; `scheduled` somente apos a feature 002.",
        "state": "`requested`, `running`, `succeeded`, `failed` ou `blocked`.",
        "exit_code": "Preserva a semantica atual do comando.",
    }

    for field, constraint in constraints.items():
        assert f"`{field}`" in model
        assert constraint in model


def test_executar_modulo_preserves_interpreter_arguments_and_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        captured["command"] = command
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="sensitive", stderr="")

    monkeypatch.setattr(sync_service.subprocess, "run", fake_run)

    result = sync_service.executar_modulo("src.sync_mensagens")

    assert captured["command"] == [sys.executable, "-m", "src.sync_mensagens"]
    assert captured["cwd"] == sync_service.RAIZ_PROJETO
    assert captured["timeout"] == 3600
    assert captured["check"] is False
    assert captured["capture_output"] is True
    assert result == "Etapa concluida com sucesso."
    assert "sensitive" not in result


def test_executar_modulo_preserves_failure_and_timeout_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sync_service.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=7,
            stdout="secret stdout",
            stderr="secret stderr",
        ),
    )

    with pytest.raises(RuntimeError, match="Falha ao executar etapa") as error:
        sync_service.executar_modulo("src.sync_mensagens")
    assert "secret" not in str(error.value)

    timeout = subprocess.TimeoutExpired([sys.executable], 3600)
    monkeypatch.setattr(
        sync_service.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(timeout),
    )
    with pytest.raises(subprocess.TimeoutExpired):
        sync_service.executar_modulo("src.sync_mensagens")


def test_complete_sync_preserves_stage_order_results_and_callbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    modules: list[str] = []
    callbacks: list[tuple[int, int, str]] = []

    def fake_execute(module: str) -> str:
        modules.append(module)
        return f"resultado-{len(modules)}"

    monkeypatch.setattr(sync_service, "executar_modulo", fake_execute)

    result = sync_service.executar_sincronizacao_completa(
        lambda current, total, description: callbacks.append(
            (current, total, description)
        )
    )

    assert modules == [module for _, module in sync_service.ETAPAS_SINCRONIZACAO]
    assert result == [
        f"{description}:\nresultado-{index}"
        for index, (description, _) in enumerate(sync_service.ETAPAS_SINCRONIZACAO, 1)
    ]
    assert callbacks == [
        callback
        for index, (description, _) in enumerate(sync_service.ETAPAS_SINCRONIZACAO)
        for callback in (
            (index, len(sync_service.ETAPAS_SINCRONIZACAO), description),
            (index + 1, len(sync_service.ETAPAS_SINCRONIZACAO), description),
        )
    ]


def test_main_prints_aggregate_results(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sync_service,
        "executar_sincronizacao_completa",
        lambda: ["etapa segura 1", "etapa segura 2"],
    )

    sync_service.main()

    assert capsys.readouterr().out == "etapa segura 1\netapa segura 2\n"
