"""Página 1: mapa do Brasil com painel de composição."""
import streamlit as st

from brasil import html_rodape, linha_brasil
from componentes import mostrar_tese
from dados import NIVEIS, carregar_base
from mapa import mapa_pronto
from painel import mostrar_painel

# Escolher o nível territorial
nivel = st.sidebar.radio("Nível", list(NIVEIS))
cfg = NIVEIS[nivel]
chave_busca = f"busca_{nivel}"


def limpar_busca():
    """Limpar a busca ao clicar no mapa (o clique mais recente vence)."""
    st.session_state[chave_busca] = None


# Preparar dados e mapa
base = carregar_base(nivel)
fig = mapa_pronto(nivel)

# Buscar território pelo nome (substitui o clique anterior)
nome_busca = st.sidebar.selectbox(
    "Buscar território", sorted(base[cfg["nome"]]), index=None,
    placeholder="Digite um nome", key=chave_busca,
)

# Dividir a página em três colunas
col_tese, col_mapa, col_painel = st.columns([1, 2.4, 1.3])

# Coluna 2: exibir o mapa e capturar o clique
with col_mapa:
    evento = st.plotly_chart(
        fig,
        width="stretch",
        on_select=limpar_busca,
        selection_mode="points",
        key=f"mapa_{nivel}",
    )

# Identificar o território escolhido
pontos = evento.selection.points if evento else []
if nome_busca:
    id_sel = base.loc[base[cfg["nome"]] == nome_busca, cfg["id"]].iloc[0]
elif pontos:
    id_sel = pontos[0].get("location")
else:
    id_sel = None

# Coluna 1: exibir a tese
with col_tese:
    mostrar_tese()

# Coluna 3: exibir o Brasil (sem seleção) ou o território escolhido
with col_painel:
    if id_sel is None:
        mostrar_painel("Brasil", linha_brasil(), rodape=html_rodape())
    else:
        linha = base[base[cfg["id"]] == id_sel].iloc[0]
        mostrar_painel(linha[cfg["nome"]], linha)