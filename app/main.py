"""Entrada do app: define a navegação entre as páginas."""
import streamlit as st

# Configurar a página (somente aqui, na entrada)
st.set_page_config(page_title="Composição do PIB brasileiro - 2021", layout="wide")

# Listar as páginas do app, na ordem do roteiro
paginas = [
    st.Page("paginas/explorar.py", title="Explorar",
            icon=":material/map:", default=True),
    st.Page("paginas/concentracao.py", title="Concentração",
            icon=":material/leaderboard:"),
    st.Page("paginas/dependencia.py", title="Dependência",
            icon=":material/account_balance:"),
    st.Page("paginas/estrutura.py", title="Estrutura produtiva",
            icon=":material/factory:"),
    st.Page("paginas/metodologia.py", title="Metodologia",
            icon=":material/menu_book:"),
]

# Exibir o título na sidebar e o menu no topo
st.sidebar.title("Composição do PIB brasileiro")
st.sidebar.caption("Dados de 2021 · IBGE")
navegacao = st.navigation(paginas, position="top")

# Executar a página escolhida
navegacao.run()
