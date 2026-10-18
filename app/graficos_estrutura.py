"""Gráficos da página de estrutura produtiva."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import dados  # noqa: F401  (ajusta o caminho de src)
from componentes import br
from cores import (
    AZUL_CLARO, COR_SETOR, GRADE, OURO, QL_ABAIXO, QL_NEUTRO, TEXTO, TEXTO_ESCURO,
    TEXTO_SUAVE,
)
from dados import carregar_base, carregar_malha
from estatico import garantir_malha
from mapa import (
    ALTURA, CENTRO, DIVISA_COR, DIVISA_LARGURA, FUNDO_COR, LIMITE_COR,
    LIMITE_LARGURA, LIMITES_MAPA, ZOOM_INICIAL,
    _camada_fundo, _escala_discreta, _linhas_divisa,
)

# Definir os setores (do maior ao menor peso nacional), nomes e cores
SETORES = ["vab_servicos", "vab_industria", "vab_adm_publica", "vab_agro"]
NOMES = {
    "vab_servicos": "Serviços", "vab_industria": "Indústria",
    "vab_adm_publica": "Adm. pública", "vab_agro": "Agropecuária",
}
CORES = COR_SETOR

# Definir as cores das séries (dourado = valor, azul = território)
COR_VALOR = OURO
COR_TERRITORIO = AZUL_CLARO

# Definir a margem superior que comporta o subtítulo de três linhas
MARGEM_TOPO = 84

# Definir as faixas do mapa (iguais para todos os setores)
FAIXAS_SETOR = [0, 10, 25, 40, 55, 101]
ROTULOS_SETOR = [
    "Menos de 10%", "10% a 25%", "25% a 40%", "40% a 55%", "55% ou mais",
]

# Definir a rampa: 0 fundo escuro, PONTO_PLENO cor do setor, 1 claro
POSICOES = [0.20, 0.38, 0.58, 0.78, 1.00]
PONTO_PLENO = 0.60
CLAREAR = 0.45
BASE_ESCURA = (35, 40, 52)

# Definir a escala do QL: azul (<1), neutro (1), dourado (>1)
QL_MAX = 3.0
ESCALA_QL = [[0.0, QL_ABAIXO], [1 / QL_MAX, QL_NEUTRO], [1.0, OURO]]

# Definir texto das células: escuro no dourado forte, claro no resto
LIMIAR_DOURADO = 2.4
TEXTO_CLARO = TEXTO


@st.cache_data
def resumo_setores():
    """Calcular peso nacional, mediana dos municípios e setor dominante."""
    base = carregar_base("Município")
    partes = ["part_" + s for s in SETORES]

    # Somar a economia de todos os municípios (mesmo critério do card Brasil)
    soma = {s: base[s].sum() for s in SETORES}
    total = sum(soma.values())
    nacional = {s: soma[s] / total * 100 for s in SETORES}

    # Usar só municípios com composição válida na mediana e no dominante
    df = base[base[partes].notna().all(axis=1)]
    mediana = {s: df["part_" + s].median() for s in SETORES}
    contagem = df[partes].idxmax(axis=1).value_counts(normalize=True) * 100
    dominante = {s: float(contagem.get("part_" + s, 0.0)) for s in SETORES}
    return nacional, mediana, dominante


def _subtitulo(fig, texto):
    """Adicionar um subtítulo alinhado à esquerda, acima da área do gráfico."""
    fig.add_annotation(
        xref="paper", yref="paper", x=0, y=1.0, xanchor="left", yanchor="bottom",
        showarrow=False, align="left", font=dict(size=12, color=TEXTO_SUAVE),
        text=texto,
    )


def fig_valor_territorio():
    """Criar barras agrupadas: peso nacional × mediana dos municípios."""
    nacional, mediana, _ = resumo_setores()
    nomes = [NOMES[s] for s in SETORES]

    fig = go.Figure()
    series = [
        (
            "Brasil: soma de todos os municípios", nacional, COR_VALOR,
            "<b>%{x}</b><br>No país todo: %{y:.1f}% da economia<extra></extra>",
        ),
        (
            "Mediana dos municípios (metade acima, metade abaixo)", mediana,
            COR_TERRITORIO,
            "Mediana dos municípios: em metade deles o peso de <b>%{x}</b> "
            "é menor que %{y:.1f}%;<br>na outra metade, é maior.<extra></extra>",
        ),
    ]
    for nome, dados_serie, cor, dica in series:
        fig.add_trace(go.Bar(
            x=nomes, y=[dados_serie[s] for s in SETORES], name=nome,
            marker_color=cor, texttemplate="%{y:.1f}%", textposition="outside",
            textfont=dict(color=TEXTO, size=13), hovertemplate=dica,
        ))

    # Explicar a barra azul em linhas curtas (cabem em qualquer largura)
    _subtitulo(fig, (
        "<b>Barra azul</b>: mediana dos municípios. Em metade deles o<br>"
        "setor pesa menos que isso; na outra metade, pesa mais.<br>"
        "Cada setor é calculado à parte, e as azuis não somam 100%."
    ))

    fig.update_layout(
        barmode="group", bargap=0.3, bargroupgap=0.06,
        height=ALTURA, separators=",.",
        paper_bgcolor=FUNDO_COR, plot_bgcolor=FUNDO_COR,
        font=dict(color=TEXTO_SUAVE), margin=dict(l=10, r=10, t=MARGEM_TOPO, b=10),
        # Ancorar a legenda no canto superior direito (área vazia)
        legend=dict(
            x=0.99, y=0.98, xanchor="right", yanchor="top",
            bgcolor="rgba(14,17,23,0.7)", font=dict(color=TEXTO),
        ),
        xaxis=dict(showgrid=False, tickfont=dict(size=14)),
        yaxis=dict(
            title="Participação na economia (%)", gridcolor=GRADE,
            zeroline=False, rangemode="tozero",
        ),
    )
    return fig


def _misturar(a, b, t):
    """Interpolar duas cores RGB (t=0 devolve a, t=1 devolve b)."""
    return [round(x + (y - x) * t) for x, y in zip(a, b)]


def _cor_faixa(cor_hex, u):
    """Calcular a cor de uma faixa: fundo escuro → cor do setor → tom claro."""
    rgb = [int(cor_hex[i:i + 2], 16) for i in (1, 3, 5)]
    claro = _misturar(rgb, (255, 255, 255), CLAREAR)
    if u <= PONTO_PLENO:
        mix = _misturar(BASE_ESCURA, rgb, u / PONTO_PLENO)
    else:
        mix = _misturar(rgb, claro, (u - PONTO_PLENO) / (1 - PONTO_PLENO))
    return "#{:02x}{:02x}{:02x}".format(*mix)


@st.cache_resource(show_spinner="Montando o mapa...")
def mapa_setor(setor):
    """Criar o mapa do peso de um setor na economia, em faixas."""
    col = "part_" + setor
    base = carregar_base("Município")
    df = base[base[col].notna()].copy()

    # Montar a rampa de cores do setor
    cores = [_cor_faixa(CORES[setor], u) for u in POSICOES]

    # Classificar cada município em uma faixa (0 a 4)
    faixa = pd.cut(df[col], bins=FAIXAS_SETOR, labels=False, right=False)
    texto = [br(v, 1) + "%" for v in df[col]]

    # Desenhar todos os municípios em um único traço (geometria por URL)
    territorios = go.Choroplethmap(
        geojson=garantir_malha("Município"),
        locations=df["cod"], featureidkey="properties.cod",
        z=faixa, zmin=-0.5, zmax=len(cores) - 0.5,
        colorscale=_escala_discreta(cores), showscale=False,
        text=df["nome"], customdata=texto,
        hovertemplate=(
            "<b>%{text}</b><br>" + NOMES[setor]
            + ": %{customdata} da economia<extra></extra>"
        ),
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
        for cor, rotulo in zip(cores, ROTULOS_SETOR)
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
            title=dict(text=f"Peso de {NOMES[setor].lower()} na economia"),
            font=dict(color=TEXTO),
        ),
    )
    return fig


@st.cache_data
def tabela_ql():
    """Calcular o QL por estado e setor, além dos pesos (estado e país)."""
    base = carregar_base("Município")

    # Somar a economia de cada setor por estado
    uf = base.groupby("uf_sigla")[SETORES].sum()
    peso_uf = uf.div(uf.sum(axis=1), axis=0)
    peso_br = uf.sum() / uf.sum().sum()

    # Dividir o peso do estado pelo peso do país
    ql = peso_uf / peso_br
    return ql, peso_uf * 100, peso_br * 100


def fig_ql(setor):
    """Criar o mapa de calor do QL (estados × setores), ordenado pelo setor."""
    ql, peso_uf, peso_br = tabela_ql()

    # Ordenar os estados pelo QL do setor escolhido
    ordem = list(ql[setor].sort_values(ascending=False).index)
    z = ql.loc[ordem, SETORES]
    valores = z.values
    x = [f"{NOMES[s]}<br>(país: {br(peso_br[s], 1)}%)" for s in SETORES]

    fig = go.Figure(go.Heatmap(
        z=valores, x=x, y=ordem,
        colorscale=ESCALA_QL, zmin=0, zmax=QL_MAX, showscale=False,
        xgap=2, ygap=2, hoverongaps=False,
        customdata=peso_uf.loc[ordem, SETORES].values,
        hovertemplate=(
            "<b>%{y} · %{x}</b><br>QL: %{z:.2f}"
            "<br>Peso no estado: %{customdata:.1f}%<extra></extra>"
        ),
    ))

    # Escrever o QL em cada célula (cor do texto conforme o fundo)
    for i in range(len(ordem)):
        for j in range(len(SETORES)):
            v = valores[i][j]
            cor = TEXTO_ESCURO if v >= LIMIAR_DOURADO else TEXTO_CLARO
            fig.add_annotation(
                x=j, y=i, text=br(v, 2), showarrow=False,
                font=dict(size=13, color=cor),
            )

    # Explicar o QL em linhas curtas (cabem em qualquer largura)
    _subtitulo(fig, (
        "<b>QL</b> = peso do setor no estado ÷ peso no país.<br>"
        "Dourado: acima de 1 (mais especializado); azul: abaixo.<br>"
        "Estados ordenados pelo setor escolhido na barra lateral."
    ))

    fig.update_layout(
        height=ALTURA, separators=",.",
        paper_bgcolor=FUNDO_COR, plot_bgcolor=FUNDO_COR,
        font=dict(color=TEXTO_SUAVE), margin=dict(l=10, r=10, t=MARGEM_TOPO, b=10),
        xaxis=dict(side="bottom", tickfont=dict(size=12)),
        yaxis=dict(
            type="category", autorange="reversed", tickmode="array",
            tickvals=ordem, ticktext=ordem, tickfont=dict(size=12),
        ),
    )
    return fig
