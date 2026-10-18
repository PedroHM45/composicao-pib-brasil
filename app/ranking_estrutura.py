"""Cartão de ranking de especialização setorial."""
import html

from componentes import br, mostrar_cartao
from dados import NIVEIS, carregar_base
from graficos_estrutura import NOMES
from ranking import CSS_RANK
from ranking_dependencia import CSS_EXTRA, PISO_POP


def mostrar_ranking_estrutura(nivel, setor, n=10):
    """Exibir os territórios em que o setor mais pesa na economia."""
    cfg = NIVEIS[nivel]
    col = "part_" + setor
    df = carregar_base(nivel)
    df = df[df[col].notna()]

    # Aplicar o piso de população nos municípios
    if nivel == "Município":
        df = df[df["populacao"] >= PISO_POP]
        nota = f"Municípios com pelo menos {br(PISO_POP, 0)} habitantes."
    else:
        nota = "Todos os estados, incluindo o DF."
    nota += " PIB/hab. em R$ mil."

    # Montar as linhas do ranking
    linhas = ""
    for pos, (_, r) in enumerate(df.nlargest(n, col).iterrows(), start=1):
        nome = html.escape(str(r[cfg["nome"]]))
        linhas += (
            f'<div class="lin"><span class="pos">{pos}</span>'
            f'<span class="n" title="{nome}">{nome}</span>'
            f'<span class="v dest">{br(r[col], 1)}%</span>'
            f'<span class="v">{br(r["pib_per_capita"] / 1000, 1)}</span></div>'
        )

    corpo = (
        f'<div class="texto">Maior peso de {NOMES[setor].lower()} na economia.</div>'
        '<div class="rk dep"><div class="cab"><span>#</span><span></span>'
        '<span class="v">PESO</span><span class="v">PIB/HAB.</span></div>'
        f'{linhas}<div class="nota">{nota}</div></div>'
    )
    mostrar_cartao("Maior peso", corpo, CSS_RANK + CSS_EXTRA)
