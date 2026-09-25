import os
import time

import pytest
from fastapi.testclient import TestClient

from src.api import app


RUN_POSTGRES_INTEGRATION = os.getenv("RUN_POSTGRES_INTEGRATION") == "1"


@pytest.mark.skipif(
    not RUN_POSTGRES_INTEGRATION,
    reason="set RUN_POSTGRES_INTEGRATION=1 for disposable PostgreSQL",
)
def test_readiness_with_disposable_postgresql(monkeypatch: pytest.MonkeyPatch) -> None:
    from testcontainers.postgres import PostgresContainer

    client = TestClient(app)
    with PostgresContainer("postgres:17-alpine") as postgres:
        url = (
            postgres.get_connection_url()
            .replace("postgresql+psycopg2://", "postgresql://")
            .replace("postgresql+psycopg://", "postgresql://")
            .replace("localhost", "127.0.0.1")
        )
        monkeypatch.setenv("DATABASE_URL", url)
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.skipif(
    not RUN_POSTGRES_INTEGRATION,
    reason="set RUN_POSTGRES_INTEGRATION=1 for disposable PostgreSQL",
)
def test_unreachable_postgresql_is_sanitized_within_five_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dsn = "postgresql://secret-user:secret-password@127.0.0.1:1/secret-db"
    monkeypatch.setenv("DATABASE_URL", dsn)
    client = TestClient(app)

    started = time.monotonic()
    response = client.get("/ready")
    duration = time.monotonic() - started

    assert duration < 5
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
    assert dsn not in response.text
