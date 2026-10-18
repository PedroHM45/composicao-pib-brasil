"""Leitura das bases finais para análise."""
import pandas as pd

from src.config import ANO_REF, arquivo_final
from src.indicadores import classificar_quadrante, hhi

# Definir grupos de recortes (None = Brasil inteiro)
GRUPOS = {
    "MATOPIBA": "matopiba",
    "Semiárido": "semiarido",
    "Metrópoles": "em_metropole",
    "Fora dos recortes": "fora",
    "Brasil": None,
}

# Listar as colunas lógicas de recortes
COLUNAS_RECORTES = ["matopiba", "semiarido", "em_metropole", "fora"]


def carregar_municipios(ano=ANO_REF):
    """Ler a base municipal com recortes, perfis, HHI e quadrantes."""
    # Ler bases finais
    mun = pd.read_csv(
        arquivo_final("pib_municipios", "csv", ano), dtype={"cod": str, "uf_cod": str}
    )
    rec = pd.read_csv(arquivo_final("recortes", "csv", ano), dtype={"cod": str})
    perfis = pd.read_csv(
        arquivo_final("perfis", "csv", ano), dtype={"cod": str, "grupo": "Int64"}
    )

    # Unir recortes e perfis à base de municípios
    mun = mun.merge(rec, on="cod", how="left", validate="one_to_one")
    mun = mun.merge(perfis, on="cod", how="left", validate="one_to_one")

    # Conferir que todos os municípios têm recortes e perfil
    if mun[COLUNAS_RECORTES].isna().any().any():
        raise ValueError("Há municípios sem informação de recortes")
    if mun.loc[~mun["vab_negativo"], "perfil"].isna().any():
        raise ValueError("Há municípios sem perfil")

    # Calcular HHI e quadrantes
    mun["hhi"] = hhi(mun)
    mun["quadrante"] = classificar_quadrante(mun)

    return mun