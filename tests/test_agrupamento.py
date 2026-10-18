"""Testes do agrupamento por perfil econômico."""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import adjusted_rand_score

from src.agrupamento import agrupar, clr, nomear_grupos
from src.config import (
    PERFIL_AGRO,
    PERFIL_INDUSTRIAL,
    PERFIL_PUBLICO,
    PERFIL_URBANO,
    SETORES,
)

# Definir 4 perfis nítidos (agro, indústria, serviços, adm. pública)
CENTROS = np.array(
    [
        [0.70, 0.10, 0.10, 0.10],
        [0.10, 0.70, 0.10, 0.10],
        [0.10, 0.10, 0.70, 0.10],
        [0.10, 0.10, 0.10, 0.70],
    ]
)


def base_sintetica(por_grupo=40, semente=0):
    """Gerar municípios sintéticos com 4 perfis conhecidos."""
    rng = np.random.default_rng(semente)
    linhas, verdade = [], []
    for g, centro in enumerate(CENTROS):
        # Sortear composições próximas ao centro do perfil
        amostra = rng.dirichlet(centro * 60, size=por_grupo) * 1000
        linhas.append(amostra)
        verdade += [g] * por_grupo
    df = pd.DataFrame(np.vstack(linhas), columns=SETORES)
    df["vab_negativo"] = False
    return df, np.array(verdade)


def test_clr_linhas_somam_zero():
    df, _ = base_sintetica()
    assert np.allclose(clr(df).sum(axis=1), 0)


def test_clr_aceita_setor_zerado():
    # O piso evita logaritmo de zero
    df, _ = base_sintetica()
    df.loc[0, "vab_agro"] = 0.0
    assert np.isfinite(clr(df).to_numpy()).all()


def test_agrupar_recupera_os_perfis():
    df, verdade = base_sintetica()
    rotulos = agrupar(df, k=4)
    assert adjusted_rand_score(verdade, rotulos) > 0.95


def test_agrupar_e_reprodutivel():
    df, _ = base_sintetica()
    assert agrupar(df, k=4).equals(agrupar(df, k=4))


def test_agrupar_exclui_vab_negativo():
    # Município com VAB negativo fica fora dos rótulos
    df, _ = base_sintetica()
    df.loc[3, "vab_negativo"] = True
    rotulos = agrupar(df, k=4)
    assert 3 not in rotulos.index
    assert len(rotulos) == len(df) - 1


def test_nomear_grupos_pelo_setor_dominante():
    df, verdade = base_sintetica()
    df["grupo"] = verdade
    nomes = nomear_grupos(df)
    assert nomes[0] == PERFIL_AGRO
    assert nomes[1] == PERFIL_INDUSTRIAL
    assert nomes[2] == PERFIL_URBANO
    assert nomes[3] == PERFIL_PUBLICO


def test_nomear_grupos_recusa_numero_errado():
    df, verdade = base_sintetica()
    df["grupo"] = np.where(verdade == 3, 2, verdade)  # só 3 grupos
    with pytest.raises(ValueError):
        nomear_grupos(df)
