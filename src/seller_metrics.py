from dataclasses import dataclass
from datetime import date

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "mensagem_id",
    "data",
    "direcao",
    "usuario_id_mensagem",
    "vendedor_responsavel",
    "canal",
}
COLUNAS_RANKING = [
    "posicao",
    "vendedor",
    "mensagens_enviadas",
    "participacao_percentual",
]


@dataclass(frozen=True)
class ResumoMetricasVendedores:
    total_geral: int
    ranking: pd.DataFrame

    @property
    def sem_dados(self) -> bool:
        return self.total_geral == 0


def calcular_metricas_vendedores(
    mensagens: pd.DataFrame,
    data_inicial: date,
    data_final: date,
    canais: list[str] | None = None,
) -> ResumoMetricasVendedores:
    if data_inicial > data_final:
        raise ValueError("O periodo informado e invalido.")

    colunas_ausentes = sorted(
        COLUNAS_OBRIGATORIAS.difference(mensagens.columns)
    )
    if colunas_ausentes:
        raise ValueError(
            "Colunas obrigatorias ausentes: "
            + ", ".join(colunas_ausentes)
        )

    usuario_preenchido = (
        mensagens["usuario_id_mensagem"].notna()
        & mensagens["usuario_id_mensagem"]
        .astype(str)
        .str.strip()
        .ne("")
    )
    selecao = (
        mensagens["data"].between(
            data_inicial,
            data_final,
            inclusive="both",
        )
        & mensagens["direcao"].eq("TO_HUB")
        & usuario_preenchido
    )
    if canais:
        selecao &= mensagens["canal"].isin(canais)

    elegiveis = mensagens.loc[
        selecao,
        ["mensagem_id", "vendedor_responsavel"],
    ].copy()

    if elegiveis.empty:
        return ResumoMetricasVendedores(
            total_geral=0,
            ranking=pd.DataFrame(columns=COLUNAS_RANKING),
        )

    identidade_invalida = (
        elegiveis["mensagem_id"].isna()
        | elegiveis["mensagem_id"]
        .astype(str)
        .str.strip()
        .eq("")
    )
    if identidade_invalida.any():
        raise ValueError(
            "Mensagem elegivel sem mensagem_id valido."
        )

    elegiveis["vendedor"] = (
        elegiveis["vendedor_responsavel"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", "Não identificado")
    )

    vendedores_por_mensagem = elegiveis.groupby(
        "mensagem_id",
        sort=False,
    )["vendedor"].nunique()
    if vendedores_por_mensagem.gt(1).any():
        raise ValueError(
            "Mensagem duplicada com vendedores conflitantes."
        )

    mensagens_unicas = elegiveis.drop_duplicates(
        subset=["mensagem_id"]
    )

    ranking = (
        mensagens_unicas.groupby(
            "vendedor",
            as_index=False,
            sort=False,
        )
        .size()
        .rename(columns={"size": "mensagens_enviadas"})
        .sort_values(
            ["mensagens_enviadas", "vendedor"],
            ascending=[False, True],
            ignore_index=True,
        )
    )
    total_geral = int(ranking["mensagens_enviadas"].sum())
    ranking["participacao_percentual"] = (
        ranking["mensagens_enviadas"] / total_geral * 100
    )
    ranking.insert(
        0,
        "posicao",
        range(1, len(ranking) + 1),
    )

    return ResumoMetricasVendedores(
        total_geral=total_geral,
        ranking=ranking[COLUNAS_RANKING].reset_index(
            drop=True
        ),
    )
