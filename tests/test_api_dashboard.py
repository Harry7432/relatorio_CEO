from datetime import date
from unittest.mock import patch
import pandas as pd
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_dashboard_health():
    response = client.get("/api/v1/dashboard/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_headers():
    response = client.options(
        "/api/v1/dashboard/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@patch("src.api.buscar_dados_dashboard")
def test_dashboard_metrics_and_filters(mock_buscar):
    mock_buscar.return_value = [
        {
            "mensagem_id": "msg-1",
            "sessao_id": "sess-1",
            "usuario_id_mensagem": "usr-1",
            "timestamp_mensagem": "2026-09-21T10:00:00+00:00",
            "tipo_mensagem": "TEXT",
            "direcao": "TO_HUB",
            "status_mensagem": "SENT",
            "origem_mensagem": "SYSTEM",
            "texto": "Proposta comercial",
            "status_sessao": "CLOSED",
            "channel_id": "00000000-0000-4000-8000-000000000001",
            "titulo_sessao": "Atendimento",
            "numero_sessao": "1001",
            "contato_id": "cnt-1",
            "contato_nome": "João Silva",
            "nome_whatsapp": "João WhatsApp",
            "telefone": "5511999998888",
            "telefone_formatado": "+55 11 99999-8888",
            "vendedor_responsavel": "Carlos Vendedor",
            "origem_vendedor": "HUBSPOT",
            "usuario_mensagem": "Carlos Vendedor",
        }
    ]

    res_filters = client.get("/api/v1/dashboard/filters")
    assert res_filters.status_code == 200
    data_filters = res_filters.json()
    assert "data_minima" in data_filters
    assert "vendedores" in data_filters
    assert "Carlos Vendedor" in data_filters["vendedores"]

    res_metrics = client.get("/api/v1/dashboard/metrics")
    assert res_metrics.status_code == 200
    data_metrics = res_metrics.json()
    assert data_metrics["total_mensagens"] == 1
    assert data_metrics["total_sessoes"] == 1
    assert data_metrics["total_contatos"] == 1
    assert len(data_metrics["ranking"]) == 1
    assert data_metrics["ranking"][0]["vendedor"] == "Carlos Vendedor"


@patch("src.api.buscar_dados_dashboard")
def test_dashboard_overview_and_conversations(mock_buscar):
    mock_buscar.return_value = [
        {
            "mensagem_id": "msg-1",
            "sessao_id": "sess-1",
            "usuario_id_mensagem": "usr-1",
            "timestamp_mensagem": "2026-09-21T10:00:00+00:00",
            "tipo_mensagem": "TEXT",
            "direcao": "TO_HUB",
            "status_mensagem": "SENT",
            "origem_mensagem": "SYSTEM",
            "texto": "Teste mensagem proposta",
            "status_sessao": "CLOSED",
            "channel_id": "00000000-0000-4000-8000-000000000001",
            "titulo_sessao": "Atendimento",
            "numero_sessao": "1001",
            "contato_id": "cnt-1",
            "contato_nome": "Maria Souza",
            "nome_whatsapp": "Maria WS",
            "telefone": "5511988887777",
            "telefone_formatado": "+55 11 98888-7777",
            "vendedor_responsavel": "Ana Vendedora",
            "origem_vendedor": "MANUAL",
            "usuario_mensagem": "Ana Vendedora",
        }
    ]

    res_overview = client.get("/api/v1/dashboard/overview")
    assert res_overview.status_code == 200
    overview = res_overview.json()
    assert "mensagens_por_dia" in overview
    assert "mensagens_por_tipo" in overview

    res_conv = client.get("/api/v1/dashboard/conversations?search_cliente=Maria")
    assert res_conv.status_code == 200
    conv = res_conv.json()
    assert conv["total"] == 1
    assert len(conv["items"]) == 1
    assert conv["items"][0]["contato_nome"] == "Maria Souza"


@patch("src.api.buscar_dados_dashboard")
def test_dashboard_export(mock_buscar):
    mock_buscar.return_value = [
        {
            "mensagem_id": "msg-1",
            "sessao_id": "sess-1",
            "usuario_id_mensagem": "usr-1",
            "timestamp_mensagem": "2026-09-21T10:00:00+00:00",
            "tipo_mensagem": "TEXT",
            "direcao": "TO_HUB",
            "status_mensagem": "SENT",
            "origem_mensagem": "SYSTEM",
            "texto": "Export test",
            "status_sessao": "CLOSED",
            "channel_id": "00000000-0000-4000-8000-000000000001",
            "titulo_sessao": "Atendimento",
            "numero_sessao": "1001",
            "contato_id": "cnt-1",
            "contato_nome": "Maria Souza",
            "nome_whatsapp": "Maria WS",
            "telefone": "5511988887777",
            "telefone_formatado": "+55 11 98888-7777",
            "vendedor_responsavel": "Ana Vendedora",
            "origem_vendedor": "MANUAL",
            "usuario_mensagem": "Ana Vendedora",
        }
    ]

    res_csv = client.get("/api/v1/dashboard/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

    res_xlsx = client.get("/api/v1/dashboard/export?format=xlsx")
    assert res_xlsx.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in res_xlsx.headers["content-type"]
    )
