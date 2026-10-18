"""Testes dos indicadores de concentração e especialização."""
import numpy as np
import pandas as pd
import pytest

from src.config import (
    QUADRANTE_CONC_ALTA,
    QUADRANTE_CONC_BAIXA,
    QUADRANTE_DIV_ALTA,
    QUADRANTE_DIV_BAIXA,
    SETORES,
)
from src.indicadores import (
    classificar_quadrante,
    composicao_nacional,
    gini,
    hhi,
    participacoes,
    quociente_locacional,
)


def setores(*linhas):
    """Montar DataFrame com os 4 setores a partir de listas."""
    return pd.DataFrame(list(linhas), columns=SETORES, dtype=float)


# --- Gini -------------------------------------------------------------
def test_gini_igualdade_perfeita():
    # Valores iguais não geram desigualdade
    assert gini([5, 5, 5, 5]) == pytest.approx(0)


def test_gini_concentracao_maxima():
    # Um só território com tudo: Gini = (n - 1) / n
    assert gini([0] * 9 + [10]) == pytest.approx(0.9)


def test_gini_ignora_ordem():
    # A ordem de entrada não altera o resultado
    assert gini([1, 2, 3, 10]) == pytest.approx(gini([10, 3, 1, 2]))


# --- Participações ----------------------------------------------------
def test_participacoes_somam_um():
    df = setores([10, 20, 30, 40], [1, 1, 1, 1])
    assert np.allclose(participacoes(df).sum(axis=1), 1)


def test_participacoes_anula_setor_negativo():
    # Setor negativo invalida a linha inteira
    df = setores([10, 20, 30, 40], [10, -5, 30, 40])
    part = participacoes(df)
    assert part.iloc[0].notna().all()
    assert part.iloc[1].isna().all()


# --- HHI --------------------------------------------------------------
def test_hhi_um_setor_vale_um():
    assert hhi(setores([100, 0, 0, 0])).iloc[0] == pytest.approx(1)


def test_hhi_setores_iguais_vale_zero():
    assert hhi(setores([25, 25, 25, 25])).iloc[0] == pytest.approx(0)


def test_hhi_sem_normalizar_tem_piso():
    # Sem normalizar, o piso é 1 / n = 0,25
    assert hhi(setores([25, 25, 25, 25]), normalizar=False).iloc[0] == pytest.approx(0.25)


def test_hhi_negativo_fica_vazio():
    # Território com setor negativo não recebe HHI
    assert np.isnan(hhi(setores([10, -5, 30, 40])).iloc[0])


def test_hhi_fica_entre_zero_e_um():
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.random((200, 4)), columns=SETORES)
    h = hhi(df)
    assert h.min() >= 0 and h.max() <= 1


# --- Composição e QL --------------------------------------------------
def test_composicao_nacional_soma_um():
    df = setores([10, 20, 30, 40], [5, 5, 5, 5])
    assert composicao_nacional(df).sum() == pytest.approx(1)


def test_ql_do_proprio_pais_vale_um():
    # Território idêntico ao país tem QL = 1 em todos os setores
    df = setores([10, 20, 30, 40], [30, 20, 10, 0])
    ref = composicao_nacional(df)
    pais = df.sum().to_frame().T
    assert np.allclose(quociente_locacional(pais, ref).iloc[0], 1)


def test_ql_maximo_e_o_inverso_da_participacao_nacional():
    # Território 100% agro: QL agro = 1 / participação nacional do agro
    df = setores([100, 0, 0, 0], [0, 100, 100, 100])
    ref = composicao_nacional(df)
    ql = quociente_locacional(df, ref)
    assert ql.loc[0, "vab_agro"] == pytest.approx(1 / ref["vab_agro"])


# --- Quadrantes -------------------------------------------------------
def test_quadrantes_cobrem_as_quatro_combinacoes():
    df = pd.DataFrame(
        {
            "hhi": [0.1, 0.1, 0.9, 0.9],
            "pib_per_capita": [10, 100, 10, 100],
        }
    )
    q = classificar_quadrante(df)
    assert q.tolist() == [
        QUADRANTE_DIV_BAIXA,
        QUADRANTE_DIV_ALTA,
        QUADRANTE_CONC_BAIXA,
        QUADRANTE_CONC_ALTA,
    ]


def test_quadrante_vazio_sem_hhi():
    df = pd.DataFrame({"hhi": [0.1, np.nan, 0.9], "pib_per_capita": [10, 50, 100]})
    q = classificar_quadrante(df)
    assert q.isna().tolist() == [False, True, False]
