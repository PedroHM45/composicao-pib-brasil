"""Página 4: estrutura produtiva (ato 3)."""
import streamlit as st

from componentes import br, mostrar_cartao
from graficos_estrutura import (
    NOMES, SETORES, fig_ql, fig_valor_territorio, mapa_setor, resumo_setores,
)
from ranking_estrutura import mostrar_ranking_estrutura

# Definir o estilo dos números em destaque (compacto para caber no card)
CSS_LEITURA = """
<style>
.card .num{font-size:1.9rem;font-weight:700;color:var(--ouro);line-height:1.1;margin-top:10px}
.card .rot{color:var(--texto-suave);font-size:.92rem;margin-top:2px;line-height:1.35}
.card .peq{color:var(--texto-fraco);font-size:.8rem;margin-top:2px;line-height:1.4}
</style>
"""

# Definir as opções do seletor de gráfico
OPCOES = ["Valor × território", "Mapa do setor", "Especialização por estado"]

# Escolher gráfico, setor e nível do ranking (sidebar)
grafico = st.sidebar.radio("Gráfico", OPCOES)
setor = st.sidebar.radio("Setor", SETORES, format_func=NOMES.get)
rotulo = st.sidebar.radio("Ranking", ["Municípios", "Estados"])
nivel_ranking = {"Municípios": "Município", "Estados": "Estado"}[rotulo]

# Calcular os números da leitura
nacional, mediana, dominante = resumo_setores()
terciario = nacional["vab_servicos"] + nacional["vab_adm_publica"]

# Dividir a página em três colunas
col_leitura, col_grafico, col_ranking = st.columns([1, 2.4, 1.3])

# Coluna 2: exibir o gráfico escolhido
with col_grafico:
    if grafico == OPCOES[0]:
        st.plotly_chart(fig_valor_territorio(), width="stretch", key="valor_territorio")
    elif grafico == OPCOES[1]:
        st.plotly_chart(mapa_setor(setor), width="stretch", key=f"mapa_setor_{setor}")
    else:
        st.plotly_chart(fig_ql(setor), width="stretch", key=f"ql_{setor}")

# Coluna 1: exibir a pergunta, os números e a leitura
with col_leitura:
    corpo = (
        '<div class="texto">Como se distribuem serviços, indústria e agro?</div>'
        f'<div class="num">{br(nacional["vab_servicos"], 1)}%</div>'
        '<div class="rot">da economia do país é de serviços</div>'
        f'<div class="peq">{br(terciario, 1)}% somando a adm. pública</div>'
        f'<div class="num">{br(dominante["vab_agro"], 1)}%</div>'
        '<div class="rot">dos municípios têm o agro como maior setor</div>'
        f'<div class="peq">mas é só {br(nacional["vab_agro"], 1)}% da economia do país</div>'
        f'<div class="num">{br(dominante["vab_industria"], 1)}%</div>'
        '<div class="rot">dos municípios têm a indústria como maior setor</div>'
        f'<div class="peq">mas gera {br(nacional["vab_industria"], 1)}% da economia</div>'
        '<div class="sec">LEITURA</div>'
        '<div class="peq">O valor está nos serviços e na indústria concentrada; '
        "o território é agrícola e público.</div>"
        '<div class="peq" style="margin-top:6px">Indústria inclui mineração, '
        "petróleo, construção e utilidades.</div>"
    )
    mostrar_cartao("Estrutura", corpo, CSS_LEITURA)

# Coluna 3: exibir o ranking do setor escolhido
with col_ranking:
    mostrar_ranking_estrutura(nivel_ranking, setor)
