"""Gráfico comparativo das regiões."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dados  # noqa: F401  (ajusta o caminho de src)
from componentes import br
from graficos import COR_PIB, COR_POP
from mapa import ALTURA
from src.visual import ORDEM_REGIOES


def fig_regioes(base):
    """Criar o comparativo regional: PIB x população e PIB per capita mediano."""
    grupo = base.groupby("regiao")
    pct_pib = (grupo["pib"].sum() / base["pib"].sum() * 100).reindex(ORDEM_REGIOES)
    pct_pop = (grupo["populacao"].sum() / base["populacao"].sum() * 100).reindex(ORDEM_REGIOES)
    mediana = grupo["pib_per_capita"].median().reindex(ORDEM_REGIOES)

    fig = make_subplots(
        rows=2, cols=1, vertical_spacing=0.2,
        subplot_titles=(
            "Participação de cada região no PIB e na população",
            "PIB per capita mediano dos municípios",
        ),
    )

    # Painel de cima: PIB e população lado a lado
    fig.add_trace(go.Bar(
        x=ORDEM_REGIOES, y=pct_pib, name="PIB", marker_color=COR_PIB,
        text=[br(v, 1) + "%" for v in pct_pib], textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:.1f}% do PIB do Brasil<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=ORDEM_REGIOES, y=pct_pop, name="População", marker_color=COR_POP,
        text=[br(v, 1) + "%" for v in pct_pop], textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:.1f}% da população do Brasil<extra></extra>",
    ), row=1, col=1)

    # Painel de baixo: PIB per capita mediano
    fig.add_trace(go.Bar(
        x=ORDEM_REGIOES, y=mediana, showlegend=False, marker_color=COR_PIB,
        text=[f"R$ {br(v / 1000, 1)} mil" for v in mediana],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{x}<br>Mediana: R$ %{y:,.0f}<extra></extra>",
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=ALTURA, margin=dict(l=10, r=10, t=40, b=10),
        separators=",.", barmode="group",
        legend=dict(orientation="h", x=0, y=1.1),
    )
    fig.update_yaxes(range=[0, pct_pib.max() * 1.25], ticksuffix="%", row=1, col=1)
    fig.update_yaxes(range=[0, mediana.max() * 1.25], row=2, col=1)
    return fig
