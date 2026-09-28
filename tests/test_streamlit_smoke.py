import logging
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src import dashboard_repository, sync_service


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
SECRET = "postgresql://secret-user:secret-password@db.internal/secret-db"


def records() -> list[dict[str, object]]:
    return [
        {
            "mensagem_id": "message-1",
            "sessao_id": "session-1",
            "contato_id": "contact-1",
            "usuario_id_mensagem": "user-1",
            "timestamp_mensagem": "2026-09-21T12:00:00Z",
            "tipo_mensagem": "TEXT",
            "direcao": "TO_HUB",
            "status_mensagem": "SENT",
            "origem_mensagem": "AGENT",
            "texto": "Mensagem segura",
            "status_sessao": "OPEN",
            "channel_id": "channel-1",
            "titulo_sessao": "Atendimento",
            "numero_sessao": "1",
            "contato_nome": "Cliente Teste",
            "nome_whatsapp": "Cliente",
            "telefone": "+55 11 00000-0002",
            "telefone_formatado": "+55 11 00000-0001",
            "vendedor_responsavel": "Alice",
            "origem_vendedor": "AGENT",
            "usuario_mensagem": "Alice",
        }
    ]


def fresh_app() -> AppTest:
    st.cache_data.clear()
    return AppTest.from_file(APP_PATH, default_timeout=30).run()


def test_streamlit_loads_tabs_filters_empty_state_and_exports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(dashboard_repository, "buscar_dados_dashboard", records)

    app = fresh_app()

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "📊 Visão geral",
        "👥 Vendedores",
        "💬 Conversas",
    ]
    assert {widget.label for widget in app.multiselect} == {
        "Vendedor responsável",
        "Canal comercial",
        "Status da sessão",
        "Tipo de mensagem",
        "Direção da mensagem",
        "Origem do vendedor",
    }
    assert {widget.label for widget in app.text_input} == {
        "Pesquisar cliente ou telefone",
        "Pesquisar na mensagem",
    }
    assert [button.label for button in app.download_button] == [
        "⬇️ Baixar CSV",
        "⬇️ Baixar Excel",
    ]

    search = next(
        widget
        for widget in app.text_input
        if widget.label == "Pesquisar cliente ou telefone"
    )
    app = search.set_value("inexistente").run()
    assert not app.exception
    assert any(
        "Nenhum registro corresponde" in warning.value
        for warning in app.warning
    )


def test_streamlit_preserves_empty_repository_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(dashboard_repository, "buscar_dados_dashboard", lambda: [])

    app = fresh_app()

    assert not app.exception
    assert any("Nenhum dado foi encontrado" in warning.value for warning in app.warning)
    assert any("Sincronizar" in button.label for button in app.button)


def test_streamlit_sanitizes_dashboard_failure(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(
        dashboard_repository,
        "buscar_dados_dashboard",
        lambda: (_ for _ in ()).throw(RuntimeError(SECRET)),
    )
    caplog.set_level(logging.INFO)

    app = fresh_app()

    assert not app.exception
    assert any("painel está indisponível" in warning.value for warning in app.warning)
    assert SECRET not in caplog.text
    assert SECRET not in str(app)


def test_streamlit_manual_sync_success_and_sanitized_failure(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(dashboard_repository, "buscar_dados_dashboard", records)
    calls: list[bool] = []

    def successful_sync(callback: object) -> list[str]:
        calls.append(True)
        return ["Etapa concluida com sucesso."]

    monkeypatch.setattr(sync_service, "executar_sincronizacao_completa", successful_sync)
    app = fresh_app()
    sync_button = next(button for button in app.button if "Sincronizar" in button.label)
    app = sync_button.click().run()
    assert calls == [True]
    assert not app.exception

    def failing_sync(callback: object) -> list[str]:
        raise RuntimeError(SECRET)

    monkeypatch.setattr(sync_service, "executar_sincronizacao_completa", failing_sync)
    caplog.clear()
    app = fresh_app()
    sync_button = next(button for button in app.button if "Sincronizar" in button.label)
    app = sync_button.click().run()

    assert not app.exception
    assert any("sincronização manual está indisponível" in error.value for error in app.error)
    assert len(app.code) == 0
    assert SECRET not in caplog.text
    assert SECRET not in str(app)
