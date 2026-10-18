"""Carga de dados do app (somente leitura de data/processed)."""
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from shapely.geometry import mapping, shape

# Tornar o pacote src visível ao app
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.base import carregar_municipios  # noqa: E402
from src.config import ANO_REF, PROCESSED  # noqa: E402
from src.indicadores import hhi  # noqa: E402

# Descrever cada nível: colunas, malha, simplificação (graus) e casas decimais
NIVEIS = {
    "Município": {
        "id": "cod", "nome": "nome", "malha": "municipios",
        "simplificar": 0.01, "casas": 3,
    },
    "Estado": {
        "id": "uf_cod", "nome": "uf_nome", "malha": "uf",
        "simplificar": None, "casas": 4,
    },
    "Região": {
        "id": "regiao", "nome": "regiao", "malha": "regioes",
        "simplificar": None, "casas": 4,
    },
}


def _arredondar(coords, casas):
    """Arredondar coordenadas aninhadas (pontos, anéis, polígonos)."""
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], casas), round(coords[1], casas)]
    return [_arredondar(c, casas) for c in coords]


@st.cache_data
def carregar_base(nivel):
    """Carregar a tabela de dados do nível escolhido."""
    if nivel == "Município":
        return carregar_municipios()

    # Ler estados ou regiões e acrescentar o HHI
    if nivel == "Estado":
        df = pd.read_csv(PROCESSED / f"pib_uf_{ANO_REF}.csv", dtype={"uf_cod": str})
    else:
        df = pd.read_csv(PROCESSED / f"pib_regioes_{ANO_REF}.csv")
    return df.assign(hhi=hhi(df))


@st.cache_resource(show_spinner="Preparando a malha...")
def carregar_malha(nivel):
    """Carregar a malha enxuta: só o código, geometria simplificada e arredondada."""
    cfg = NIVEIS[nivel]
    arquivo = PROCESSED / f"malha_{cfg['malha']}_{ANO_REF}.geojson"
    with open(arquivo, encoding="utf-8") as f:
        geo = json.load(f)

    for feature in geo["features"]:
        # Reduzir as propriedades ao código do território
        feature["properties"] = {cfg["id"]: feature["properties"][cfg["id"]]}

        # Simplificar a geometria (preservando a topologia de cada polígono)
        if cfg["simplificar"]:
            geometria = shape(feature["geometry"]).simplify(
                cfg["simplificar"], preserve_topology=True
            )
            feature["geometry"] = mapping(geometria)

        # Arredondar as coordenadas
        feature["geometry"]["coordinates"] = _arredondar(
            feature["geometry"]["coordinates"], cfg["casas"]
        )
    return geo
