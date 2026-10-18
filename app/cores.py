"""Paleta do painel: fonte única das cores de gráficos e mapas."""

# Destaques
OURO = "#D4AF37"        # PIB, valor, números e linha de destaque
AZUL_CLARO = "#7FB2E5"  # população e território

# Setores (mesma cor em todas as páginas)
COR_SETOR = {
    "vab_servicos": "#F4A261",
    "vab_industria": "#4682B4",
    "vab_adm_publica": "#8E44AD",
    "vab_agro": "#2E8B57",
}

# Regiões (roxo reservado à adm. pública)
COR_REGIAO = {
    "Norte": "#2E8B57", "Nordeste": "#F4A261", "Centro-Oeste": OURO,
    "Sudeste": "#4682B4", "Sul": "#E06C9F",
}

# Rampa roxa da adm. pública (do escuro ao claro) e cores por porte
RAMPA_ROXO = ["#2b2438", "#4a3a6e", "#6a4a9c", "#8E44AD", "#C792EA"]
PORTE_ROXO = ["#C792EA", "#8E44AD", "#4a3a6e"]

# Escala do QL (azul abaixo de 1, neutro em 1, ouro acima)
QL_ABAIXO = "#2b5d8a"
QL_NEUTRO = "#232834"

# Textos
TEXTO = "#f1f3f5"         # títulos e valores
TEXTO_CORPO = "#dfe2e6"   # parágrafos do cartão
TEXTO_SUAVE = "#c9cdd2"   # rótulos e eixos
TEXTO_FRACO = "#9aa0a6"   # notas e fontes
TEXTO_ESCURO = "#14161b"  # texto sobre cor clara
AVISO = "#f0c36d"         # avisos do cartão

# Fundos e linhas
FUNDO = "#0e1117"         # fundo da página e dos mapas
CARTAO = "#1b1d22"        # fundo dos cartões
BORDA = "#2c2f36"         # separadores dos cartões
GRADE = "#262a33"         # grade dos gráficos
CINZA_LINHA = "#6b7280"   # referências (diagonal, medianas)
CINZA_RESTO = "#6b7a8f"   # territórios fora do destaque
SILHUETA = "#171b22"      # silhueta do país
DIVISA_SUAVE = "#3a3f4b"  # divisas nos mapas de bolhas