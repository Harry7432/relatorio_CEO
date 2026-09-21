from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.seller_metrics import calcular_metricas_vendedores


def criar_mensagens(
    registros: list[dict] | None = None,
) -> pd.DataFrame:
    if registros is None:
        registros = [
            {
                "mensagem_id": "m1",
                "data": date(2026, 9, 1),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m2",
                "data": date(2026, 9, 30),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u2",
                "vendedor_responsavel": "Bruno",
                "canal": "Comercial 2",
            },
            {
                "mensagem_id": "m2",
                "data": date(2026, 9, 30),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u2",
                "vendedor_responsavel": "Bruno",
                "canal": "Comercial 2",
            },
            {
                "mensagem_id": "m3",
                "data": date(2026, 9, 15),
                "direcao": "FROM_HUB",
                "usuario_id_mensagem": None,
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m4",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": None,
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m5",
                "data": date(2026, 10, 1),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m6",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u3",
                "vendedor_responsavel": "  ",
                "canal": "Comercial 1",
            },
        ]

    return pd.DataFrame(registros)


@pytest.mark.parametrize(
    "usuario_automacao",
    [None, "", "  "],
)
def test_filtra_periodo_direcao_automacao_e_duplicidade(
    usuario_automacao: str | None,
) -> None:
    mensagens = criar_mensagens()
    mensagens.loc[
        mensagens["mensagem_id"].eq("m4"),
        "usuario_id_mensagem",
    ] = usuario_automacao
    original = mensagens.copy(deep=True)

    resultado = calcular_metricas_vendedores(
        mensagens,
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
    )

    assert resultado.ranking[
        ["vendedor", "mensagens_enviadas"]
    ].to_dict("records") == [
        {"vendedor": "Alice", "mensagens_enviadas": 1},
        {"vendedor": "Bruno", "mensagens_enviadas": 1},
        {"vendedor": "Não identificado", "mensagens_enviadas": 1},
    ]
    assert_frame_equal(mensagens, original)


@pytest.mark.parametrize(
    "mensagem_id",
    [None, "", "  "],
)
def test_rejeita_identidade_ausente_em_mensagem_elegivel(
    mensagem_id: str | None,
) -> None:
    mensagens = criar_mensagens(
        [
            {
                "mensagem_id": mensagem_id,
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            }
        ]
    )

    with pytest.raises(ValueError, match="mensagem_id"):
        calcular_metricas_vendedores(
            mensagens,
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 30),
        )


def test_rejeita_vendedores_conflitantes_para_mesma_mensagem() -> None:
    mensagens = criar_mensagens(
        [
            {
                "mensagem_id": "m1",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m1",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Bruno",
                "canal": "Comercial 1",
            },
        ]
    )

    with pytest.raises(ValueError, match="vendedores conflitantes"):
        calcular_metricas_vendedores(
            mensagens,
            data_inicial=date(2026, 9, 1),
            data_final=date(2026, 9, 30),
        )


def test_rejeita_periodo_invalido() -> None:
    with pytest.raises(ValueError, match="periodo"):
        calcular_metricas_vendedores(
            criar_mensagens(),
            data_inicial=date(2026, 9, 30),
            data_final=date(2026, 9, 1),
        )


def test_calcula_total_ranking_percentuais_e_desempate() -> None:
    mensagens = criar_mensagens(
        [
            {
                "mensagem_id": "m1",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m2",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": "Alice",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m3",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u2",
                "vendedor_responsavel": "Carla",
                "canal": "Comercial 1",
            },
            {
                "mensagem_id": "m4",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u3",
                "vendedor_responsavel": "Bruno",
                "canal": "Comercial 1",
            },
        ]
    )

    resultado = calcular_metricas_vendedores(
        mensagens,
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
    )

    assert resultado.total_geral == 4
    assert resultado.sem_dados is False
    assert resultado.ranking.to_dict("records") == [
        {
            "posicao": 1,
            "vendedor": "Alice",
            "mensagens_enviadas": 2,
            "participacao_percentual": 50.0,
        },
        {
            "posicao": 2,
            "vendedor": "Bruno",
            "mensagens_enviadas": 1,
            "participacao_percentual": 25.0,
        },
        {
            "posicao": 3,
            "vendedor": "Carla",
            "mensagens_enviadas": 1,
            "participacao_percentual": 25.0,
        },
    ]
    assert resultado.ranking["mensagens_enviadas"].sum() == 4


def test_vendedor_nao_identificado_pode_representar_cem_por_cento() -> None:
    mensagens = criar_mensagens(
        [
            {
                "mensagem_id": "m1",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": "u1",
                "vendedor_responsavel": None,
                "canal": "Comercial 1",
            }
        ]
    )

    resultado = calcular_metricas_vendedores(
        mensagens,
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
    )

    assert resultado.total_geral == 1
    assert resultado.ranking.iloc[0].to_dict() == {
        "posicao": 1,
        "vendedor": "Não identificado",
        "mensagens_enviadas": 1,
        "participacao_percentual": 100.0,
    }


def test_mantem_percentual_sem_arredondamento_interno() -> None:
    mensagens = criar_mensagens(
        [
            {
                "mensagem_id": f"m{indice}",
                "data": date(2026, 9, 15),
                "direcao": "TO_HUB",
                "usuario_id_mensagem": f"u{indice}",
                "vendedor_responsavel": vendedor,
                "canal": "Comercial 1",
            }
            for indice, vendedor in enumerate(
                ["Alice", "Bruno", "Carla"],
                start=1,
            )
        ]
    )

    resultado = calcular_metricas_vendedores(
        mensagens,
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
    )

    assert resultado.ranking[
        "participacao_percentual"
    ].tolist() == pytest.approx([100 / 3] * 3)


def test_resultado_vazio_tem_contrato_estavel() -> None:
    resultado = calcular_metricas_vendedores(
        criar_mensagens(),
        data_inicial=date(2026, 8, 1),
        data_final=date(2026, 8, 31),
    )

    assert resultado.total_geral == 0
    assert resultado.sem_dados is True
    assert resultado.ranking.empty
    assert resultado.ranking.columns.tolist() == [
        "posicao",
        "vendedor",
        "mensagens_enviadas",
        "participacao_percentual",
    ]


@pytest.mark.parametrize(
    ("canais", "total_esperado"),
    [
        ([], 3),
        (["Comercial 1"], 2),
        (["Comercial 2"], 1),
        (["Comercial 1", "Comercial 2"], 3),
        (["Canal sem mensagens"], 0),
    ],
)
def test_filtra_canais_selecionados(
    canais: list[str],
    total_esperado: int,
) -> None:
    resultado = calcular_metricas_vendedores(
        criar_mensagens(),
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
        canais=canais,
    )

    assert resultado.total_geral == total_esperado
    assert resultado.sem_dados is (total_esperado == 0)


def test_ignora_colunas_de_filtros_nao_relacionados() -> None:
    mensagens = criar_mensagens()
    mensagens["status_sessao"] = "OPEN"
    mensagens["tipo_mensagem"] = "TEXT"
    mensagens["pesquisa"] = "nao deve afetar a metrica"

    resultado = calcular_metricas_vendedores(
        mensagens,
        data_inicial=date(2026, 9, 1),
        data_final=date(2026, 9, 30),
        canais=[],
    )

    assert resultado.total_geral == 3
