"""Testes dos cálculos de concentração do app."""
import numpy as np
import pytest

from app.calculos import curva_lorenz, n_para_participacao


def test_lorenz_igualdade_coincide_com_diagonal():
    x, y = curva_lorenz([1, 1, 1, 1])
    assert np.allclose(x, y)


def test_lorenz_concentracao_maxima_fica_em_zero_ate_o_fim():
    x, y = curva_lorenz([0, 0, 0, 10])
    assert np.allclose(y[:-1], 0)
    assert y[-1] == pytest.approx(100)


def test_lorenz_comeca_em_zero_e_termina_em_cem():
    x, y = curva_lorenz([5, 1, 3])
    assert (x[0], y[0]) == (0, 0)
    assert x[-1] == pytest.approx(100)
    assert y[-1] == pytest.approx(100)
    assert len(x) == len(y) == 4


def test_lorenz_ignora_ordem_da_entrada():
    a = curva_lorenz([5, 1, 3])
    b = curva_lorenz([1, 3, 5])
    assert np.allclose(a[0], b[0])
    assert np.allclose(a[1], b[1])


def test_n_para_participacao_conta_os_maiores():
    valores = [50, 30, 20]
    assert n_para_participacao(valores, 0.5) == 1
    assert n_para_participacao(valores, 0.51) == 2
    assert n_para_participacao(valores, 0.8) == 2
    assert n_para_participacao(valores, 1.0) == 3


def test_n_para_participacao_ignora_ordem_da_entrada():
    assert n_para_participacao([20, 50, 30], 0.8) == 2