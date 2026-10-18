"""Painel de composição do PIB de um território."""
import html

import dados  # noqa: F401  (ajusta o caminho de src)
import streamlit as st

from componentes import CSS_CARD
from src.config import ANO_REF, SETORES
from src.visual import CORES_SETORES, NOMES_SETORES

# Definir a ordem dos setores no cartão e seus nomes
ORDEM_CARD = ["vab_servicos", "vab_adm_publica", "vab_agro", "vab_industria"]
NOME = dict(zip(SETORES, NOMES_SETORES))
PARTES = [f"part_{s}" for s in ORDEM_CARD]

# Definir o estilo interno do cartão de composição
CSS = """
<style>
.card .topo{display:flex;justify-content:space-between;align-items:baseline;margin:6px 0 14px}
.card .rotulo{font-weight:700;letter-spacing:.12em;font-size:.85rem;color:var(--texto-suave)}
.card .fonte{color:var(--texto-fraco);font-size:.8rem;letter-spacing:.08em}
.card .barra{display:flex;height:30px;border-radius:999px;overflow:hidden;margin-bottom:16px}
.card .legenda{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px}
.card .item{display:flex;align-items:center;gap:8px;font-size:.95rem}
.card .ponto{width:10px;height:10px;border-radius:50%;flex:none}
.card .item .nome-setor{color:var(--texto-suave)}
.card .valor{margin-left:auto;font-weight:700}
.card hr{border:none;border-top:1px solid var(--borda);margin:16px 0}
.card .linha{display:flex;justify-content:space-between;align-items:baseline;margin:8px 0}
.card .linha strong{font-size:1.15rem}
.card .aviso{color:var(--aviso);font-size:.95rem;margin:8px 0}
.card .rodape{color:var(--texto-fraco);font-size:.78rem;line-height:1.45}
.card .rodape .sec{font-size:.7rem;margin:12px 0 4px}
.card .rodape li{margin:3px 0}
</style>
"""


def _pct(valor):
    """Formatar percentual com vírgula."""
    return f"{valor:.1f}".replace(".", ",") + "%"


def _reais_mil(valor_mil):
    """Abreviar um valor em mil reais (tri, bi, mi)."""
    reais = valor_mil * 1000
    for limite, sufixo in [(1e12, "tri"), (1e9, "bi"), (1e6, "mi")]:
        if reais >= limite:
            return f"R$ {reais / limite:.1f}".replace(".", ",") + f" {sufixo}"
    return f"R$ {reais:,.0f}".replace(",", ".")


def _reais(valor):
    """Formatar reais com ponto de milhar."""
    return f"R$ {valor:,.0f}".replace(",", ".")


def _html_composicao(linha):
    """Montar a barra e a legenda de composição do VAB."""
    segmentos, itens = "", ""
    for setor in ORDEM_CARD:
        nome = NOME[setor]
        cor = CORES_SETORES[nome]
        valor = linha[f"part_{setor}"]
        segmentos += f'<span style="width:{valor}%;background:{cor}"></span>'
        itens += (
            f'<div class="item"><span class="ponto" style="background:{cor}"></span>'
            f'<span class="nome-setor">{nome}</span><span class="valor">{_pct(valor)}</span></div>'
        )
    return f'<div class="barra">{segmentos}</div><div class="legenda">{itens}</div>'


def _html_cartao(titulo, linha, rodape=None):
    """Montar o HTML do cartão: título, composição, totais e rodapé opcional."""
    # Avisar quando a composição não existe (VAB setorial negativo)
    if linha[PARTES].isna().any():
        miolo = (
            '<div class="aviso">Composição indisponível: '
            "algum setor tem valor adicionado negativo neste território.</div>"
        )
    else:
        miolo = _html_composicao(linha)

    # Adicionar o rodapé (HTML pronto) dentro do cartão
    fim = f'<hr><div class="rodape">{rodape}</div>' if rodape else ""

    return (
        '<div class="card">'
        f'<div class="nome">{html.escape(str(titulo))}</div>'
        '<div class="topo"><span class="rotulo">COMPOSIÇÃO DO PIB</span>'
        f'<span class="fonte">IBGE {ANO_REF}</span></div>'
        f"{miolo}<hr>"
        f'<div class="linha"><span>PIB total</span><strong>{_reais_mil(linha["pib"])}</strong></div>'
        f'<div class="linha"><span>PIB per capita</span><strong>{_reais(linha["pib_per_capita"])}</strong></div>'
        f"{fim}</div>"
    )


def mostrar_painel(titulo, linha, rodape=None):
    """Exibir o cartão de composição (estilo e cartão em um só elemento)."""
    st.markdown(
        CSS_CARD + CSS + _html_cartao(titulo, linha, rodape),
        unsafe_allow_html=True,
    )
