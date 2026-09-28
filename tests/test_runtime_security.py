from types import SimpleNamespace

import pytest
import requests

from src import botnext_client, config, sync_mensagens, sync_service
from src.runtime_security import (
    OperationalErrorCategory,
    operational_error,
    redact_sensitive,
)


TOKEN = "token-super-secreto"
PASSWORD = "senha-super-secreta"
DSN = "postgresql://usuario:senha@db.internal:5432/producao"
PHONE = "+55 11 00000-0001"
SESSION_ID = "11111111-2222-3333-4444-555555555555"
CONTACT_ID = "contact-sensitive-id"
MESSAGE_ID = "message-sensitive-id"
MESSAGE = "conteudo confidencial da mensagem"
RESPONSE_BODY = '{"token":"token-super-secreto"}'

SENSITIVE_VALUES = (
    TOKEN,
    PASSWORD,
    DSN,
    PHONE,
    SESSION_ID,
    CONTACT_ID,
    MESSAGE_ID,
    MESSAGE,
    RESPONSE_BODY,
)


def assert_sanitized(value: object) -> None:
    rendered = str(value)
    for sensitive in SENSITIVE_VALUES:
        assert sensitive not in rendered


def test_runtime_redaction_removes_seeded_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DSN)
    monkeypatch.setenv("BOTNEXT_TOKEN", TOKEN)
    monkeypatch.setenv("BOTNEXT_CHANNEL_IDS", SESSION_ID)

    raw = " | ".join(SENSITIVE_VALUES)
    sanitized = redact_sensitive(raw, extra_values=SENSITIVE_VALUES)

    assert sanitized
    assert_sanitized(sanitized)


def test_runtime_redaction_is_recursive_and_redacts_sensitive_keys() -> None:
    raw = {
        "password": PASSWORD,
        "nested": [TOKEN, {"message": MESSAGE}],
        "safe": "operational",
    }

    sanitized = redact_sensitive(raw, extra_values=SENSITIVE_VALUES)

    assert sanitized == {
        "password": "[REDACTED]",
        "nested": ["[REDACTED]", {"message": "[REDACTED]"}],
        "safe": "operational",
    }
    assert_sanitized(sanitized)


def test_operational_errors_are_selected_from_an_allow_list() -> None:
    messages = {
        operational_error(category)
        for category in OperationalErrorCategory
    }

    assert messages == {
        "Configuracao obrigatoria ausente.",
        "Falha ao consultar o BotNext.",
        "Falha ao consultar mensagens do BotNext.",
        "Falha ao executar etapa de sincronizacao.",
        "Servico temporariamente indisponivel.",
    }
    for message in messages:
        assert_sanitized(message)


def test_configuration_errors_only_name_missing_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(config, "DATABASE_URL", "")
    monkeypatch.setattr(config, "BOTNEXT_TOKEN", "")
    monkeypatch.setattr(config, "BOTNEXT_CHANNEL_IDS", [])

    with pytest.raises(ValueError) as database_error:
        config.validar_configuracoes_banco()
    with pytest.raises(ValueError) as botnext_error:
        config.validar_configuracoes_botnext()

    assert str(database_error.value) == "Configuracao ausente: DATABASE_URL."
    assert str(botnext_error.value) == "Configuracao ausente: BOTNEXT_TOKEN."


def test_botnext_http_error_does_not_expose_response_or_url() -> None:
    response = SimpleNamespace(
        status_code=500,
        text=RESPONSE_BODY,
        url=f"https://api.example.invalid/messages?token={TOKEN}",
        raise_for_status=lambda: (_ for _ in ()).throw(requests.HTTPError(DSN)),
    )
    client = botnext_client.BotNextClient.__new__(botnext_client.BotNextClient)
    client.http = SimpleNamespace(get=lambda *args, **kwargs: response)

    with pytest.raises(RuntimeError) as error:
        client.executar_get("https://api.example.invalid/messages")

    assert str(error.value) == "Falha ao consultar o BotNext."
    assert error.value.__cause__ is None
    assert_sanitized(error.value)


def test_message_retry_output_and_error_are_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class FailingClient:
        def listar_mensagens_pagina(self, **kwargs: object) -> dict:
            raise RuntimeError(" | ".join(SENSITIVE_VALUES))

    monkeypatch.setattr(sync_mensagens.time, "sleep", lambda _: None)

    with pytest.raises(RuntimeError) as error:
        sync_mensagens.buscar_pagina_com_tentativas(
            FailingClient(),
            SESSION_ID,
            1,
        )

    assert str(error.value) == "Falha ao consultar mensagens do BotNext."
    assert error.value.__cause__ is None
    assert_sanitized(capsys.readouterr().out)
    assert_sanitized(error.value)


@pytest.mark.parametrize("returncode", [0, 1])
def test_worker_boundary_never_returns_subprocess_output(
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
) -> None:
    output = " | ".join(SENSITIVE_VALUES)
    completed = SimpleNamespace(
        returncode=returncode,
        stdout=output,
        stderr=output,
    )
    monkeypatch.setattr(sync_service.subprocess, "run", lambda *args, **kwargs: completed)

    if returncode == 0:
        result = sync_service.executar_modulo("src.sync_mensagens")
        assert result == "Etapa concluida com sucesso."
        assert_sanitized(result)
    else:
        with pytest.raises(RuntimeError) as error:
            sync_service.executar_modulo("src.sync_mensagens")
        assert str(error.value) == "Falha ao executar etapa de sincronizacao."
        assert_sanitized(error.value)
