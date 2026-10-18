"""Cartão de ranking de dependência da administração pública."""
import html

from componentes import br, mostrar_cartao
from dados import NIVEIS, carregar_base
from ranking import CSS_RANK

COL = "part_vab_adm_publica"
PISO_POP = 10_000   # população mínima no ranking de municípios

# Ajustar as colunas e permitir que o nome quebre em duas linhas
CSS_EXTRA = """
<style>
.card .rk.dep .cab,.card .rk.dep .lin{
  grid-template-columns:22px 1fr 52px 64px;align-items:center}
.card .rk.dep .lin{height:auto;min-height:0}
.card .rk.dep .n{
  font-size:.9rem;line-height:1.2;white-space:normal;
  overflow:visible;text-overflow:clip}
</style>
"""


def mostrar_ranking_dependencia(nivel, n=10):
    """Exibir os territórios em que a adm. pública mais pesa na economia."""
    cfg = NIVEIS[nivel]
    df = carregar_base(nivel)
    df = df[df[COL].notna()]

    # Aplicar o piso de população nos municípios
    if nivel == "Município":
        df = df[df["populacao"] >= PISO_POP]
        nota = f"Municípios com pelo menos {br(PISO_POP, 0)} habitantes."
    else:
        nota = "Todos os estados, incluindo o DF."
    nota += " PIB/hab. em R$ mil."

    # Montar as linhas (o nome do município já traz a UF)
    linhas = ""
    for pos, (_, r) in enumerate(df.nlargest(n, COL).iterrows(), start=1):
        nome = html.escape(str(r[cfg["nome"]]))
        linhas += (
            f'<div class="lin"><span class="pos">{pos}</span>'
            f'<span class="n" title="{nome}">{nome}</span>'
            f'<span class="v dest">{br(r[COL], 1)}%</span>'
            f'<span class="v">{br(r["pib_per_capita"] / 1000, 1)}</span></div>'
        )

    corpo = (
        '<div class="texto">Maior peso da adm. pública na economia.</div>'
        '<div class="rk dep"><div class="cab"><span>#</span><span></span>'
        '<span class="v">PESO</span><span class="v">PIB/HAB.</span></div>'
        f'{linhas}<div class="nota">{nota}</div></div>'
    )
    mostrar_cartao("Maior dependência", corpo, CSS_RANK + CSS_EXTRA)
