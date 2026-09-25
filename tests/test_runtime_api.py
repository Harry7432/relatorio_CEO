from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api


ROOT = Path(__file__).resolve().parent.parent
CLIENT = TestClient(api.app)


def test_probe_result_contract_is_recorded_verbatim() -> None:
    model = (ROOT / "specs/003-production-runtime/data-model.md").read_text()
    constraints = {
        "probe": "`health` ou `readiness`; derivado da rota, nao retornado no corpo.",
        "status": "`ok`, `ready` ou `not_ready`.",
        "http_status": "`200` para `ok`/`ready`; `503` para `not_ready`.",
        "cache_control": "Sempre `no-store`.",
    }

    for field, constraint in constraints.items():
        assert f"`{field}`" in model
        assert constraint in model


def test_health_has_exact_contract_and_does_no_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api.psycopg,
        "connect",
        lambda *args, **kwargs: pytest.fail("health accessed PostgreSQL"),
    )
    monkeypatch.setattr(
        api.os,
        "getenv",
        lambda *args, **kwargs: pytest.fail("health accessed configuration"),
    )

    response = CLIENT.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"


def test_readiness_without_database_url_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    response = CLIENT.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
    assert response.headers["cache-control"] == "no-store"


def test_readiness_executes_only_select_one_and_closes_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executed: list[str] = []
    closed = False

    class Cursor:
        def __enter__(self) -> "Cursor":
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def execute(self, query: str) -> None:
            executed.append(query)

    class Connection:
        def __enter__(self) -> "Connection":
            return self

        def __exit__(self, *args: object) -> None:
            nonlocal closed
            closed = True

        def cursor(self) -> Cursor:
            return Cursor()

    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/test")
    monkeypatch.setattr(api.psycopg, "connect", lambda *args, **kwargs: Connection())

    response = CLIENT.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    assert executed == ["SELECT 1"]
    assert closed is True


def test_readiness_hides_database_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "postgresql://private-user:private-password@db.internal/private-db"
    monkeypatch.setenv("DATABASE_URL", secret)
    monkeypatch.setattr(
        api.psycopg,
        "connect",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError(secret)),
    )

    response = CLIENT.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
    assert secret not in response.text


def test_invalid_database_url_fails_safely_within_five_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import time

    monkeypatch.setenv("DATABASE_URL", "invalid secret database url")
    started = time.monotonic()

    response = CLIENT.get("/ready")

    assert time.monotonic() - started < 5
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
    assert "invalid secret database url" not in response.text


@pytest.mark.parametrize("path", ["/", "/docs", "/redoc", "/openapi.json", "/health/", "/ready/"])
def test_undeclared_routes_are_not_available(path: str) -> None:
    response = CLIENT.get(path, follow_redirects=False)

    assert response.status_code == 404
    assert response.is_redirect is False


@pytest.mark.parametrize("path", ["/health", "/ready"])
def test_unsupported_probe_methods_return_405(path: str) -> None:
    response = CLIENT.post(path)

    assert response.status_code == 405


def test_fastapi_contract_surfaces_are_disabled() -> None:
    assert api.app.openapi_url is None
    assert api.app.docs_url is None
    assert api.app.redoc_url is None
    assert api.app.router.redirect_slashes is False
