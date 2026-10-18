"""Agregação nacional e rodapé de transparência do cartão do Brasil."""
import pandas as pd
import streamlit as st

from dados import carregar_base
from src.config import SETORES

# Definir o nome da coluna de população (ajustar se for diferente)
COL_POP = "populacao"

# Definir as fontes e os avisos principais
FONTES = [
    "IBGE · PIB dos Municípios 2021 (SIDRA, tabela 5938)",
    "IBGE · Estimativas de população (SIDRA, tabela 6579)",
    "IBGE · Malhas territoriais 2021",
]
AVISOS = [
    "Retrato de 2021: não mostra tendência.",
    "Indústria inclui mineração, petróleo, construção e utilidades; "
    "adm. pública é separada de serviços.",
    "Os dados mostram associações, não causas.",
    "Sem composição setorial: Cachoeira Dourada (GO), pelo valor adicionado negativo. "
    "Boa Esperança do Norte (MT) não tem PIB em 2021.",
]


@st.cache_data
def linha_brasil():
    """Somar os municípios e montar a linha do Brasil (mesmos campos do cartão)."""
    base = carregar_base("Município")

    # Calcular a participação de cada setor sobre o VAB somado
    vab = base[list(SETORES)].sum()
    partes = vab / vab.sum() * 100

    # Somar PIB e população e calcular o PIB per capita (PIB em mil reais)
    pib = base["pib"].sum()
    pop = base[COL_POP].sum()

    dados = {f"part_{s}": partes[s] for s in SETORES}
    dados.update(pib=pib, populacao=pop, pib_per_capita=pib * 1000 / pop)
    return pd.Series(dados)


def texto_escala():
    """Devolver o texto da escala dos dados: territórios e população."""
    brasil = linha_brasil()
    n_mun = f"{len(carregar_base('Município')):,}".replace(",", ".")
    n_uf = len(carregar_base("Estado"))
    n_reg = len(carregar_base("Região"))
    pop = f"{brasil['populacao'] / 1e6:.1f}".replace(".", ",")
    return (
        f"{n_mun} municípios · {n_uf} estados · {n_reg} regiões · "
        f"{pop} mi de habitantes"
    )


def html_rodape():
    """Montar o HTML do rodapé: escala, fontes e avisos."""
    fontes = "".join(f"<li>{f}</li>" for f in FONTES)
    avisos = "".join(f"<li>{a}</li>" for a in AVISOS)
    return (
        f"<div>{texto_escala()}</div>"
        '<div class="sec">FONTES</div>'
        f"<ul>{fontes}</ul>"
        '<div class="sec">AVISOS</div>'
        f"<ul>{avisos}</ul>"
    )
