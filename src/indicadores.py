"""Indicadores de concentração, diversificação e especialização."""
import numpy as np
import pandas as pd

from src.config import (
    QUADRANTE_CONC_ALTA,
    QUADRANTE_CONC_BAIXA,
    QUADRANTE_DIV_ALTA,
    QUADRANTE_DIV_BAIXA,
    SETORES,
)


def gini(x):
    """Calcular o índice de Gini."""
    # Ordenar valores em ordem crescente
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)

    # Gerar posições de 1 a n
    pos = np.arange(1, n + 1)

    # Aplicar a fórmula do Gini
    return (2 * (pos * x).sum()) / (n * x.sum()) - (n + 1) / n


def participacoes(df):
    """Calcular a participação de cada setor (fração do total dos setores)."""
    # Dividir cada setor pela soma dos setores
    part = df[SETORES].div(df[SETORES].sum(axis=1), axis=0)

    # Anular territórios com algum setor negativo
    negativo = (df[SETORES] < 0).any(axis=1)
    part.loc[negativo] = np.nan

    return part


def hhi(df, normalizar=True):
    """Calcular o índice de Herfindahl-Hirschman dos setores."""
    # Somar os quadrados das participações
    h = (participacoes(df) ** 2).sum(axis=1, skipna=False)

    # Normalizar para a escala de 0 a 1
    if normalizar:
        n = len(SETORES)
        h = (h - 1 / n) / (1 - 1 / n)

    return h


def composicao_nacional(df):
    """Calcular a participação de cada setor no total do país."""
    total = df[SETORES].sum()
    return total / total.sum()


def quociente_locacional(df, referencia):
    """Calcular o quociente locacional de cada setor."""
    # Dividir a participação local pela participação de referência
    return participacoes(df).div(referencia, axis=1)


def limites_quadrante(df):
    """Calcular os limites dos quadrantes (medianas de HHI e PIB per capita)."""
    return df["hhi"].median(), df["pib_per_capita"].median()


def classificar_quadrante(df):
    """Classificar municípios por concentração setorial e renda."""
    # Calcular os limites
    lim_hhi, lim_renda = limites_quadrante(df)

    # Comparar cada município com os limites
    conc = df["hhi"] > lim_hhi
    rico = df["pib_per_capita"] > lim_renda

    # Escolher o rótulo de cada combinação
    rotulos = np.select(
        [conc & ~rico, conc & rico, ~conc & ~rico, ~conc & rico],
        [
            QUADRANTE_CONC_BAIXA,
            QUADRANTE_CONC_ALTA,
            QUADRANTE_DIV_BAIXA,
            QUADRANTE_DIV_ALTA,
        ],
        default="",
    )

    # Deixar vazio o município sem HHI ou sem renda
    valido = df["hhi"].notna() & df["pib_per_capita"].notna()
    return pd.Series(rotulos, index=df.index).where(valido)