from datetime import date
from io import BytesIO
import logging
import os
from typing import Any, List, Optional

from fastapi import APIRouter, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import pandas as pd
import psycopg

from src.dashboard_repository import buscar_dados_dashboard
from src.seller_metrics import (
    ResumoMetricasVendedores,
    calcular_metricas_vendedores,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NO_STORE = {"Cache-Control": "no-store"}

MAPA_CANAIS = {
    "00000000-0000-4000-8000-000000000001": "Comercial 1 — +55 11 00000-0001",
    "00000000-0000-4000-8000-000000000002": "Comercial 2 — +55 11 00000-0002",
}


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


# ============================================================
# HELPER DE TRATAMENTO DE DADOS
# ============================================================


def carregar_dataframe_dashboard() -> pd.DataFrame:
    registros = buscar_dados_dashboard()
    df = pd.DataFrame(registros)

    if df.empty:
        return df

    df["timestamp_mensagem"] = pd.to_datetime(
        df["timestamp_mensagem"],
        utc=True,
        errors="coerce",
    ).dt.tz_convert("America/Sao_Paulo")

    colunas_texto = [
        "tipo_mensagem",
        "direcao",
        "status_mensagem",
        "origem_mensagem",
        "texto",
        "status_sessao",
        "channel_id",
        "titulo_sessao",
        "numero_sessao",
        "contato_nome",
        "nome_whatsapp",
        "telefone",
        "telefone_formatado",
        "vendedor_responsavel",
        "origem_vendedor",
        "usuario_mensagem",
    ]

    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    df["vendedor_responsavel"] = df["vendedor_responsavel"].replace(
        "", "Não identificado"
    )
    df["origem_vendedor"] = df["origem_vendedor"].replace(
        "", "NAO_IDENTIFICADO"
    )
    df["contato_nome"] = df["contato_nome"].replace("", "Contato sem nome")
    df["usuario_mensagem"] = df["usuario_mensagem"].replace(
        "", "Automação/BotNext"
    )

    df["canal"] = df["channel_id"].map(MAPA_CANAIS).fillna(df["channel_id"])
    df["data"] = df["timestamp_mensagem"].dt.date

    return df


def aplicar_filtros_df(
    df: pd.DataFrame,
    data_inicial: Optional[date] = None,
    data_final: Optional[date] = None,
    vendedores: Optional[List[str]] = None,
    canais: Optional[List[str]] = None,
    status_sessao: Optional[List[str]] = None,
    tipos_mensagem: Optional[List[str]] = None,
    direcoes: Optional[List[str]] = None,
    origens_vendedor: Optional[List[str]] = None,
    search_cliente: Optional[str] = None,
    search_mensagem: Optional[str] = None,
) -> pd.DataFrame:
    if df.empty:
        return df

    df_filtrado = df.copy()

    if data_inicial and data_final:
        df_filtrado = df_filtrado[
            (df_filtrado["data"] >= data_inicial)
            & (df_filtrado["data"] <= data_final)
        ]

    if vendedores:
        df_filtrado = df_filtrado[
            df_filtrado["vendedor_responsavel"].isin(vendedores)
        ]

    if canais:
        df_filtrado = df_filtrado[df_filtrado["canal"].isin(canais)]

    if status_sessao:
        df_filtrado = df_filtrado[
            df_filtrado["status_sessao"].isin(status_sessao)
        ]

    if tipos_mensagem:
        df_filtrado = df_filtrado[
            df_filtrado["tipo_mensagem"].isin(tipos_mensagem)
        ]

    if direcoes:
        df_filtrado = df_filtrado[df_filtrado["direcao"].isin(direcoes)]

    if origens_vendedor:
        df_filtrado = df_filtrado[
            df_filtrado["origem_vendedor"].isin(origens_vendedor)
        ]

    if search_cliente and search_cliente.strip():
        q = search_cliente.strip()
        mascara = (
            df_filtrado["contato_nome"].str.contains(
                q, case=False, na=False, regex=False
            )
            | df_filtrado["nome_whatsapp"].str.contains(
                q, case=False, na=False, regex=False
            )
            | df_filtrado["telefone"].str.contains(
                q, case=False, na=False, regex=False
            )
            | df_filtrado["telefone_formatado"].str.contains(
                q, case=False, na=False, regex=False
            )
        )
        df_filtrado = df_filtrado[mascara]

    if search_mensagem and search_mensagem.strip():
        q_msg = search_mensagem.strip()
        df_filtrado = df_filtrado[
            df_filtrado["texto"].str.contains(
                q_msg, case=False, na=False, regex=False
            )
        ]

    return df_filtrado


# ============================================================
# ROUTER DO DASHBOARD (/api/v1/dashboard)
# ============================================================

dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@dashboard_router.get("/health")
def dashboard_health() -> JSONResponse:
    return JSONResponse({"status": "ok"}, headers=NO_STORE)


@dashboard_router.get("/filters")
def get_dashboard_filters() -> JSONResponse:
    df = carregar_dataframe_dashboard()

    if df.empty:
        return JSONResponse(
            {
                "data_minima": str(date.today()),
                "data_maxima": str(date.today()),
                "vendedores": [],
                "canais": [],
                "status_sessao": [],
                "tipos_mensagem": [],
                "direcoes": [],
                "origens_vendedor": [],
            },
            headers=NO_STORE,
        )

    data_minima = str(df["data"].min())
    data_maxima = str(df["data"].max())

    vendedores = sorted(
        df["vendedor_responsavel"].dropna().unique().tolist()
    )
    canais = sorted(df["canal"].dropna().unique().tolist())
    status_sessao = sorted(
        [s for s in df["status_sessao"].unique() if s]
    )
    tipos_mensagem = sorted(
        [t for t in df["tipo_mensagem"].unique() if t]
    )
    direcoes = sorted([d for d in df["direcao"].unique() if d])
    origens_vendedor = sorted(
        [o for o in df["origem_vendedor"].unique() if o]
    )

    return JSONResponse(
        {
            "data_minima": data_minima,
            "data_maxima": data_maxima,
            "vendedores": vendedores,
            "canais": canais,
            "status_sessao": status_sessao,
            "tipos_mensagem": tipos_mensagem,
            "direcoes": direcoes,
            "origens_vendedor": origens_vendedor,
        },
        headers=NO_STORE,
    )


@dashboard_router.get("/metrics")
def get_dashboard_metrics(
    data_inicial: Optional[date] = Query(None),
    data_final: Optional[date] = Query(None),
    vendedores: Optional[List[str]] = Query(None),
    canais: Optional[List[str]] = Query(None),
    status_sessao: Optional[List[str]] = Query(None),
    tipos_mensagem: Optional[List[str]] = Query(None),
    direcoes: Optional[List[str]] = Query(None),
    origens_vendedor: Optional[List[str]] = Query(None),
    search_cliente: Optional[str] = Query(None),
    search_mensagem: Optional[str] = Query(None),
) -> JSONResponse:
    df = carregar_dataframe_dashboard()

    if df.empty:
        return JSONResponse(
            {
                "total_mensagens": 0,
                "total_sessoes": 0,
                "total_contatos": 0,
                "percentual_contatos_identificados": 0.0,
                "vendedores_total_mensagens_enviadas": 0,
                "ranking": [],
            },
            headers=NO_STORE,
        )

    df_filtrado = aplicar_filtros_df(
        df,
        data_inicial=data_inicial,
        data_final=data_final,
        vendedores=vendedores,
        canais=canais,
        status_sessao=status_sessao,
        tipos_mensagem=tipos_mensagem,
        direcoes=direcoes,
        origens_vendedor=origens_vendedor,
        search_cliente=search_cliente,
        search_mensagem=search_mensagem,
    )

    total_mensagens = len(df_filtrado)
    total_sessoes = (
        int(df_filtrado["sessao_id"].nunique()) if not df_filtrado.empty else 0
    )
    total_contatos = (
        int(df_filtrado["contato_id"].nunique()) if not df_filtrado.empty else 0
    )

    if not df_filtrado.empty:
        contatos_unicos = df_filtrado[
            ["contato_id", "vendedor_responsavel"]
        ].drop_duplicates(subset=["contato_id"])
        contatos_identificados = len(
            contatos_unicos[
                contatos_unicos["vendedor_responsavel"] != "Não identificado"
            ]
        )
        percentual_identificado = (
            (contatos_identificados / total_contatos * 100)
            if total_contatos > 0
            else 0.0
        )
    else:
        percentual_identificado = 0.0

    # Cálculo do ranking de vendedores via seller_metrics.py
    dt_inicio = data_inicial or df["data"].min()
    dt_fim = data_final or df["data"].max()

    try:
        resumo_vendedores: ResumoMetricasVendedores = (
            calcular_metricas_vendedores(
                df,
                data_inicial=dt_inicio,
                data_final=dt_fim,
                canais=canais,
            )
        )
        ranking_records = resumo_vendedores.ranking.to_dict(orient="records")
        vendedores_total = resumo_vendedores.total_geral
    except ValueError:
        ranking_records = []
        vendedores_total = 0

    return JSONResponse(
        {
            "total_mensagens": total_mensagens,
            "total_sessoes": total_sessoes,
            "total_contatos": total_contatos,
            "percentual_contatos_identificados": round(
                percentual_identificado, 1
            ),
            "vendedores_total_mensagens_enviadas": vendedores_total,
            "ranking": ranking_records,
        },
        headers=NO_STORE,
    )


@dashboard_router.get("/overview")
def get_dashboard_overview(
    data_inicial: Optional[date] = Query(None),
    data_final: Optional[date] = Query(None),
    vendedores: Optional[List[str]] = Query(None),
    canais: Optional[List[str]] = Query(None),
    status_sessao: Optional[List[str]] = Query(None),
    tipos_mensagem: Optional[List[str]] = Query(None),
    direcoes: Optional[List[str]] = Query(None),
    origens_vendedor: Optional[List[str]] = Query(None),
    search_cliente: Optional[str] = Query(None),
    search_mensagem: Optional[str] = Query(None),
) -> JSONResponse:
    df = carregar_dataframe_dashboard()
    df_filtrado = aplicar_filtros_df(
        df,
        data_inicial=data_inicial,
        data_final=data_final,
        vendedores=vendedores,
        canais=canais,
        status_sessao=status_sessao,
        tipos_mensagem=tipos_mensagem,
        direcoes=direcoes,
        origens_vendedor=origens_vendedor,
        search_cliente=search_cliente,
        search_mensagem=search_mensagem,
    )

    if df_filtrado.empty:
        return JSONResponse(
            {
                "mensagens_por_dia": [],
                "mensagens_por_tipo": [],
                "sessoes_por_status": [],
                "mensagens_por_canal": [],
                "contatos_por_vendedor": [],
            },
            headers=NO_STORE,
        )

    # 1. Mensagens por dia
    dia = (
        df_filtrado.groupby("data")
        .size()
        .reset_index(name="mensagens")
        .sort_values("data")
    )
    dia["data"] = dia["data"].astype(str)
    mensagens_por_dia = dia.to_dict(orient="records")

    # 2. Mensagens por tipo
    tipo = (
        df_filtrado.groupby("tipo_mensagem")
        .size()
        .reset_index(name="quantidade")
        .sort_values("quantidade", ascending=False)
    )
    tipo = tipo.rename(columns={"tipo_mensagem": "tipo"})
    mensagens_por_tipo = tipo.to_dict(orient="records")

    # 3. Sessões por status
    status = (
        df_filtrado[["sessao_id", "status_sessao"]]
        .drop_duplicates()
        .groupby("status_sessao")
        .size()
        .reset_index(name="conversas")
        .sort_values("conversas", ascending=False)
    )
    status = status.rename(columns={"status_sessao": "status"})
    sessoes_por_status = status.to_dict(orient="records")

    # 4. Mensagens por canal
    canal = (
        df_filtrado.groupby("canal")
        .size()
        .reset_index(name="mensagens")
        .sort_values("mensagens", ascending=False)
    )
    mensagens_por_canal = canal.to_dict(orient="records")

    # 5. Contatos por vendedor / origem
    contatos_vend = (
        df_filtrado[
            ["contato_id", "vendedor_responsavel", "origem_vendedor"]
        ]
        .drop_duplicates(subset=["contato_id"])
        .groupby(["vendedor_responsavel", "origem_vendedor"])
        .size()
        .reset_index(name="contatos")
        .sort_values("contatos", ascending=False)
    )
    contatos_vend = contatos_vend.rename(
        columns={
            "vendedor_responsavel": "vendedor",
            "origem_vendedor": "origem",
        }
    )
    contatos_por_vendedor = contatos_vend.to_dict(orient="records")

    return JSONResponse(
        {
            "mensagens_por_dia": mensagens_por_dia,
            "mensagens_por_tipo": mensagens_por_tipo,
            "sessoes_por_status": sessoes_por_status,
            "mensagens_por_canal": mensagens_por_canal,
            "contatos_por_vendedor": contatos_por_vendedor,
        },
        headers=NO_STORE,
    )


@dashboard_router.get("/conversations")
def get_dashboard_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    data_inicial: Optional[date] = Query(None),
    data_final: Optional[date] = Query(None),
    vendedores: Optional[List[str]] = Query(None),
    canais: Optional[List[str]] = Query(None),
    status_sessao: Optional[List[str]] = Query(None),
    tipos_mensagem: Optional[List[str]] = Query(None),
    direcoes: Optional[List[str]] = Query(None),
    origens_vendedor: Optional[List[str]] = Query(None),
    search_cliente: Optional[str] = Query(None),
    search_mensagem: Optional[str] = Query(None),
) -> JSONResponse:
    df = carregar_dataframe_dashboard()
    df_filtrado = aplicar_filtros_df(
        df,
        data_inicial=data_inicial,
        data_final=data_final,
        vendedores=vendedores,
        canais=canais,
        status_sessao=status_sessao,
        tipos_mensagem=tipos_mensagem,
        direcoes=direcoes,
        origens_vendedor=origens_vendedor,
        search_cliente=search_cliente,
        search_mensagem=search_mensagem,
    )

    if df_filtrado.empty:
        return JSONResponse(
            {"items": [], "total": 0, "page": page, "pages": 0},
            headers=NO_STORE,
        )

    total = len(df_filtrado)
    pages = (total + limit - 1) // limit

    inicio = (page - 1) * limit
    fim = inicio + limit

    df_pagina = df_filtrado.iloc[inicio:fim].copy()
    df_pagina["timestamp_mensagem"] = df_pagina[
        "timestamp_mensagem"
    ].dt.strftime("%d/%m/%Y %H:%M:%S")

    colunas_tabela = [
        "timestamp_mensagem",
        "vendedor_responsavel",
        "origem_vendedor",
        "contato_nome",
        "telefone_formatado",
        "canal",
        "status_sessao",
        "tipo_mensagem",
        "direcao",
        "usuario_mensagem",
        "texto",
        "sessao_id",
    ]

    items = df_pagina[colunas_tabela].to_dict(orient="records")

    return JSONResponse(
        {"items": items, "total": total, "page": page, "pages": pages},
        headers=NO_STORE,
    )


@dashboard_router.get("/export")
def export_dashboard(
    format: str = Query("csv"),
    data_inicial: Optional[date] = Query(None),
    data_final: Optional[date] = Query(None),
    vendedores: Optional[List[str]] = Query(None),
    canais: Optional[List[str]] = Query(None),
    status_sessao: Optional[List[str]] = Query(None),
    tipos_mensagem: Optional[List[str]] = Query(None),
    direcoes: Optional[List[str]] = Query(None),
    origens_vendedor: Optional[List[str]] = Query(None),
    search_cliente: Optional[str] = Query(None),
    search_mensagem: Optional[str] = Query(None),
) -> Response:
    df = carregar_dataframe_dashboard()
    df_filtrado = aplicar_filtros_df(
        df,
        data_inicial=data_inicial,
        data_final=data_final,
        vendedores=vendedores,
        canais=canais,
        status_sessao=status_sessao,
        tipos_mensagem=tipos_mensagem,
        direcoes=direcoes,
        origens_vendedor=origens_vendedor,
        search_cliente=search_cliente,
        search_mensagem=search_mensagem,
    )

    tabela = df_filtrado[
        [
            "timestamp_mensagem",
            "vendedor_responsavel",
            "origem_vendedor",
            "contato_nome",
            "telefone_formatado",
            "canal",
            "status_sessao",
            "tipo_mensagem",
            "direcao",
            "usuario_mensagem",
            "texto",
            "sessao_id",
        ]
    ].copy()

    if not tabela.empty:
        tabela["timestamp_mensagem"] = tabela["timestamp_mensagem"].dt.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

    tabela = tabela.rename(
        columns={
            "timestamp_mensagem": "Data e hora",
            "vendedor_responsavel": "Vendedor",
            "origem_vendedor": "Origem do vendedor",
            "contato_nome": "Cliente",
            "telefone_formatado": "Telefone",
            "canal": "Canal",
            "status_sessao": "Status da conversa",
            "tipo_mensagem": "Tipo",
            "direcao": "Direção",
            "usuario_mensagem": "Usuário/Bot",
            "texto": "Mensagem",
            "sessao_id": "ID da sessão",
        }
    )

    if format.lower() == "xlsx":
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as escritor:
            tabela.to_excel(
                escritor, index=False, sheet_name="Conversas BotNext"
            )
        content = buffer.getvalue()
        headers = {
            "Content-Disposition": 'attachment; filename="relatorio_botnext.xlsx"'
        }
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )
    else:
        csv_str = tabela.to_csv(index=False, sep=";").encode("utf-8-sig")
        headers = {
            "Content-Disposition": 'attachment; filename="relatorio_botnext.csv"'
        }
        return Response(
            content=csv_str, media_type="text/csv; charset=utf-8", headers=headers
        )


app.include_router(dashboard_router)
