"""Funções de coleta de dados do SIDRA."""
import logging

import pandas as pd
import sidrapy

from src.config import ANO_REF

logger = logging.getLogger(__name__)

# Definir tabela e variáveis do PIB
TABELA = "5938"
VARIAVEIS = {
    "37": "pib",
    "498": "vab_total",
    "513": "vab_agro",
    "517": "vab_industria",
    "6575": "vab_servicos",
    "525": "vab_adm_publica",
    "543": "impostos",
}

# Definir tabela e variável de população
TABELA_POP = "6579"
VAR_POP = "9324"

# Definir níveis territoriais do SIDRA
NIVEL_REGIAO = "2"
NIVEL_UF = "3"
NIVEL_MUNICIPIO = "6"

# Definir o tamanho esperado do código de cada nível
TAMANHO_CODIGO = {NIVEL_REGIAO: 1, NIVEL_UF: 2, NIVEL_MUNICIPIO: 7}

# Definir símbolos do SIDRA: zero absoluto e valores indisponíveis
SIMBOLO_ZERO = "-"
SIMBOLOS_AUSENTES = ["..", "...", "X"]


def _consultar(tabela, nivel, variaveis, periodo):
    """Consultar o SIDRA e devolver os dados sem a linha de cabeçalho."""
    bruto = sidrapy.get_table(
        table_code=tabela,
        territorial_level=nivel,
        ibge_territorial_code="all",
        variable=variaveis,
        period=periodo,
    )

    # Remover linha de cabeçalho descritivo
    return bruto.iloc[1:].copy()


def _validar_codigos(codigos, nivel):
    """Conferir se os códigos têm o tamanho esperado para o nível."""
    esperado = TAMANHO_CODIGO[nivel]
    if not (codigos.str.len() == esperado).all():
        raise ValueError(f"Códigos fora do formato esperado para o nível {nivel}")


def _converter(valores):
    """Converter valores do SIDRA em números, tratando os símbolos."""
    # Trocar símbolos de indisponível por vazio e o zero absoluto por "0"
    v = valores.where(~valores.isin(SIMBOLOS_AUSENTES)).replace(SIMBOLO_ZERO, "0")

    # Converter em número (texto inesperado gera erro)
    return pd.to_numeric(v)


def _alertar_ausentes(serie):
    """Avisar quantos valores estão ausentes."""
    ausentes = serie.isna().sum()
    if ausentes:
        logger.warning("Atenção: %d valores ausentes", ausentes)


def baixar_pib(nivel, periodo=ANO_REF):
    """Baixar PIB e componentes em formato largo."""
    # Consultar o SIDRA
    df = _consultar(TABELA, nivel, ",".join(VARIAVEIS), periodo)

    # Selecionar e renomear colunas
    df = df[["D1C", "D1N", "D2C", "D3C", "V"]]
    df.columns = ["cod", "nome", "ano", "var_cod", "valor"]

    # Conferir o formato dos códigos
    _validar_codigos(df["cod"], nivel)

    # Converter valores e alertar ausentes
    df["valor"] = _converter(df["valor"])
    _alertar_ausentes(df["valor"])

    # Nomear variáveis a partir do código
    df["variavel"] = df["var_cod"].map(VARIAVEIS)
    if df["variavel"].isna().any():
        raise ValueError("O SIDRA devolveu uma variável desconhecida")

    # Pivotar: uma linha por território, uma coluna por variável
    largo = df.pivot(
        index=["cod", "nome", "ano"], columns="variavel", values="valor"
    ).reset_index()
    largo.columns.name = None
    return largo


def baixar_populacao(nivel, periodo=ANO_REF):
    """Baixar população residente estimada."""
    # Consultar o SIDRA
    df = _consultar(TABELA_POP, nivel, VAR_POP, periodo)

    # Selecionar e renomear colunas
    df = df[["D1C", "V"]]
    df.columns = ["cod", "populacao"]

    # Conferir o formato dos códigos
    _validar_codigos(df["cod"], nivel)

    # Converter valores e alertar ausentes
    df["populacao"] = _converter(df["populacao"])
    _alertar_ausentes(df["populacao"])

    return df.reset_index(drop=True)