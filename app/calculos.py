"""Cálculos de concentração (funções puras, sem Streamlit)."""
import numpy as np


def curva_lorenz(valores):
    """Calcular a curva de Lorenz em % (territórios x total acumulado)."""
    v = np.sort(np.asarray(valores, dtype=float))
    acum = np.concatenate([[0.0], np.cumsum(v) / v.sum()])
    x = np.linspace(0, 1, len(acum))
    return x * 100, acum * 100


def n_para_participacao(valores, alvo):
    """Contar quantos maiores territórios somam a participação-alvo (0 a 1)."""
    v = np.sort(np.asarray(valores, dtype=float))[::-1]
    acum = np.cumsum(v) / v.sum()
    return int(np.searchsorted(acum, alvo) + 1)
