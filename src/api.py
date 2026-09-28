import os

import psycopg
from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)

NO_STORE = {"Cache-Control": "no-store"}


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"}, headers=NO_STORE)


@app.get("/ready")
def readiness() -> JSONResponse:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return JSONResponse(
            {"status": "not_ready"},
            status_code=503,
            headers=NO_STORE,
        )

    try:
        with psycopg.connect(database_url, connect_timeout=4) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
    except Exception:
        return JSONResponse(
            {"status": "not_ready"},
            status_code=503,
            headers=NO_STORE,
        )

    return JSONResponse({"status": "ready"}, headers=NO_STORE)
