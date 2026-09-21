from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard_repository import buscar_dados_dashboard
from src.sync_service import executar_sincronizacao_completa


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Relatório Comercial BotNext",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        [data-testid="stMetricLabel"] {
            color: #475569;
        }

        [data-testid="stMetricValue"] {
            color: #0F172A;
        }

        .titulo-principal {
            font-size: 2rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0;
        }

        .subtitulo {
            color: #64748B;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }

        .status-atualizacao {
            padding: 8px 12px;
            background-color: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 8px;
            color: #065F46;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTES
# ============================================================

MAPA_CANAIS = {
    "1df7e653-c749-460c-82a7-96b371cb0399":
        "Comercial 1 — +55 41 99938-4102",

    "eca264fb-449a-43b2-a4e5-77a3853d830c":
        "Comercial 2 — +55 41 99938-0663",
}


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    registros = buscar_dados_dashboard()
    dataframe = pd.DataFrame(registros)

    if dataframe.empty:
        return dataframe

    dataframe["timestamp_mensagem"] = pd.to_datetime(
        dataframe["timestamp_mensagem"],
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

    for coluna in colunas_texto:
        if coluna in dataframe.columns:
            dataframe[coluna] = (
                dataframe[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    dataframe["vendedor_responsavel"] = dataframe[
        "vendedor_responsavel"
    ].replace("", "Não identificado")

    dataframe["origem_vendedor"] = dataframe[
        "origem_vendedor"
    ].replace("", "NAO_IDENTIFICADO")

    dataframe["contato_nome"] = dataframe[
        "contato_nome"
    ].replace("", "Contato sem nome")

    dataframe["usuario_mensagem"] = dataframe[
        "usuario_mensagem"
    ].replace("", "Automação/BotNext")

    dataframe["canal"] = (
        dataframe["channel_id"]
        .map(MAPA_CANAIS)
        .fillna(dataframe["channel_id"])
    )

    dataframe["data"] = dataframe[
        "timestamp_mensagem"
    ].dt.date

    return dataframe


def gerar_excel(
    dataframe: pd.DataFrame,
) -> bytes:
    exportacao = dataframe.copy()

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl",
    ) as escritor:
        exportacao.to_excel(
            escritor,
            index=False,
            sheet_name="Conversas BotNext",
        )

    return buffer.getvalue()


# ============================================================
# DADOS INICIAIS
# ============================================================

df = carregar_dados()


# ============================================================
# CABEÇALHO
# ============================================================

coluna_titulo, coluna_atualizar = st.columns(
    [5, 1]
)

with coluna_titulo:
    st.markdown(
        '<p class="titulo-principal">'
        'Relatório Comercial BotNext'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="subtitulo">'
        'Acompanhamento de contatos, conversas e mensagens '
        'dos canais comerciais.'
        '</p>',
        unsafe_allow_html=True,
    )

with coluna_atualizar:
    iniciar_sincronizacao = st.button(
        "🔄 Sincronizar",
        use_container_width=True,
        help=(
            "Busca novamente usuários, contatos, "
            "sessões e mensagens do BotNext."
        ),
    )


# ============================================================
# MENSAGEM APÓS SINCRONIZAÇÃO
# ============================================================

if st.session_state.pop(
    "sincronizacao_concluida",
    False,
):
    st.success(
        "Sincronização concluída! "
        "O banco e o painel foram atualizados."
    )


# ============================================================
# SINCRONIZAÇÃO COMPLETA
# ============================================================

if iniciar_sincronizacao:
    barra_progresso = st.progress(
        0,
        text="Preparando sincronização...",
    )

    mensagem_etapa = st.empty()

    def atualizar_progresso(
        etapa_atual: int,
        total_etapas: int,
        descricao: str,
    ) -> None:
        if total_etapas > 0:
            percentual = (
                etapa_atual / total_etapas
            )
        else:
            percentual = 0

        barra_progresso.progress(
            percentual,
            text=descricao,
        )

        mensagem_etapa.info(
            f"{descricao}..."
        )

    try:
        with st.spinner(
            "Consultando o BotNext e atualizando o banco..."
        ):
            executar_sincronizacao_completa(
                atualizar_progresso
            )

        barra_progresso.progress(
            1.0,
            text="Sincronização concluída!",
        )

        mensagem_etapa.success(
            "Todos os dados foram atualizados."
        )

        st.session_state[
            "sincronizacao_concluida"
        ] = True

        st.cache_data.clear()
        st.rerun()

    except Exception as erro:
        barra_progresso.empty()
        mensagem_etapa.empty()

        st.error(
            "Não foi possível concluir a sincronização."
        )

        with st.expander(
            "Visualizar detalhes do erro"
        ):
            st.code(str(erro))


# ============================================================
# VALIDAÇÃO DOS DADOS
# ============================================================

if df.empty:
    st.warning(
        "Nenhum dado foi encontrado no banco."
    )
    st.stop()


# ============================================================
# FILTROS LATERAIS
# ============================================================

st.sidebar.header("Filtros do relatório")

data_minima = df["data"].min()
data_maxima = df["data"].max()

periodo = st.sidebar.date_input(
    "Período das mensagens",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY",
)

vendedores_disponiveis = sorted(
    df["vendedor_responsavel"]
    .dropna()
    .unique()
    .tolist()
)

vendedores_selecionados = st.sidebar.multiselect(
    "Vendedor responsável",
    options=vendedores_disponiveis,
    default=[],
    placeholder="Todos os vendedores",
)

canais_disponiveis = sorted(
    df["canal"]
    .dropna()
    .unique()
    .tolist()
)

canais_selecionados = st.sidebar.multiselect(
    "Canal comercial",
    options=canais_disponiveis,
    default=[],
    placeholder="Todos os canais",
)

status_disponiveis = sorted(
    [
        status
        for status
        in df["status_sessao"].unique()
        if status
    ]
)

status_selecionados = st.sidebar.multiselect(
    "Status da sessão",
    options=status_disponiveis,
    default=[],
    placeholder="Todos os status",
)

tipos_disponiveis = sorted(
    [
        tipo
        for tipo
        in df["tipo_mensagem"].unique()
        if tipo
    ]
)

tipos_selecionados = st.sidebar.multiselect(
    "Tipo de mensagem",
    options=tipos_disponiveis,
    default=[],
    placeholder="Todos os tipos",
)

direcoes_disponiveis = sorted(
    [
        direcao
        for direcao
        in df["direcao"].unique()
        if direcao
    ]
)

direcoes_selecionadas = st.sidebar.multiselect(
    "Direção da mensagem",
    options=direcoes_disponiveis,
    default=[],
    placeholder="Todas as direções",
)

origens_disponiveis = sorted(
    [
        origem
        for origem
        in df["origem_vendedor"].unique()
        if origem
    ]
)

origens_selecionadas = st.sidebar.multiselect(
    "Origem do vendedor",
    options=origens_disponiveis,
    default=[],
    placeholder="Todas as origens",
)

pesquisa_cliente = st.sidebar.text_input(
    "Pesquisar cliente ou telefone",
    placeholder="Nome ou telefone",
)

pesquisa_mensagem = st.sidebar.text_input(
    "Pesquisar na mensagem",
    placeholder="Palavra ou frase",
)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()

if (
    isinstance(periodo, tuple)
    and len(periodo) == 2
):
    data_inicial, data_final = periodo

    df_filtrado = df_filtrado[
        (
            df_filtrado["data"]
            >= data_inicial
        )
        & (
            df_filtrado["data"]
            <= data_final
        )
    ]

if vendedores_selecionados:
    df_filtrado = df_filtrado[
        df_filtrado[
            "vendedor_responsavel"
        ].isin(
            vendedores_selecionados
        )
    ]

if canais_selecionados:
    df_filtrado = df_filtrado[
        df_filtrado["canal"].isin(
            canais_selecionados
        )
    ]

if status_selecionados:
    df_filtrado = df_filtrado[
        df_filtrado[
            "status_sessao"
        ].isin(
            status_selecionados
        )
    ]

if tipos_selecionados:
    df_filtrado = df_filtrado[
        df_filtrado[
            "tipo_mensagem"
        ].isin(
            tipos_selecionados
        )
    ]

if direcoes_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado["direcao"].isin(
            direcoes_selecionadas
        )
    ]

if origens_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado[
            "origem_vendedor"
        ].isin(
            origens_selecionadas
        )
    ]

if pesquisa_cliente:
    pesquisa = pesquisa_cliente.strip()

    mascara_cliente = (
        df_filtrado[
            "contato_nome"
        ].str.contains(
            pesquisa,
            case=False,
            na=False,
            regex=False,
        )
        | df_filtrado[
            "nome_whatsapp"
        ].str.contains(
            pesquisa,
            case=False,
            na=False,
            regex=False,
        )
        | df_filtrado[
            "telefone"
        ].str.contains(
            pesquisa,
            case=False,
            na=False,
            regex=False,
        )
        | df_filtrado[
            "telefone_formatado"
        ].str.contains(
            pesquisa,
            case=False,
            na=False,
            regex=False,
        )
    )

    df_filtrado = df_filtrado[
        mascara_cliente
    ]

if pesquisa_mensagem:
    df_filtrado = df_filtrado[
        df_filtrado["texto"].str.contains(
            pesquisa_mensagem.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]


# ============================================================
# INDICADORES
# ============================================================

total_mensagens = len(df_filtrado)

total_sessoes = df_filtrado[
    "sessao_id"
].nunique()

total_contatos = df_filtrado[
    "contato_id"
].nunique()

contatos_unicos = (
    df_filtrado[
        [
            "contato_id",
            "vendedor_responsavel",
        ]
    ]
    .drop_duplicates(
        subset=["contato_id"]
    )
)

contatos_identificados = len(
    contatos_unicos[
        contatos_unicos[
            "vendedor_responsavel"
        ]
        != "Não identificado"
    ]
)

if total_contatos > 0:
    percentual_identificado = (
        contatos_identificados
        / total_contatos
        * 100
    )
else:
    percentual_identificado = 0


st.markdown(
    '<div class="status-atualizacao">'
    f'Exibindo {total_mensagens:,} mensagens '
    'após os filtros.'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")

metrica_1, metrica_2, metrica_3, metrica_4 = st.columns(
    4
)

with metrica_1:
    st.metric(
        "Mensagens",
        f"{total_mensagens:,}".replace(
            ",",
            ".",
        ),
    )

with metrica_2:
    st.metric(
        "Conversas",
        f"{total_sessoes:,}".replace(
            ",",
            ".",
        ),
    )

with metrica_3:
    st.metric(
        "Contatos",
        f"{total_contatos:,}".replace(
            ",",
            ".",
        ),
    )

with metrica_4:
    st.metric(
        "Contatos identificados",
        f"{percentual_identificado:.1f}%"
        .replace(
            ".",
            ",",
        ),
    )


if df_filtrado.empty:
    st.warning(
        "Nenhum registro corresponde "
        "aos filtros selecionados."
    )
    st.stop()


# ============================================================
# ABAS
# ============================================================

aba_visao_geral, aba_vendedores, aba_conversas = st.tabs(
    [
        "📊 Visão geral",
        "👥 Vendedores",
        "💬 Conversas",
    ]
)


# ============================================================
# ABA VISÃO GERAL
# ============================================================

with aba_visao_geral:
    coluna_grafico_1, coluna_grafico_2 = st.columns(
        2
    )

    mensagens_por_dia = (
        df_filtrado
        .groupby("data")
        .size()
        .reset_index(
            name="mensagens"
        )
        .sort_values("data")
    )

    figura_evolucao = px.line(
        mensagens_por_dia,
        x="data",
        y="mensagens",
        markers=True,
        title="Evolução diária das mensagens",
        labels={
            "data": "Data",
            "mensagens": "Mensagens",
        },
    )

    figura_evolucao.update_traces(
        line_color="#2563EB",
        line_width=3,
    )

    figura_evolucao.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        hovermode="x unified",
    )

    with coluna_grafico_1:
        st.plotly_chart(
            figura_evolucao,
            use_container_width=True,
        )

    mensagens_por_tipo = (
        df_filtrado
        .groupby("tipo_mensagem")
        .size()
        .reset_index(
            name="quantidade"
        )
        .sort_values(
            "quantidade",
            ascending=False,
        )
    )

    figura_tipos = px.bar(
        mensagens_por_tipo,
        x="tipo_mensagem",
        y="quantidade",
        title="Mensagens por tipo",
        labels={
            "tipo_mensagem": "Tipo",
            "quantidade": "Quantidade",
        },
        color="quantidade",
        color_continuous_scale="Blues",
    )

    figura_tipos.update_layout(
        coloraxis_showscale=False,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    with coluna_grafico_2:
        st.plotly_chart(
            figura_tipos,
            use_container_width=True,
        )

    coluna_grafico_3, coluna_grafico_4 = st.columns(
        2
    )

    sessoes_por_status = (
        df_filtrado[
            [
                "sessao_id",
                "status_sessao",
            ]
        ]
        .drop_duplicates()
        .groupby("status_sessao")
        .size()
        .reset_index(
            name="conversas"
        )
        .sort_values(
            "conversas",
            ascending=False,
        )
    )

    figura_status = px.pie(
        sessoes_por_status,
        names="status_sessao",
        values="conversas",
        hole=0.55,
        title="Conversas por status",
    )

    figura_status.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    with coluna_grafico_3:
        st.plotly_chart(
            figura_status,
            use_container_width=True,
        )

    mensagens_por_canal = (
        df_filtrado
        .groupby("canal")
        .size()
        .reset_index(
            name="mensagens"
        )
        .sort_values(
            "mensagens",
            ascending=False,
        )
    )

    figura_canais = px.bar(
        mensagens_por_canal,
        x="canal",
        y="mensagens",
        title="Mensagens por canal comercial",
        labels={
            "canal": "Canal",
            "mensagens": "Mensagens",
        },
        color="canal",
    )

    figura_canais.update_layout(
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    with coluna_grafico_4:
        st.plotly_chart(
            figura_canais,
            use_container_width=True,
        )


# ============================================================
# ABA VENDEDORES
# ============================================================

with aba_vendedores:
    contatos_por_vendedor = (
        df_filtrado[
            [
                "contato_id",
                "vendedor_responsavel",
                "origem_vendedor",
            ]
        ]
        .drop_duplicates(
            subset=["contato_id"]
        )
        .groupby(
            [
                "vendedor_responsavel",
                "origem_vendedor",
            ]
        )
        .size()
        .reset_index(
            name="contatos"
        )
        .sort_values(
            "contatos",
            ascending=False,
        )
    )

    figura_vendedores = px.bar(
        contatos_por_vendedor,
        x="contatos",
        y="vendedor_responsavel",
        orientation="h",
        color="origem_vendedor",
        title="Contatos por vendedor responsável",
        labels={
            "contatos": "Contatos",
            "vendedor_responsavel":
                "Vendedor",
            "origem_vendedor":
                "Origem",
        },
    )

    figura_vendedores.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        },
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        figura_vendedores,
        use_container_width=True,
    )

    st.subheader(
        "Resumo por vendedor"
    )

    resumo_vendedores = (
        df_filtrado
        .groupby(
            "vendedor_responsavel"
        )
        .agg(
            contatos=(
                "contato_id",
                "nunique",
            ),
            conversas=(
                "sessao_id",
                "nunique",
            ),
            mensagens=(
                "mensagem_id",
                "count",
            ),
        )
        .reset_index()
        .sort_values(
            "contatos",
            ascending=False,
        )
        .rename(
            columns={
                "vendedor_responsavel":
                    "Vendedor responsável",
                "contatos":
                    "Contatos",
                "conversas":
                    "Conversas",
                "mensagens":
                    "Mensagens",
            }
        )
    )

    st.dataframe(
        resumo_vendedores,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ABA CONVERSAS
# ============================================================

with aba_conversas:
    st.subheader(
        "Mensagens encontradas"
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

    tabela["timestamp_mensagem"] = (
        tabela["timestamp_mensagem"]
        .dt.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    tabela = tabela.rename(
        columns={
            "timestamp_mensagem":
                "Data e hora",
            "vendedor_responsavel":
                "Vendedor",
            "origem_vendedor":
                "Origem do vendedor",
            "contato_nome":
                "Cliente",
            "telefone_formatado":
                "Telefone",
            "canal":
                "Canal",
            "status_sessao":
                "Status da conversa",
            "tipo_mensagem":
                "Tipo",
            "direcao":
                "Direção",
            "usuario_mensagem":
                "Usuário/Bot",
            "texto":
                "Mensagem",
            "sessao_id":
                "ID da sessão",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=550,
    )

    st.subheader(
        "Exportar relatório"
    )

    coluna_csv, coluna_excel = st.columns(
        2
    )

    arquivo_csv = tabela.to_csv(
        index=False,
        sep=";",
    ).encode(
        "utf-8-sig"
    )

    with coluna_csv:
        st.download_button(
            label="⬇️ Baixar CSV",
            data=arquivo_csv,
            file_name="relatorio_botnext.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with coluna_excel:
        st.download_button(
            label="⬇️ Baixar Excel",
            data=gerar_excel(tabela),
            file_name="relatorio_botnext.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            use_container_width=True,
        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Relatório alimentado pela API do BotNext. "
    "Os dados exibidos são provenientes do banco PostgreSQL."
)