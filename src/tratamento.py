"""Funções de integração e tratamento dos dados."""
from src.config import SETORES, SOMAVEIS
from src.indicadores import participacoes
from src.territorio import adicionar_territorio


def calcular_indicadores(df):
    """Calcular PIB per capita e participações setoriais."""
    # Copiar para não alterar o argumento
    out = df.copy()

    # Calcular PIB per capita (mil reais para reais)
    out["pib_per_capita"] = out["pib"] * 1000 / out["populacao"]

    # Marcar territórios com algum setor de VAB negativo
    out["vab_negativo"] = (out[SETORES] < 0).any(axis=1)

    # Calcular participação de cada setor (%), vazia onde há VAB negativo
    part = participacoes(out) * 100
    for s in SETORES:
        out[f"part_{s}"] = part[s]

    return out


def integrar(pib, pop):
    """Unir PIB e população e calcular indicadores."""
    # Unir pelo código, mantendo só municípios com PIB
    df = pib.merge(pop, on="cod", how="left", validate="one_to_one")

    # Adicionar UF, sigla e região
    df = adicionar_territorio(df)

    # Calcular indicadores
    return calcular_indicadores(df)


def agregar(df, por):
    """Agregar municípios por coluna(s) e recalcular indicadores."""
    # Somar valores absolutos por grupo
    ag = df.groupby(por, as_index=False)[SOMAVEIS].sum()

    # Recalcular indicadores sobre os totais
    return calcular_indicadores(ag)