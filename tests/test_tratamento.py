"""Testes de tratamento, agregação e território."""
import numpy as np
import pandas as pd
import pytest

from src.config import SETORES
from src.territorio import adicionar_territorio
from src.tratamento import agregar, calcular_indicadores


def municipios():
    """Montar dois municípios do mesmo estado."""
    return pd.DataFrame(
        {
            "cod": ["3550308", "3509502"],
            "uf_cod": ["35", "35"],
            "pib": [1000.0, 100.0],
            "vab_total": [900.0, 90.0],
            "impostos": [100.0, 10.0],
            "populacao": [500.0, 100.0],
            "vab_agro": [0.0, 80.0],
            "vab_industria": [300.0, 5.0],
            "vab_servicos": [500.0, 3.0],
            "vab_adm_publica": [100.0, 2.0],
        }
    )


def test_pib_per_capita_converte_mil_reais():
    # PIB em mil reais: 1000 mil / 500 hab = R$ 2.000 por pessoa
    out = calcular_indicadores(municipios())
    assert out["pib_per_capita"].iloc[0] == pytest.approx(2000)


def test_participacoes_somam_cem():
    out = calcular_indicadores(municipios())
    cols = [f"part_{s}" for s in SETORES]
    assert np.allclose(out[cols].sum(axis=1), 100)


def test_vab_negativo_anula_participacoes():
    df = municipios()
    df.loc[0, "vab_industria"] = -50.0
    out = calcular_indicadores(df)
    cols = [f"part_{s}" for s in SETORES]
    assert out.loc[0, "vab_negativo"]
    assert out.loc[0, cols].isna().all()
    assert out.loc[1, cols].notna().all()


def test_agregar_recalcula_sobre_os_totais():
    # Agro agregado = 80 / 990 = 8,08%; a média das participações daria 44,4%
    ag = agregar(calcular_indicadores(municipios()), "uf_cod")
    soma_vab = 900 + 90
    assert ag.loc[0, "part_vab_agro"] == pytest.approx(80 / soma_vab * 100)
    media_simples = calcular_indicadores(municipios())["part_vab_agro"].mean()
    assert ag.loc[0, "part_vab_agro"] != pytest.approx(media_simples)


def test_agregar_preserva_o_pib_total():
    df = calcular_indicadores(municipios())
    assert agregar(df, "uf_cod")["pib"].sum() == pytest.approx(df["pib"].sum())


def test_territorio_deriva_uf_e_regiao():
    out = adicionar_territorio(pd.DataFrame({"cod": ["3550308", "1100015"]}))
    assert out["uf_sigla"].tolist() == ["SP", "RO"]
    assert out["regiao"].tolist() == ["Sudeste", "Norte"]


def test_territorio_recusa_uf_desconhecida():
    with pytest.raises(ValueError):
        adicionar_territorio(pd.DataFrame({"cod": ["9900000"]}))
