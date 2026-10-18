"""Agrupamento de municípios pelo perfil econômico."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import (
    K_PERFIS,
    PERFIL_AGRO,
    PERFIL_INDUSTRIAL,
    PERFIL_PUBLICO,
    PERFIL_URBANO,
    SETORES,
)
from src.indicadores import participacoes

# Definir participação mínima (evita o logaritmo de zero)
MINIMO = 0.001


def clr(df):
    """Transformar participações setoriais com CLR (log-razão centrada)."""
    # Calcular participações e impor um mínimo
    p = participacoes(df).clip(lower=MINIMO)

    # Renormalizar para somar 1
    p = p.div(p.sum(axis=1), axis=0)

    # Subtrair de cada logaritmo a média da linha
    logp = np.log(p)
    return logp.sub(logp.mean(axis=1), axis=0)


def agrupar(df, k=K_PERFIS, semente=42):
    """Agrupar municípios por K-means e devolver o rótulo de cada um."""
    # Excluir municípios sem participações válidas
    valido = df.loc[~df["vab_negativo"]]

    # Padronizar a matriz CLR
    X = StandardScaler().fit_transform(clr(valido))

    # Ajustar K-means
    km = KMeans(n_clusters=k, n_init=10, random_state=semente).fit(X)

    # Devolver rótulos alinhados ao índice original
    return pd.Series(km.labels_, index=valido.index, name="grupo")


def nomear_grupos(df, coluna="grupo"):
    """Nomear os grupos pelo setor de maior peso relativo."""
    # Calcular a composição ponderada de cada grupo
    soma = df.groupby(coluna)[SETORES].sum()
    comp = soma.div(soma.sum(axis=1), axis=0)

    # Definir as regras, do perfil mais extremo ao menos extremo
    regras = [
        ("vab_agro", PERFIL_AGRO),
        ("vab_adm_publica", PERFIL_PUBLICO),
        ("vab_industria", PERFIL_INDUSTRIAL),
    ]

    # Recusar quantidade de grupos incompatível com as regras
    if len(comp) != len(regras) + 1:
        raise ValueError(
            f"A regra de nomes vale para {len(regras) + 1} grupos, e há {len(comp)}"
        )

    # Atribuir os nomes na ordem das regras
    nomes = {}
    restantes = list(comp.index)
    for setor, nome in regras:
        g = comp.loc[restantes, setor].idxmax()
        nomes[g] = nome
        restantes.remove(g)

    # Nomear o grupo que sobrou
    nomes[restantes[0]] = PERFIL_URBANO
    return nomes