"""Gráficos Plotly do dashboard."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shapely.geometry import shape

import dados  # noqa: F401  (ajusta o caminho de src)
from calculos import curva_lorenz, n_para_participacao
from componentes import br
from cores import (
    AZUL_CLARO, CINZA_LINHA, CINZA_RESTO, DIVISA_SUAVE, OURO, SILHUETA, TEXTO,
    TEXTO_FRACO,
)
from dados import carregar_base, carregar_malha
from estatico import garantir_malha
from mapa import ALTURA, CENTRO, FUNDO_COR, LIMITES_MAPA, ZOOM_INICIAL, _camada_fundo
from painel import _reais_mil
from src.indicadores import gini

# Definir as cores dos gráficos
COR_PIB = OURO
COR_POP = AZUL_CLARO
COR_IGUAL = CINZA_LINHA
COR_RESTO = CINZA_RESTO
COR_SILHUETA = SILHUETA
COR_DIVISA = DIVISA_SUAVE
TAMANHO_MAX, TAMANHO_MIN = 55, 2.5   # diâmetro das bolhas em pixels


def fig_lorenz(base):
    """Criar a curva de Lorenz do PIB e da população entre os municípios."""
    n = len(base)
    x_pib, y_pib = curva_lorenz(base["pib"])
    x_pop, y_pop = curva_lorenz(base["populacao"])
    g_pib = gini(base["pib"].to_numpy())
    g_pop = gini(base["populacao"].to_numpy())

    fig = go.Figure()

    # Desenhar a linha de igualdade perfeita
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100], mode="lines", name="Igualdade perfeita",
        line=dict(color=COR_IGUAL, dash="dash", width=1), hoverinfo="skip",
    ))

    # Desenhar as curvas da população e do PIB
    fig.add_trace(go.Scatter(
        x=x_pop, y=y_pop, mode="lines",
        name=f"População · Gini {br(g_pop, 2)}",
        line=dict(color=COR_POP, width=2.5),
        hovertemplate="Os %{x:.1f}% menores municípios<br>somam %{y:.1f}% da população<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x_pib, y=y_pib, mode="lines",
        name=f"PIB · Gini {br(g_pib, 2)}",
        line=dict(color=COR_PIB, width=2.5),
        hovertemplate="Os %{x:.1f}% menores municípios<br>somam %{y:.1f}% do PIB<extra></extra>",
    ))

    # Destacar o ponto em que os maiores municípios somam metade do PIB
    k = n_para_participacao(base["pib"], 0.5)
    xm, ym = x_pib[n - k], y_pib[n - k]
    fig.add_trace(go.Scatter(
        x=[xm], y=[ym], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(color=COR_PIB, size=10, line=dict(color="white", width=1.5)),
    ))
    fig.add_annotation(
        x=xm, y=ym, ax=-150, ay=-90, showarrow=True, arrowhead=2,
        arrowcolor=COR_PIB, font=dict(color=TEXTO, size=13),
        text=f"<b>{k} municípios ({br(k / n * 100, 1)}%)</b><br>concentram 50% do PIB",
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=ALTURA, margin=dict(l=10, r=10, t=10, b=10),
        separators=",.",
        legend=dict(orientation="h", x=0, y=1.06),
        xaxis=dict(title="% acumulado dos municípios (do menor para o maior)",
                   ticksuffix="%", range=[0, 100]),
        yaxis=dict(title="% acumulado do total", ticksuffix="%", range=[0, 100]),
    )
    return fig


@st.cache_data
def _centroides():
    """Calcular o centro de cada município a partir da malha."""
    malha = carregar_malha("Município")
    linhas = []
    for feature in malha["features"]:
        centro = shape(feature["geometry"]).centroid
        linhas.append((str(feature["properties"]["cod"]), centro.x, centro.y))
    return pd.DataFrame(linhas, columns=["cod", "lon", "lat"])


def _bolhas(df, total, nome, cor, opacidade, pib_max):
    """Criar um traço de bolhas com área proporcional ao PIB."""
    tamanho = np.maximum(TAMANHO_MIN, np.sqrt(df["pib"] / pib_max) * TAMANHO_MAX)
    textos = np.column_stack([
        [_reais_mil(v) for v in df["pib"]],
        [br(v / total * 100, 2) + "%" for v in df["pib"]],
    ])
    return go.Scattermap(
        lon=df["lon"], lat=df["lat"], mode="markers", name=nome,
        text=df["nome"] + " (" + df["uf_sigla"] + ")", customdata=textos,
        marker=dict(size=tamanho, color=cor, opacity=opacidade),
        hovertemplate="<b>%{text}</b><br>PIB: %{customdata[0]}<br>"
                      "%{customdata[1]} do PIB nacional<extra></extra>",
    )


def fig_bolhas(base):
    """Criar o mapa de bolhas: os maiores PIBs destacados sobre os demais."""
    df = base.assign(cod=base["cod"].astype(str)).merge(_centroides(), on="cod")
    df = df.sort_values("pib", ascending=False)
    k = n_para_participacao(df["pib"], 0.5)
    total, pib_max = df["pib"].sum(), df["pib"].max()

    # Desenhar a silhueta do Brasil com as divisas estaduais
    estados = carregar_base("Estado")
    silhueta = go.Choroplethmap(
        geojson=garantir_malha("Estado"),
        locations=estados["uf_cod"], featureidkey="properties.uf_cod",
        z=[0] * len(estados), colorscale=[[0, COR_SILHUETA], [1, COR_SILHUETA]],
        showscale=False, hoverinfo="skip",
        marker=dict(opacity=1, line=dict(width=0.8, color=COR_DIVISA)),
    )

    # Desenhar as bolhas: primeiro os demais, depois os maiores
    resto = _bolhas(df.iloc[k:], total, "Demais municípios", COR_RESTO, 0.55, pib_max)
    top = _bolhas(df.iloc[:k], total, f"{k} maiores (metade do PIB)", COR_PIB, 0.8, pib_max)

    fig = go.Figure([silhueta, resto, top])
    fig.add_annotation(
        text="Área da bolha proporcional ao PIB", xref="paper", yref="paper",
        x=0.01, y=0.01, showarrow=False, font=dict(color=TEXTO_FRACO, size=12),
    )
    fig.update_layout(
        map=dict(
            style="white-bg", center=CENTRO, zoom=ZOOM_INICIAL,
            bounds=LIMITES_MAPA, layers=[_camada_fundo()],
        ),
        paper_bgcolor=FUNDO_COR, height=ALTURA,
        margin=dict(l=0, r=0, t=0, b=0), separators=",.",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(14,17,23,0.7)",
                    font=dict(color=TEXTO)),
    )
    return fig
