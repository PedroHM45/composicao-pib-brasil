"""Cartão de ranking dos maiores PIBs."""
import html

from componentes import br, mostrar_cartao
from dados import NIVEIS, carregar_base

# Definir o estilo da tabela do ranking
CSS_RANK = """
<style>
.card .rk{margin-top:12px;font-size:.85rem}
.card .rk .cab,.card .rk .lin{display:grid;
grid-template-columns:22px 1fr 50px 54px 50px;gap:6px;align-items:center}
.card .rk .cab{color:var(--texto-fraco);font-size:.68rem;letter-spacing:.08em;margin-bottom:6px}
.card .rk .lin{padding:7px 0;border-top:1px solid var(--borda)}
.card .rk .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .rk .v{text-align:right}
.card .rk .pos{color:var(--texto-fraco)}
.card .rk .dest{font-weight:700;color:var(--ouro)}
.card .rk .nota{color:var(--texto-fraco);font-size:.8rem;line-height:1.45;margin-top:14px}
</style>
"""

ROTULOS = {"Município": "municípios", "Estado": "estados"}


def _pct(valor):
    """Formatar percentual no padrão brasileiro."""
    return br(valor, 1) + "%"


def mostrar_ranking(nivel, n=10):
    """Exibir o ranking dos maiores PIBs do nível escolhido."""
    cfg = NIVEIS[nivel]
    base = carregar_base(nivel)

    # Calcular as participações no total do Brasil
    top = base.nlargest(n, "pib").copy()
    top["p_pib"] = top["pib"] / base["pib"].sum() * 100
    top["p_pop"] = top["populacao"] / base["populacao"].sum() * 100
    top["acum"] = top["p_pib"].cumsum()

    # Montar as linhas (municípios mostram a UF)
    linhas = ""
    for pos, (_, r) in enumerate(top.iterrows(), start=1):
        nome = html.escape(str(r[cfg["nome"]]))
        if nivel == "Município":
            nome += f" ({html.escape(str(r['uf_sigla']))})"
        linhas += (
            f'<div class="lin"><span class="pos">{pos}</span>'
            f'<span class="n">{nome}</span>'
            f'<span class="v dest">{_pct(r["p_pib"])}</span>'
            f'<span class="v">{_pct(r["acum"])}</span>'
            f'<span class="v">{_pct(r["p_pop"])}</span></div>'
        )

    ultimo = top.iloc[-1]
    corpo = (
        f'<div class="texto">Top {n} {ROTULOS[nivel]} por PIB, em % do total do Brasil.</div>'
        '<div class="rk"><div class="cab"><span>#</span><span></span>'
        '<span class="v">PIB</span><span class="v">ACUM.</span>'
        f'<span class="v">POP.</span></div>{linhas}'
        f'<div class="nota">Os {n} maiores somam {_pct(ultimo["acum"])} do PIB '
        f'e {_pct(top["p_pop"].sum())} da população.</div></div>'
    )
    mostrar_cartao("Maiores PIBs", corpo, CSS_RANK)
