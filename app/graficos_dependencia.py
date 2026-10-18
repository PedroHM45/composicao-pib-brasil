"""Gráficos da página de dependência da administração pública."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import dados  # noqa: F401  (ajusta o caminho de src)
from componentes import br
from cores import (
    CINZA_LINHA, COR_REGIAO, GRADE, PORTE_ROXO, RAMPA_ROXO, TEXTO, TEXTO_FRACO,
    TEXTO_SUAVE,
)
from dados import carregar_base, carregar_malha
from estatico import garantir_malha
from mapa import (
    ALTURA, CENTRO, DIVISA_COR, DIVISA_LARGURA, FUNDO_COR, LIMITE_COR,
    LIMITE_LARGURA, LIMITES_MAPA, ZOOM_INICIAL,
    _camada_fundo, _escala_discreta, _linhas_divisa,
)
from src.visual import ORDEM_REGIOES

# Definir coluna, faixas e cores do mapa (do claro ao escuro)
COL = "part_vab_adm_publica"
FAIXAS = [0, 15, 30, 45, 60, 101]
ROTULOS = ["Menos de 15%", "15% a 30%", "30% a 45%", "45% a 60%", "60% ou mais"]
CORES = RAMPA_ROXO

# Definir os portes (limites em habitantes) e suas cores
PORTES = ["Até 20 mil hab.", "20 a 100 mil hab.", "Mais de 100 mil hab."]
LIMITES_PORTE = [0, 20_000, 100_000, np.inf]
CORES_PORTE = PORTE_ROXO

# Definir as cores das regiões na dispersão (roxo reservado à adm. pública)
CORES_REGIAO = COR_REGIAO
# Desenhar o Nordeste por último, para ficar sobre os demais
ORDEM_DESENHO = ["Sul", "Sudeste", "Centro-Oeste", "Norte", "Nordeste"]

# Definir os marcadores de renda no eixo y (escala log)
TICKS_RENDA = [5_000, 10_000, 20_000, 50_000, 100_000, 200_000]
LABELS_RENDA = ["5 mil", "10 mil", "20 mil", "50 mil", "100 mil", "200 mil"]


@st.cache_resource(show_spinner="Montando o mapa...")
def mapa_dependencia():
    """Criar o mapa do peso da adm. pública na economia, em faixas."""
    base = carregar_base("Município")
    df = base[base[COL].notna()].copy()

    # Classificar cada município em uma faixa (0 a 4)
    faixa = pd.cut(df[COL], bins=FAIXAS, labels=False, right=False)
    texto = [br(v, 1) + "%" for v in df[COL]]

    # Desenhar todos os municípios em um único traço (geometria por URL)
    territorios = go.Choroplethmap(
        geojson=garantir_malha("Município"),
        locations=df["cod"], featureidkey="properties.cod",
        z=faixa, zmin=-0.5, zmax=len(CORES) - 0.5,
        colorscale=_escala_discreta(CORES), showscale=False,
        text=df["nome"], customdata=texto,
        hovertemplate="<b>%{text}</b><br>Adm. pública: %{customdata} da economia<extra></extra>",
        marker=dict(opacity=1, line=dict(width=LIMITE_LARGURA, color=LIMITE_COR)),
    )

    # Desenhar as divisas dos estados
    lon, lat = _linhas_divisa(carregar_malha("Estado"))
    divisa = go.Scattermap(
        lon=lon, lat=lat, mode="lines", showlegend=False, hoverinfo="skip",
        line=dict(width=DIVISA_LARGURA, color=DIVISA_COR),
    )

    # Criar a legenda das faixas (traços vazios, só com nome e cor)
    legenda = [
        go.Scattermap(
            lon=[None], lat=[None], mode="markers", name=rotulo,
            marker=dict(size=11, color=cor),
        )
        for cor, rotulo in zip(CORES, ROTULOS)
    ]

    fig = go.Figure([territorios, divisa, *legenda])
    fig.update_layout(
        map=dict(
            style="white-bg", center=CENTRO, zoom=ZOOM_INICIAL,
            bounds=LIMITES_MAPA, layers=[_camada_fundo()],
        ),
        paper_bgcolor=FUNDO_COR, height=ALTURA,
        margin=dict(l=0, r=0, t=0, b=0), separators=",.",
        # Ancorar a legenda no canto inferior esquerdo
        legend=dict(
            x=0.01, y=0.01, xanchor="left", yanchor="bottom",
            bgcolor="rgba(14,17,23,0.7)",
            title=dict(text="Peso da adm. pública na economia"),
            font=dict(color=TEXTO),
        ),
    )
    return fig


@st.cache_data
def _resumo_regiao_porte():
    """Calcular mediana e contagem do peso da adm. pública por região e porte."""
    base = carregar_base("Município")
    df = base[base[COL].notna()].copy()

    # Classificar cada município em um porte
    df["porte"] = pd.cut(
        df["populacao"], bins=LIMITES_PORTE, labels=PORTES, right=True
    )

    # Agrupar por região e porte
    grupo = df.groupby(["regiao", "porte"], observed=False)[COL]
    mediana = grupo.median().unstack("porte").reindex(ORDEM_REGIOES)
    contagem = grupo.size().unstack("porte").reindex(ORDEM_REGIOES)
    return mediana, contagem


def fig_regiao_porte():
    """Criar barras agrupadas: região no eixo x, porte como série."""
    mediana, contagem = _resumo_regiao_porte()

    fig = go.Figure()
    for porte, cor in zip(PORTES, CORES_PORTE):
        fig.add_trace(go.Bar(
            x=mediana.index, y=mediana[porte], name=porte,
            marker_color=cor,
            customdata=contagem[porte],
            texttemplate="%{y:.1f}%", textposition="outside",
            textfont=dict(color=TEXTO, size=12),
            hovertemplate=(
                "<b>%{x} · " + porte + "</b><br>"
                "Mediana: %{y:.1f}%<br>"
                "Municípios: %{customdata:,.0f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="group", bargap=0.25, bargroupgap=0.06,
        height=ALTURA, separators=",.",
        paper_bgcolor=FUNDO_COR, plot_bgcolor=FUNDO_COR,
        font=dict(color=TEXTO_SUAVE),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", x=0, y=1.08, yanchor="bottom"),
        xaxis=dict(showgrid=False, tickfont=dict(size=13)),
        yaxis=dict(
            title="Mediana do peso da adm. pública na economia (%)",
            gridcolor=GRADE, zeroline=False, rangemode="tozero",
        ),
    )
    return fig


@st.cache_data
def _dados_dispersao():
    """Filtrar municípios válidos e calcular medianas e correlação."""
    base = carregar_base("Município")
    df = base[base[COL].notna() & (base["pib_per_capita"] > 0)].copy()
    rho = df[COL].corr(df["pib_per_capita"], method="spearman")
    return df, df[COL].median(), df["pib_per_capita"].median(), rho


def fig_dispersao():
    """Criar a dispersão: peso da adm. pública × PIB per capita (log)."""
    df, med_x, med_y, rho = _dados_dispersao()
    fig = go.Figure()

    # Criar a legenda com marcadores opacos (um por região)
    for regiao in ORDEM_REGIOES:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers", name=regiao, legendgroup=regiao,
            marker=dict(size=10, color=CORES_REGIAO.get(regiao, TEXTO_FRACO)),
            hoverinfo="skip",
        ))

    # Desenhar um traço por região (Scattergl para fluidez)
    for regiao in ORDEM_DESENHO:
        d = df[df["regiao"] == regiao]
        fig.add_trace(go.Scattergl(
            x=d[COL], y=d["pib_per_capita"], mode="markers", name=regiao,
            legendgroup=regiao, showlegend=False,
            marker=dict(size=5, opacity=0.55, color=CORES_REGIAO[regiao]),
            text=d["nome"],
            hovertemplate=(
                "<b>%{text}</b><br>Adm. pública: %{x:.1f}% da economia"
                "<br>PIB per capita: R$ %{y:,.0f}<extra></extra>"
            ),
        ))

    # Marcar as medianas (quatro quadrantes)
    linha = dict(color=CINZA_LINHA, dash="dash", width=1)
    fig.add_vline(x=med_x, line=linha)
    fig.add_hline(y=med_y, line=linha)

    # Exibir a correlação no canto superior direito
    fig.add_annotation(
        xref="paper", yref="paper", x=0.99, y=0.98, xanchor="right", yanchor="top",
        showarrow=False, align="right", font=dict(color=TEXTO, size=13),
        text=f"Correlação de Spearman: <b>{br(rho, 2)}</b><br>"
             f"<span style='font-size:11px;color:{TEXTO_FRACO}'>associação, não causa</span>",
    )

    fig.update_layout(
        height=ALTURA, separators=",.",
        paper_bgcolor=FUNDO_COR, plot_bgcolor=FUNDO_COR,
        font=dict(color=TEXTO_SUAVE), margin=dict(l=10, r=10, t=20, b=90),
        # Ancorar a legenda abaixo do título do eixo x (horizontal, centralizada)
        legend=dict(
            orientation="h", xanchor="center", x=0.5,
            yref="container", yanchor="bottom", y=0.0,
            itemsizing="constant", font=dict(size=13, color=TEXTO),
        ),
        xaxis=dict(
            title="Peso da adm. pública na economia", ticksuffix="%",
            gridcolor=GRADE, zeroline=False, rangemode="tozero",
        ),
        yaxis=dict(
            title="PIB per capita (R$, escala log)", type="log",
            tickvals=TICKS_RENDA, ticktext=LABELS_RENDA,
            gridcolor=GRADE, zeroline=False,
        ),
    )
    return fig
