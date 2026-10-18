"""Página 2: concentração da riqueza (ato 1)."""
import streamlit as st

from calculos import n_para_participacao
from componentes import br, mostrar_cartao
from dados import carregar_base
from graficos import fig_bolhas, fig_lorenz
from graficos_regioes import fig_regioes
from ranking import mostrar_ranking
from src.indicadores import gini

# Definir o estilo dos números em destaque
CSS_LEITURA = """
<style>
.card .num{font-size:2.2rem;font-weight:700;color:var(--ouro);line-height:1.1;margin-top:18px}
.card .rot{color:var(--texto-suave);font-size:.95rem;margin-top:2px}
.card .peq{color:var(--texto-fraco);font-size:.82rem;margin-top:2px}
</style>
"""

# Escolher o gráfico e o nível do ranking (seletores na sidebar)
grafico = st.sidebar.radio("Gráfico", ["Curva de Lorenz", "Mapa de bolhas", "Regiões"])
rotulo = st.sidebar.radio("Ranking", ["Municípios", "Estados"])
nivel_ranking = {"Municípios": "Município", "Estados": "Estado"}[rotulo]

# Preparar a base municipal e os indicadores de concentração
base = carregar_base("Município")
n = len(base)
n50 = n_para_participacao(base["pib"], 0.5)
n25 = n_para_participacao(base["pib"], 0.25)
g_pib = gini(base["pib"].to_numpy())
g_pop = gini(base["populacao"].to_numpy())
g_pc = gini(base["pib_per_capita"].dropna().to_numpy())

# Contar os maiores municípios por região
regioes = base.nlargest(n50, "pib")["regiao"].value_counts()
por_regiao = " · ".join(f"{r} {q}" for r, q in regioes.items())

# Dividir a página em três colunas
col_leitura, col_grafico, col_ranking = st.columns([1, 2.4, 1.3])

# Coluna 2: exibir o gráfico escolhido
with col_grafico:
    if grafico == "Curva de Lorenz":
        st.plotly_chart(fig_lorenz(base), width="stretch", key="lorenz")
    elif grafico == "Mapa de bolhas":
        st.plotly_chart(fig_bolhas(base), width="stretch", key="bolhas")
    else:
        st.plotly_chart(fig_regioes(base), width="stretch", key="regioes")

# Coluna 1: exibir a pergunta, os números e a leitura
with col_leitura:
    corpo = (
        '<div class="texto">Quão concentrada é a riqueza no território?</div>'
        f'<div class="num">{br(n50 / n * 100, 1)}%</div>'
        f'<div class="rot">dos municípios ({n50}) somam metade do PIB</div>'
        f'<div class="num">{n25}</div>'
        '<div class="rot">municípios somam um quarto do PIB</div>'
        f'<div class="num">{br(g_pib, 2)}</div>'
        '<div class="rot">Gini do PIB entre os municípios</div>'
        f'<div class="peq">População: {br(g_pop, 2)} · PIB per capita: {br(g_pc, 2)}</div>'
        '<div class="sec">LEITURA</div>'
        '<div class="rot">Parte da concentração é de gente: a população também é '
        f"concentrada (Gini {br(g_pop, 2)}). Por habitante, a desigualdade "
        f"cai ({br(g_pc, 2)}), mas não desaparece.</div>"
        f'<div class="peq" style="margin-top:12px">Os {n50} maiores, por região: '
        f"{por_regiao}</div>"
    )
    mostrar_cartao("Concentração", corpo, CSS_LEITURA)

# Coluna 3: exibir o ranking
with col_ranking:
    mostrar_ranking(nivel_ranking)
