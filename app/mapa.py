"""Construção do mapa do Brasil."""
import plotly.graph_objects as go
import streamlit as st
from shapely.geometry import shape

from cores import FUNDO, TEXTO_FRACO
from dados import NIVEIS, carregar_base, carregar_malha
from estatico import garantir_malha
from src.config import SETORES
from src.visual import CORES_SETORES, NOMES_SETORES

# Definir a vista inicial (zoom menor mostra mais área)
CENTRO = dict(lat=-14.2, lon=-51.9)
ZOOM_INICIAL = 3.1
ALTURA = 650

# Delimitar a área navegável, rente ao território
LIMITES_MAPA = dict(west=-95, east=-15, south=-50, north=20)

# Servir a geometria por URL (figura leve); False volta ao modo antigo
USAR_URL = True

# Definir a malha das divisas em destaque para cada nível
MALHA_DIVISA = {"Município": "Estado", "Estado": "Estado", "Região": "Região"}
DIVISA_SIMPLIFICAR = 0.01   # tolerância em graus; None desliga

# Definir rótulos por nível: coluna e tamanho (Município sem rótulo)
ROTULO_COLUNA = {"Estado": "uf_sigla", "Região": "regiao"}
ROTULO_TAMANHO = {"Estado": 11, "Região": 14}
TEXTO_ESCURO, TEXTO_CLARO = "#111111", "#f5f5f5"
LIMIAR_LUMINANCIA = 0.30   # acima disso, usar texto escuro

# Definir rótulos de estados pequenos: sigla -> (lon, lat) da chamada
ROTULO_FORA = {
    "Estado": {
        "RN": (-33.5, -5.5),
        "PB": (-33.5, -7.0),
        "PE": (-33.5, -8.5),
        "AL": (-33.5, -10.0),
        "SE": (-33.5, -11.5),
    },
    "Região": {},
}
CHAMADA_COR, CHAMADA_LARGURA = TEXTO_FRACO, 0.8
CHAMADA_RECUO = 0.8        # graus a leste da ponta da linha, onde fica o texto
CHAMADA_TEXTO = "#ffffff"

# Definir nomes e colunas dos setores
NOME = dict(zip(SETORES, NOMES_SETORES))
PARTES = [f"part_{s}" for s in SETORES]
CORES = [CORES_SETORES[n] for n in NOMES_SETORES]

# Definir o estilo (igual em todos os níveis): hierarquia só pela espessura
LIMITE_COR, LIMITE_LARGURA = "#1a1a1a", 0.3   # entre territórios
DIVISA_COR, DIVISA_LARGURA = "#111111", 1.4   # divisa em destaque
FUNDO_COR = FUNDO


def _escala_discreta(cores):
    """Criar escala em degraus: uma cor fixa para cada categoria."""
    n = len(cores)
    escala = []
    for i, cor in enumerate(cores):
        escala += [[i / n, cor], [(i + 1) / n, cor]]
    return escala


def _setor_dominante(base):
    """Marcar o setor de maior participação no VAB de cada território."""
    # Manter só territórios com participações válidas
    valido = base[PARTES].notna().all(axis=1)
    df = base.loc[valido].copy()

    # Identificar o setor de maior peso e traduzir para o nome
    maior = df[PARTES].idxmax(axis=1).str.replace("part_", "", regex=False)
    df["setor_dominante"] = maior.map(NOME)
    return df


def _linhas_divisa(malha_divisa):
    """Extrair os contornos simplificados como sequência de pontos."""
    lon, lat = [], []
    for feature in malha_divisa["features"]:
        geometria = shape(feature["geometry"])

        # Reduzir os vértices para aliviar a figura
        if DIVISA_SIMPLIFICAR:
            geometria = geometria.simplify(DIVISA_SIMPLIFICAR, preserve_topology=True)
        poligonos = geometria.geoms if geometria.geom_type == "MultiPolygon" else [geometria]

        for poligono in poligonos:
            for anel in [poligono.exterior, *poligono.interiors]:
                xs, ys = anel.xy
                # Separar cada anel com None para não ligar contornos distintos
                lon += list(xs) + [None]
                lat += list(ys) + [None]
    return lon, lat


def _luminancia(cor_hex):
    """Calcular a luminância relativa de uma cor hexadecimal (0 a 1)."""
    canais = []
    for i in (1, 3, 5):
        c = int(cor_hex[i:i + 2], 16) / 255
        canais.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def _cor_texto(cor_fundo):
    """Escolher texto escuro ou claro conforme o contraste com o fundo."""
    if not isinstance(cor_fundo, str):
        return TEXTO_CLARO
    return TEXTO_ESCURO if _luminancia(cor_fundo) > LIMIAR_LUMINANCIA else TEXTO_CLARO


def _ponto_rotulo(geometria):
    """Calcular o ponto do rótulo: centroide do maior polígono (se estiver dentro)."""
    if geometria.geom_type == "MultiPolygon":
        geometria = max(geometria.geoms, key=lambda g: g.area)

    # Preferir o centro geométrico; recorrer ao ponto interno se cair fora
    centro = geometria.centroid
    return centro if geometria.contains(centro) else geometria.representative_point()


def _criar_rotulos(malha, base, df, cfg, coluna, tamanho, fora):
    """Criar os rótulos do nível: dentro do território ou em chamada no oceano."""
    # Manter a coluna do id (drop=False): no nível Região, id e texto coincidem
    textos = base.set_index(cfg["id"], drop=False)[coluna]
    cores = df.set_index(cfg["id"])["setor_dominante"].map(CORES_SETORES)

    # Separar os rótulos internos (por cor do texto) dos rótulos em chamada
    grupos = {TEXTO_ESCURO: ([], [], []), TEXTO_CLARO: ([], [], [])}
    ch_lon, ch_lat = [], []              # linhas das chamadas
    f_lon, f_lat, f_texto = [], [], []   # textos das chamadas

    for feature in malha["features"]:
        id_ = feature["properties"][cfg["id"]]
        ponto = _ponto_rotulo(shape(feature["geometry"]))
        texto = str(textos.get(id_, ""))

        # Mandar o rótulo para o oceano quando o território for pequeno
        if texto in fora:
            lon_fim, lat_fim = fora[texto]
            ch_lon += [ponto.x, lon_fim, None]
            ch_lat += [ponto.y, lat_fim, None]
            # Centralizar o texto logo após a ponta da linha
            f_lon.append(lon_fim + CHAMADA_RECUO)
            f_lat.append(lat_fim)
            f_texto.append(texto)
            continue

        lon, lat, lista = grupos[_cor_texto(cores.get(id_))]
        lon.append(ponto.x)
        lat.append(ponto.y)
        lista.append(texto)

    # Criar um traço por cor de texto (o Plotly aceita uma cor por traço)
    tracos = [
        go.Scattermap(
            lon=lon, lat=lat, mode="text", text=lista,
            textfont=dict(size=tamanho, color=cor), hoverinfo="skip",
        )
        for cor, (lon, lat, lista) in grupos.items() if lon
    ]

    # Criar as chamadas: linha fina e texto claro sobre o fundo escuro
    if f_texto:
        tracos.append(go.Scattermap(
            lon=ch_lon, lat=ch_lat, mode="lines",
            line=dict(width=CHAMADA_LARGURA, color=CHAMADA_COR), hoverinfo="skip",
        ))
        tracos.append(go.Scattermap(
            lon=f_lon, lat=f_lat, mode="text", text=f_texto,
            textfont=dict(size=tamanho, color=CHAMADA_TEXTO), hoverinfo="skip",
        ))
    return tracos


def _camada_fundo():
    """Criar um retângulo escuro que cobre toda a área do mapa."""
    w, e = LIMITES_MAPA["west"], LIMITES_MAPA["east"]
    s, n = LIMITES_MAPA["south"], LIMITES_MAPA["north"]
    caixa = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]],
        },
    }
    return dict(
        sourcetype="geojson", source=caixa, type="fill",
        color=FUNDO_COR, below="traces",
    )


def criar_mapa(base, geo, nivel, malha_divisa, malha_rotulo):
    """Criar o mapa do Brasil, colorido pelo setor dominante."""
    cfg = NIVEIS[nivel]
    df = _setor_dominante(base)

    # Converter o setor em número (posição na lista de setores)
    posicao = {nome: i for i, nome in enumerate(NOMES_SETORES)}
    z = df["setor_dominante"].map(posicao)

    # Desenhar todos os territórios em um único traço (geo: URL ou dict)
    territorios = go.Choroplethmap(
        geojson=geo,
        locations=df[cfg["id"]],
        featureidkey=f"properties.{cfg['id']}",
        z=z,
        zmin=-0.5,
        zmax=len(NOMES_SETORES) - 0.5,
        colorscale=_escala_discreta(CORES),
        showscale=False,
        text=df[cfg["nome"]],
        customdata=df["setor_dominante"],
        hovertemplate="<b>%{text}</b><br>Setor dominante: %{customdata}<extra></extra>",
        marker=dict(
            opacity=1,
            line=dict(width=LIMITE_LARGURA, color=LIMITE_COR),
        ),
        selected=dict(marker=dict(opacity=1)),
        unselected=dict(marker=dict(opacity=0.55)),
    )

    # Criar as divisas em destaque (linha escura, um pouco mais grossa)
    lon, lat = _linhas_divisa(malha_divisa)
    divisa = go.Scattermap(
        lon=lon, lat=lat, mode="lines",
        line=dict(width=DIVISA_LARGURA, color=DIVISA_COR), hoverinfo="skip",
    )
    camadas = [territorios, divisa]

    # Criar os rótulos do nível (siglas nos estados, nomes nas regiões)
    if malha_rotulo is not None:
        camadas.extend(_criar_rotulos(
            malha_rotulo, base, df, cfg,
            ROTULO_COLUNA[nivel], ROTULO_TAMANHO[nivel], ROTULO_FORA[nivel],
        ))

    # Montar a figura (a ordem define a sobreposição)
    fig = go.Figure(camadas)
    fig.update_layout(
        map=dict(
            style="white-bg",
            center=CENTRO,
            zoom=ZOOM_INICIAL,
            bounds=LIMITES_MAPA,
            layers=[_camada_fundo()],
        ),
        paper_bgcolor=FUNDO_COR,
        height=ALTURA,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        uirevision=nivel,
    )
    return fig


@st.cache_resource(show_spinner="Montando o mapa...")
def mapa_pronto(nivel):
    """Montar o mapa uma vez por nível e reaproveitar nos cliques."""
    # Escolher a fonte da geometria: URL estática ou dict na figura
    geo = garantir_malha(nivel) if USAR_URL else carregar_malha(nivel)

    # Carregar a malha dos rótulos só nos níveis que os têm
    malha_rotulo = carregar_malha(nivel) if nivel in ROTULO_COLUNA else None
    return criar_mapa(
        carregar_base(nivel), geo, nivel,
        carregar_malha(MALHA_DIVISA[nivel]), malha_rotulo,
    )


def mostrar_legenda():
    """Exibir a legenda dos setores abaixo do mapa."""
    itens = "".join(
        '<span style="display:inline-flex;align-items:center;margin-right:18px">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{CORES_SETORES[n]};'
        f'margin-right:6px"></span>{n}</span>'
        for n in NOMES_SETORES
    )
    st.markdown(
        f'<div style="font-size:.9rem">Setor dominante: {itens}</div>',
        unsafe_allow_html=True,
    )

