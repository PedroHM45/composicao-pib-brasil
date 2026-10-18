"""Peças reutilizáveis das páginas."""
import streamlit as st

from cores import (
    AVISO, BORDA, CARTAO, OURO, TEXTO, TEXTO_CORPO, TEXTO_FRACO, TEXTO_SUAVE,
)
from mapa import ALTURA

# Definir a tese central do projeto (HTML simples)
TESE = (
    "<b>O Brasil é um país de economia desigual.</b> A riqueza se concentra em "
    "poucos centros urbanos de serviços, enquanto um terço dos municípios "
    "depende da administração pública, a indústria está em poucos lugares e "
    "o agro ocupa boa parte do interior."
)

# Definir as perguntas que surgem dos dados (uma por ato)
TITULO_PERGUNTAS = "DOS DADOS COLETADOS SURGEM ESTAS PERGUNTAS"
PERGUNTAS = [
    "Quão concentrada é a riqueza no território?",
    "Quem depende da administração pública?",
    "Como se distribuem serviços, indústria e agro?",
]

# Definir o estilo comum dos cartões
ALTURA_CARD = ALTURA        # igualar à altura do mapa

# Definir as variáveis de cor (usadas como var(--nome) em todos os cartões)
CSS_CARD = """
<style>
.card{--ouro:__OURO__;--texto-suave:__SUAVE__;--texto-fraco:__FRACO__;
--borda:__BORDA__;--aviso:__AVISO__;
background:__CARTAO__;color:__TEXTO__;border-radius:16px;
padding:20px 22px;height:__ALTURA__px;box-sizing:border-box;overflow:auto}
.card .nome{font-size:1.5rem;font-weight:700;margin-bottom:6px}
.card .texto{font-size:1rem;line-height:1.55;color:__CORPO__;margin-top:14px}
.card .sec{font-weight:700;letter-spacing:.12em;font-size:.75rem;
color:var(--texto-suave);margin:18px 0 8px}
.card ul,.card ol{margin:0;padding-left:18px}
.card li{margin:5px 0;line-height:1.45}
</style>
"""
SUBSTITUICOES = {
    "__ALTURA__": str(ALTURA_CARD), "__OURO__": OURO, "__SUAVE__": TEXTO_SUAVE,
    "__FRACO__": TEXTO_FRACO, "__BORDA__": BORDA, "__AVISO__": AVISO,
    "__CARTAO__": CARTAO, "__TEXTO__": TEXTO, "__CORPO__": TEXTO_CORPO,
}
for chave, valor in SUBSTITUICOES.items():
    CSS_CARD = CSS_CARD.replace(chave, valor)


def br(valor, casas=1):
    """Formatar número no padrão brasileiro (vírgula decimal, ponto de milhar)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def cabecalho(titulo, pergunta):
    """Exibir o título da página e a pergunta que ela responde."""
    st.title(titulo)
    st.caption(f"Pergunta: {pergunta}")


def mostrar_cartao(titulo, corpo, css_extra=""):
    """Exibir um cartão (estilo, título e corpo em um só elemento)."""
    st.markdown(
        CSS_CARD + css_extra
        + f'<div class="card"><div class="nome">{titulo}</div>{corpo}</div>',
        unsafe_allow_html=True,
    )


def mostrar_tese():
    """Exibir a tese e as perguntas do projeto em um cartão."""
    perguntas = "".join(f"<li>{p}</li>" for p in PERGUNTAS)
    corpo = (
        f'<div class="texto">{TESE}</div>'
        f'<div class="sec">{TITULO_PERGUNTAS}</div>'
        f"<ol>{perguntas}</ol>"
    )
    mostrar_cartao("A tese", corpo)