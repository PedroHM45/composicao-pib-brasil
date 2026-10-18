"""Página 3: dependência da administração pública (ato 2)."""
import streamlit as st

from componentes import br, mostrar_cartao
from dados import carregar_base
from graficos_dependencia import fig_dispersao, fig_regiao_porte, mapa_dependencia
from ranking_dependencia import mostrar_ranking_dependencia

COL = "part_vab_adm_publica"

# Definir o estilo dos números em destaque
CSS_LEITURA = """
<style>
.card .num{font-size:2.2rem;font-weight:700;color:var(--ouro);line-height:1.1;margin-top:14px}
.card .rot{color:var(--texto-suave);font-size:.95rem;margin-top:2px}
.card .peq{color:var(--texto-fraco);font-size:.82rem;margin-top:2px;line-height:1.45}
</style>
"""

# Escolher o gráfico da coluna 2 e o nível do ranking (sidebar)
grafico = st.sidebar.radio("Gráfico", ["Mapa", "Região × porte", "Dependência × renda"])
rotulo = st.sidebar.radio("Ranking", ["Municípios", "Estados"])
nivel_ranking = {"Municípios": "Município", "Estados": "Estado"}[rotulo]

# Preparar a base e identificar o setor de maior peso de cada município
base = carregar_base("Município")
partes = [c for c in base.columns if c.startswith("part_")]
valido = base[partes].notna().all(axis=1)
dominante = base.loc[valido, partes].idxmax(axis=1)
n_dom = int((dominante == COL).sum())
p_dom = n_dom / valido.sum() * 100

# Identificar o perfil dependente: o de maior peso médio da adm. pública
perfil_dep = base.groupby("perfil")[COL].mean().idxmax()
dep = base[base["perfil"] == perfil_dep]
n_dep = len(dep)
p_pop = dep["populacao"].sum() / base["populacao"].sum() * 100
p_pib = dep["pib"].sum() / base["pib"].sum() * 100
mediana = base["pib_per_capita"].median()
p_abaixo = (dep["pib_per_capita"] < mediana).mean() * 100

# Calcular o peso mediano da adm. pública por região
medianas = base.groupby("regiao")[COL].median().sort_values(ascending=False)
por_regiao = " · ".join(f"{r} {br(v, 1)}%" for r, v in medianas.items())

# Calcular a correlação entre o peso da adm. pública e a renda
valida = base[base[COL].notna() & (base["pib_per_capita"] > 0)]
rho = valida[COL].corr(valida["pib_per_capita"], method="spearman")

# Dividir a página em três colunas
col_leitura, col_grafico, col_ranking = st.columns([1, 2.4, 1.3])

# Coluna 2: exibir o gráfico escolhido
with col_grafico:
    if grafico == "Mapa":
        st.plotly_chart(mapa_dependencia(), width="stretch", key="mapa_dependencia")
    elif grafico == "Região × porte":
        st.plotly_chart(fig_regiao_porte(), width="stretch", key="barras_regiao_porte")
    else:
        st.plotly_chart(fig_dispersao(), width="stretch", key="dispersao_dependencia")

# Coluna 1: exibir a pergunta, os números e a leitura
with col_leitura:
    corpo = (
        '<div class="texto">Quem depende da administração pública?</div>'
        f'<div class="num">{br(p_dom, 1)}%</div>'
        f'<div class="rot">dos municípios ({br(n_dom, 0)}) têm a adm. pública como maior setor</div>'
        f'<div class="num">{br(n_dep, 0)}</div>'
        f'<div class="rot">municípios no perfil “{perfil_dep}”</div>'
        f'<div class="peq">{br(p_pop, 1)}% da população · {br(p_pib, 1)}% do PIB</div>'
        f'<div class="num">{br(p_abaixo, 0)}%</div>'
        '<div class="rot">deles têm PIB per capita abaixo da mediana do país</div>'
        '<div class="sec">LEITURA</div>'
        f'<div class="peq">Peso mediano por região: {por_regiao}.</div>'
        '<div class="peq" style="margin-top:8px">Onde falta atividade privada, a adm. '
        f"pública ocupa o espaço (Spearman {br(rho, 2)} com a renda). Associação, não "
        "causa. Inclui educação, saúde e seguridade públicas.</div>"
    )
    mostrar_cartao("Dependência", corpo, CSS_LEITURA)

# Coluna 3: exibir o ranking
with col_ranking:
    mostrar_ranking_dependencia(nivel_ranking)
